from . import whatsapp_accounts, logger, validate_data_presence, async_exception_handler

@async_exception_handler
async def get_user_from_number(phone_number: str):
    """
    Fetch the user ID associated with a given phone number.
    """
    resp = whatsapp_accounts.select("user_id, users(*, user_settings(tz_offset), subscriptions(*))").eq("phone_number", phone_number).limit(1).execute()
    
    if validate_data_presence(resp):
        return resp.data[0]
    else:
        logger.info(f"No user found for phone number {phone_number}")
        return None


