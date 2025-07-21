from . import user_settings, logger, validate_data_presence, async_exception_handler


@async_exception_handler
async def update_user_settings(data:dict, user_id:str):
    try:
        resp = user_settings.update(data).eq("user_id", user_id).execute()
    except Exception as e:
        logger.error(f"Error updating user settings for user {user_id}: {e}")
        return False

    if not validate_data_presence(resp):
        logger.error(f"Failed to update user data: {data} for user: {user_id}")
        return False
    else:
        return True