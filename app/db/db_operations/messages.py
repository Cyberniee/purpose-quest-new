from . import messages, logger, async_exception_handler, validate_data_presence

async def update_msg_status(message_id: str, status: str, entry_id: str = None):
    """
    Try to update the status on an existing message. If no row was updated,
    fall back to inserting a minimal status‐only row (with defaults).
    """
    resp = await messages.update({
        "status": status,
        "entry_id":entry_id
    }).eq("wamid", message_id).execute()

    # if nothing was updated, insert a stub so we don't lose the status event
    if getattr(resp, "count", 0) == 0:
        await insert_msg_status(message_id, status)


async def insert_msg_status(message_id: str, status: str):
    """
    Inserts a minimal row so that an out‐of‐order status (or
    a status for a message we haven't seen yet) still gets recorded.
    We supply the bare minimum for NOT NULL columns:
      - message_type: default to 'text'
      - role:         default to 'inbound'
      - source:       will default in the DB to 'whatsapp'
    """
    await messages.insert({
        "wamid": message_id,
        "status": status,
        "message_type": "text",
        "role": "inbound"
    }).execute()


@async_exception_handler
async def insert_message(
    user_id: str,
    message_id: str,
    msg_content: str,
    incoming_tokens: int,
    role: str,
    status: str,
    msg_type: str,
    media_id: str = None,
    media_url: str = None,
    media_type: str = None,
    media_filename: str = None,
    source: str = None
):
    """
    Full insert of a WhatsApp message.
    Drops the old 'timestamp' field in favor of the DB default `created_at`.
    Adds optional media_url, media_type, media_filename.
    """
    try:
        payload = {
            "wamid": message_id,
            "user_id": user_id,
            "message_content": msg_content,
            "role": role,
            "message_type": msg_type,
            "tokens_used": incoming_tokens,
            "status": status,
        }
        # only include media fields if provided
        if media_id:
            payload["media_id"] = media_id
        if media_url:
            payload["media_url"] = media_url
        if media_type:
            payload["media_type"] = media_type
        if media_filename:
            payload["media_filename"] = media_filename
        # only override source if passed; otherwise rely on DB default
        if source:
            payload["source"] = source

        insert_msg_resp = await messages.insert(payload).execute()

        # check for errors (Supabase-style)
        if insert_msg_resp.get("error"):
            logger.error(f"Issue inserting message into DB: {insert_msg_resp}")
    except Exception as e:
        logger.error(f"Error inserting message into DB: {e}")


async def msg_is_processed(wamid: str):
    """
    Returns truthy if we've already stored a message with this WAMID.
    """
    resp = await messages.select("wamid").eq("wamid", wamid).execute()
    return validate_data_presence(resp)


@async_exception_handler
async def get_last_stt_msg(user_id: str):
    """
    Fetch the most recent 'audio' message_content for this user.
    Decrypts before returning.
    """
    resp = await messages\
        .select("message_content")\
        .eq("user_id", user_id)\
        .eq("message_type", "audio")\
        .order("id", desc=True)\
        .limit(1)\
        .execute()

    if validate_data_presence(resp):
        return resp.data[0]["message_content"]
    else:
        logger.info(f"No audio messages found for user {user_id}")
        return None


@async_exception_handler
async def get_context_msg(context_msg_id: str):
    """
    Fetch and decrypt the single message with this WAMID.
    """
    resp = await messages\
        .select("message_content")\
        .eq("wamid", context_msg_id)\
        .limit(1)\
        .execute()

    if validate_data_presence(resp):
        return resp.data[0]["message_content"]
    else:
        logger.info(f"No message found with WAMID {context_msg_id}")
        return None
