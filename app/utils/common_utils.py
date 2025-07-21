import functools, logging, os, tiktoken
from functools import wraps
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from termcolor import colored  # for colored output
from pydub import AudioSegment
from datetime import datetime, timedelta, timezone, date
from app.config.general_config import MediaDirSettings
from app.config.general_config import WaVariables
from datetime import datetime, timedelta, timezone



logger = logging.getLogger(__name__)

def api_response(data=None, status="ok", message=None, code=200):
    return JSONResponse(status_code=code, content={
        "status": status,
        "data": data,
        "message": message
    })

def get_wa_headers():
    token = WaVariables.access_token_wa
    if not isinstance(token, str):
        raise ValueError("WA_ACCESS_TOKEN must be set and must be a string")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_wa_ul_headers():
    return {
        "Authorization": f"Bearer {WaVariables.access_token_wa}"
    }

# Not in use at the moment, but could be useful in the future.
'''def determine_message_type(last_msg=None):
        if not last_msg:
            return 'template'
        try:
            # Parse ISO format
            last_message_time = datetime.strptime(last_msg, '%Y-%m-%dT%H:%M:%SZ')
            if (datetime.now(UTC) - last_message_time).total_seconds() < (23 * 3600 + 59 * 60): #we are comparing the logged time stamp (logged in UTC+0) to the UTC+0 time now. Comparing +0 to +0
                return 'text'
            else:
                return 'template'
        except Exception as e:
            logging.error(f"Error parsing last_message_time_str: {last_msg}, error: {e}")
            return 'template'''

def async_exception_handler(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f'Error in {func.__name__}: {e}')
            return {"status": "error", "message": str(e)}
    return wrapper

def validate_data_presence(data):
    return data is not None and 'message' not in data and len(data.data) > 0

def detailed_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Gather information
            route_name = func.__name__
            arg_details = f"Args: {args}"
            kwarg_details = f"Kwargs: {kwargs}"
            exception_message = f"Exception: {str(e)}"
            
            # Log in a formatted manner
            logging.error(colored("\n--- ERROR OCCURRED ---", "red", attrs=["bold"]))
            logging.error(colored(f"Route: {route_name}", "yellow", attrs=["bold"]))
            logging.error(colored(f"Function Name: {func.__name__}", "yellow"))
            logging.error(colored(f"{arg_details}", "cyan"))
            logging.error(colored(f"{kwarg_details}", "cyan"))
            logging.error(colored(f"{exception_message}", "red", attrs=["bold"]))
            logging.error(colored("--- END ERROR ---\n", "red", attrs=["bold"]))
            
            # Raise an HTTPException with the error detail
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred in '{route_name}': {str(e)}"
            )
    return wrapper

def calc_tokens(prompt:str):
    if not isinstance(prompt, str):
        logger.error(f"Invalid type for prompt: expected str, got {type(prompt)}")
        return 0
    # Select the appropriate tokenizer based on the model name
    model_name = "gpt-4o"
    tokenizer = tiktoken.get_encoding("o200k_base" if model_name == "gpt-4o" else "o200k_base")

    # Encode the prompt using the selected tokenizer
    token_count = len(tokenizer.encode(prompt))

    return token_count

def get_user_local_date(tz_offset_minutes: int):
    # Current UTC time
    utc_now = datetime.now()

    # Create a timezone offset
    user_timezone = timezone(timedelta(minutes=tz_offset_minutes))

    # Apply the offset
    user_local_datetime = utc_now.replace(tzinfo=timezone.utc).astimezone(user_timezone)

    # Return the date part
    return user_local_datetime.date()


async def extract_webhook_details(session):
    try:
        customer_phone = session.get('customer_details', {}).get('phone', None)
        country_hint = session.get('customer_details', {}).get('address',{}).get("country", None)
        stripe_customer_id = session.get('customer')
        customer_name = session.get('customer_details', {}).get('name', None)
        customer_email = session.get('customer_details', {}).get('email', None)
        subscription_id = session.get('subscription', None)
        subscription_type = session.get('metadata', {}).get('version', None)
        return customer_phone, country_hint, stripe_customer_id, customer_name, customer_email, subscription_id, subscription_type
    except Exception as e:
        logger.error(f"something went wrong loading the vars {e}")

def format_entry_label(date_str: str) -> str:
    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = date.today() # takes server date, not user date
    delta = (today - entry_date).days

    if delta == 0:
        return "Today’s Entry"
    elif delta == 1:
        return "Yesterday’s Entry"
    else:
        return f"{delta} days ago"


def generate_filename(message_id: str, audio_id: str, extension: str) -> str:
    filename = f"{message_id}_{audio_id}.{extension}"
    return filename


@async_exception_handler
async def convert_media(file_path: str, target_format: str = 'mp3', output_dir: str = '.') -> dict:
    logger.info('converting media...')
    try:
        # Determine new file path
        base_name = os.path.basename(file_path)
        new_file_name = '.'.join(base_name.split('.')[:-1] + [target_format])
        new_file_path = os.path.join(output_dir, new_file_name)

        # Perform conversion based on file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        audio = None

        if file_extension in ['.wav', '.wave']:
            audio = AudioSegment.from_wav(file_path)
        elif file_extension == '.ogg':
            audio = AudioSegment.from_ogg(file_path)
        elif file_extension == '.flac':
            audio = AudioSegment.from_file(file_path, format='flac')
        elif file_extension == '.aac':
            audio = AudioSegment.from_file(file_path, format='aac')
        elif file_extension in ['.mp3', '.m4a', '.mp4', '.wma']:
            audio = AudioSegment.from_file(file_path)
        else:
            return {"status": "error", "message": f"Unsupported file format: {file_extension}"}

        # Explicitly manage file output
        with open(new_file_path, 'wb') as f:
            audio.export(f, format=target_format)
            f.close()
            
        logger.info(f"File converted successfully to {target_format}. and stored in {new_file_path}")
        return {"status": "success", "message": f"File converted successfully to {target_format}.", "file_path": new_file_path}
    except Exception as e:
        logger.error(f"error converting media to {target_format}; error: {e}")
        return {"status": "error", "message": str(e)}
    

# This method ensures that all specified directories exist
def create_dirs():
    os.makedirs(MediaDirSettings.incoming_ogg_dir, exist_ok=True)
    os.makedirs(MediaDirSettings.incoming_mp3_dir, exist_ok=True)
    os.makedirs(MediaDirSettings.outgoing_mp3_dir, exist_ok=True)
    os.makedirs(MediaDirSettings.outgoing_ogg_dir, exist_ok=True)

