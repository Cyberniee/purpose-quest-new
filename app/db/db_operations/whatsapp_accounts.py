from . import whatsapp_accounts, user_settings, logger, validate_data_presence, async_exception_handler

@async_exception_handler
async def get_user_from_number(phone_number: str):
    """
    Fetch the user ID associated with a given phone number.
    """
    resp = whatsapp_accounts.select("user_id, users(*, user_settings(tz_offset), subscriptions(*))").eq("phone_number", phone_number).limit(1).execute()
    logger.info(f"Fetching user for phone number {phone_number}: {resp}")
    
    if validate_data_presence(resp):
        return resp.data[0]
    else:
        logger.info(f"No user found for phone number {phone_number}")
        return None



@async_exception_handler
async def link_wa_to_user(from_num: str, user_id: str):
    
    resp = whatsapp_accounts.insert({ "phone_number": from_num, "user_id": user_id }).execute()
    logger.info(f"Linking WhatsApp number {from_num} to user ID {user_id}, response: {resp}")

    if not validate_data_presence(resp):
        logger.error(f"Failed to link WhatsApp number {from_num} to user ID {user_id}")
        return False
    else:
        return True