from . import whatsapp_link_tokens, logger, validate_data_presence, async_exception_handler

async def get_user_id_from_token(token: str):
    """
    Fetch the user ID associated with a given link token.
    """
    resp = whatsapp_link_tokens.select("*").eq("token", token).eq('valid', True).limit(1).execute()
    
    if validate_data_presence(resp):
        return resp.data[0]
    else:
        logger.info(f"No user found for token {token}")
        return None
    
@async_exception_handler
async def update_token_validity(now, token:str):
    resp = whatsapp_link_tokens.update({ "consumed_at": now }).eq("id", token).execute()
    if not validate_data_presence(resp):
        logger.error(f"Failed to update token validity for {token}")
        return False
    else:
        return True