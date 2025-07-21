# Define functions for each command
import logging, httpx, os
import pytz
from datetime import datetime, timedelta

from app.modules.services.whatsapp.whatsapp_messaging import send_whatsapp_message
from app.config.general_config import WaVariables
from app.utils.common_utils import async_exception_handler, get_wa_headers, get_wa_ul_headers
from app.db.db_operations.messages import msg_is_processed, insert_msg_status, update_msg_status, get_context_msg
from app.db.db_operations.wa_link_tokens import get_user_id_from_token, update_token_validity
from app.modules.services.users.user_services import link_wa_account_to_user
from app.utils.messaging_utils import wa_text_msg_handler

logger = logging.getLogger(__name__)

async def extract_message_details(message_data):
    logger.info(f"message_data: {message_data}")
    audio_id = None
    mime_type = None
    context_msg_id = None
    message_id = message_data['id']
    from_num = message_data['from']
    message_type = message_data['type']
    timestamp = message_data['timestamp']
    
    
    # Initialize content variable
    content = ''

    # Check if context is present and extract context_msg_id
    if 'context' in message_data:
        context_msg_id = message_data['context'].get('id')

    # Check the type of message and extract content accordingly
    if message_type == 'text':
        content = message_data.get('text', {}).get('body', '')
    elif message_type == 'button':
        content = message_data.get('button', {}).get('text', '')
    elif message_type == 'interactive':  # Handling 'interactive' type for button replies
        # Extracting the button reply content
        content = message_data.get('interactive', {}).get('button_reply', {}).get('title', '')
        message_type = 'button_reply'  # Adjusting the message_type to reflect the interaction
    elif message_type == 'audio':
        content = "audio file!"
        audio_id = message_data['audio']['id']
        mime_type = message_data['audio']['mime_type']
        # file_size = message_data['audio']['file_size']

    return message_id, from_num, content, message_type, timestamp, audio_id, mime_type, context_msg_id

# DEV: make sure to change the faq and contact URLS!
async def process_help_command():
    return "Here are some commands you can use:\n\n" \

async def process_reflect_command():
    return "Here are some commands you can use:\n\n" \


#Command Configuration
command_config = {
    '/help': {
        'function': process_help_command,
        'params': []
    },
    '/reflect': {
        'function': process_reflect_command,
        'params': ['user_data', 'context_msg_id', 'command']
    }
}


# Process Command
async def process_command(content_stripped, user_data, context_msg_id=None):
    if content_stripped in command_config:
        func = command_config[content_stripped]['function']
        params = command_config[content_stripped]['params']
        
        # Prepare arguments based on required parameters
        kwargs = {
            'user_data': user_data,
            'context_msg_id': context_msg_id,
            'command': content_stripped,
            'plan': 'basic' if content_stripped == 'choose basic' else 'ultimate' if content_stripped == 'choose ultimate' else None
        }

        # Filter the arguments to only include those required by the function
        filtered_kwargs = {key: kwargs[key] for key in params if key in kwargs and kwargs[key] is not None}
        
        # Call the function with the filtered arguments
        result = await func(**filtered_kwargs)
        return True, result
    
    return False, None


async def is_old_msg(timestamp, message_id):
    if await is_processed(message_id):
        logger.info(f"message has already been processed, returning.")
        return True
    
    timestamp = datetime.fromtimestamp(int(timestamp))
    current_time = datetime.now() #UTC+0
    if (current_time - timestamp) > timedelta(hours=10): #10 hours as arbitrary threshold
        return True
    return False


# Helper function to check if a message or status update has been processed
async def is_processed(wamid):
    processed = await msg_is_processed(wamid) # True or false

    return processed

async def handle_status_update(status_data):
    logger.info(f"status_data: {status_data}")
    status_id = status_data['id']
    status = status_data['status']

    # current code checks if the message already exists, which is does, because it is a status update
    # if it does not exist yet, it will be inserted. If it exists, it will update it.
    if await is_processed(status_id):
        # logger.info(f"updating message {status_data}")
        await update_msg_status(message_id=status_id, status=status)
    else:
        await insert_msg_status(message_id=status_id, status=status)
        logger.warning(f"inserting another empty haha... message: {status_data}")

async def get_media_url(media_id):
    headers = get_wa_headers()
    async with httpx.AsyncClient() as client:
        response = await client.get(WaVariables.wa_dl_url.format(media_id=media_id), headers=headers)
    response.raise_for_status()  # This will raise an exception for 4XX/5XX responses

    # Assuming the API returns a JSON response
    logger.info("Response JSON:", response.json())
    # Extract and print the media URL if it's available in the response
    media_url = response.json().get("url")
    if media_url:
        print("Media URL:", media_url)
        return media_url
    else:
        print("Media URL not found in the response.")

