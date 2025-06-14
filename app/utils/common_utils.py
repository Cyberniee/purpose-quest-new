import tiktoken
import functools, logging
from functools import wraps
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from termcolor import colored  # for colored output



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

def format_entry_label(date_str: str) -> str:
    from datetime import datetime, date, timedelta
    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = date.today()
    delta = (today - entry_date).days

    if delta == 0:
        return "Today’s Entry"
    elif delta == 1:
        return "Yesterday’s Entry"
    else:
        return f"{delta} days ago"
