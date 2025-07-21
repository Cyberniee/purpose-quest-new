import logging
from app.modules.services.whatsapp.whatsapp_messaging import send_whatsapp_message
from app.db.db_operations.messages import insert_message

logger = logging.getLogger(__name__)

#sends text message and then logs to db
#why is there no nudge? DEV DEV!!!
async def wa_text_msg_handler(from_num: str, msg: str, user_id: str, tokens=0, qr_buttons=None):
    try:
        max_chars = 4096

        def split_message(message:str, limit:int):
            chunks = []
            while len(message) > limit:
                split_index = message.rfind(' ', 0, limit - 4)
                if split_index == -1:
                    split_index = limit - 4
                chunks.append(message[:split_index] + '...')
                message = message[split_index:].strip()
            chunks.append(message)
            return chunks

        message_chunks = split_message(msg, max_chars)

        for chunk in message_chunks:
            logger.info(f"Sending WhatsApp message to {from_num} {type(from_num)}: {chunk}, {type(chunk)}")
            json_resp_wam = await send_whatsapp_message(to_number=from_num, message=chunk, qr_buttons=qr_buttons)
            message_id = json_resp_wam.get('messages', [{}])[0].get('id', 'unknown')
            await insert_message(user_id=user_id, message_id=message_id, msg_content=chunk, incoming_tokens=tokens, msg_type="text", role="assistant", status="sent")

        return {"status": "success"}
    except Exception as e:
        logger.error(f"An error occurred while processing the message: {e}")
        return {"status": "error"}    
