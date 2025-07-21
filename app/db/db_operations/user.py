from . import users, logger, validate_data_presence, async_exception_handler


@async_exception_handler
async def link_wa_to_user(from_num: str, user_id: str):
    
    resp = users.update({ "phone_number": from_num }).eq("id", user_id).execute()
    logger.info(f"Linking WhatsApp number {from_num} to user ID {user_id}, response: {resp}")

    if not validate_data_presence(resp):
        logger.error(f"Failed to link WhatsApp number {from_num} to user ID {user_id}")
        return False
    else:
        return True