@async_exception_handler
async def link_new_phone_number(from_num: str, content: str):
    """
    Link a new phone number to a user if the provided token is valid.

    Args:
        from_num (str): The incoming WhatsApp phone number.
        content (str): The message body (should contain the token).
    """
    token_input = content.strip()
    now = datetime.now(pytz.timezone('utc'))

    # Step 1: Look up token
    token = await get_user_id_from_token(token=token_input)
    

    if not token:
        # await send_whatsapp_message(from_num, "❌ Invalid token. Please request a new link token from your dashboard.")
        await wa_text_msg_handler(from_num, "❌ Invalid token. Please request a new link token from your dashboard.", user_id=None)
        return


    if datetime.fromisoformat(token["expires_at"]) < now:
        await wa_text_msg_handler(from_num, "⏰ This token has expired. Please generate a new one in your dashboard.", user_id=None)
        return

    user_id = token["user_id"]

    # Step 3: Link phone number to user
    resp = await link_wa_account_to_user(from_num=from_num, user_id=user_id)

    if resp:
        # Step 4: Mark token as consumed
        await update_token_validity(now=now, token=token_input)

        # Step 5: Confirm to user
        await wa_text_msg_handler(from_num, "✅ Your number has been successfully linked to your account.", user_id=user_id)
    else:
        await wa_text_msg_handler(from_num, "❌ An error occured linking your phone number, please try again later.", user_id=user_id)




@async_exception_handler
async def download_media(url: str, file_path: str) -> dict:
    headers=get_wa_headers()
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    response.raise_for_status()  # Raises exception for 4XX/5XX responses

    mime_type = response.headers.get('Content-Type')
    logging.info(f"MIME Type: {mime_type}")

    # Save the binary content to a file
    with open(file_path, 'wb') as file:
        file.write(response.content)
    
    logging.info(f"Media saved to {file_path}")
    return {"status": "success", "message": "downloaded!"}


@async_exception_handler
async def upload_media_to_whatsapp(file_url: str, type=None) -> dict:
    url = f"{WaVariables.wa_ul_url}/media"  # Assuming you have this URL in your settings
    file_name = "DE_Wertetest_online.pdf"  # Extracts the file name from the URL
    logging.info(f"Uploading media to WhatsApp!: {url}, {file_url}")
    headers = get_wa_ul_headers()

    # Now upload the file to WhatsApp
    if type == "document":
        async with httpx.AsyncClient() as client:
            file_response = await client.get(file_url)
            file_response.raise_for_status()  # Ensure we got the file correctly
            file_content = file_response.content
            files = {
                'file': (file_name, file_content, 'application/pdf'),
                'type': (None, 'document'),
                'messaging_product': (None, 'whatsapp'),
            }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, files=files)
            if response.status_code == 200:
                logging.info(f"Response from WhatsApp upload: {response.json()}")
            json_resp = response.json()
            media_id=json_resp['id']
            return {"status": "success", "media_id": media_id}


    else:
        file_name = os.path.basename(file_url)  # Extracts the file name from the URL
        with open(file_url, 'rb') as file:
            files = {
                'file': (os.path.basename(file_url), file, 'audio/ogg'),
                'type': (None, 'audio'),
                'messaging_product': (None, 'whatsapp'),
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, files=files)

        if response.status_code == 200:
            logging.info(f"Response from WhatsApp upload: {response.json()}")
            json_resp = response.json()
            media_id=json_resp['id']
            return {"status": "success", "media_id": media_id}
        else:
            logging.error(f"Failed to upload media to WhatsApp, status code: {response.status_code}, detail: {response.text}")
            return {"status": "error", "detail": "Failed to upload media to WhatsApp"}

@async_exception_handler
async def cleanup_audio_files(ogg_in_file_path, mp3_in_file_path):
    files_to_delete = [ogg_in_file_path, mp3_in_file_path]
    logger.info(f"Attempting to clean up files: {files_to_delete}")

    for file_path in files_to_delete:
        try:
            # Ensure the file exists before trying to delete it
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Successfully deleted {file_path}")
            else:
                logger.warning(f"File not found, could not delete: {file_path}")
                return {'status': 'warning'}
        except Exception as e:
            logger.error(f"Failed to delete {file_path} due to: {e}")
            return {'status': 'error'}
    return {'status': 'success'}


