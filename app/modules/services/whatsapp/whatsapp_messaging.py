#whatsapp.py
import random, json, asyncio
import aiohttp, logging
from app.config.general_config import WaVariables
from app.utils.common_utils import get_wa_headers

logger = logging.getLogger(__name__)


# DEV CHANGED >> TEST ELABORATELY!!!

async def send_whatsapp_message(to_number: str, message: str, qr_buttons: list = None):
    try: 
        if not to_number or not message:
            logger.error(f"message or number were not provided in the right format: {message}, {to_number}")
            return None

        url = WaVariables.url_wa
        headers = get_wa_headers()

        if qr_buttons:
            buttons = []
            for button in qr_buttons:
                if "url" in button:
                    buttons.append({
                        "type": "button",
                        "sub_type": "url",
                        "url": button["url"],
                        "title": button["title"]
                    })
                else:
                    buttons.append({
                        "type": "reply",
                        "reply": {
                            "id": button['id'],
                            "title": button['title']
                        }
                    })

            data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "interactive",
                "recipient_type": "individual",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message
                    },
                    "action": {
                        "buttons": buttons
                    }
                }
            }
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            logger.error(f"Failed to send message: response status = {response.status}, response = {response}")
                            return None
            except aiohttp.ClientConnectorError as e:
                logger.error(f"Connection Error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    backoff_time = 2 ** attempt
                    await asyncio.sleep(backoff_time)
                else:
                    logger.error("Max retries reached. Giving up.")
                    return None
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return None

async def send_template_message(to_number: str, template_name: str, link_vars=[], text_vars=[], lang_code="en"):
    # logger.info(f"Trying to send template message: {to_number}, {template_name}, tv: {text_vars}, lv: {link_vars}")
    if not to_number or not template_name:
        logger.error(f"Template or number were not provided in the right format: {template_name}, {to_number}")
        return None
    template_name_new = None

    if template_name.startswith('morning_nudge_') or template_name.startswith('checkin_'):
        template_name_new = f"{template_name}{random.randint(1, 3)}"
    else:
        template_name_new = template_name

    url = WaVariables.url_wa
    headers = get_wa_headers()
    components = [{
        "type": "body",
        "parameters": [{"type": "text", "text": var} for var in text_vars]
    }] if text_vars else []

    if link_vars:
        # Starting index for buttons, after the text variables
        button_index = len(text_vars)

        # Add a button component for each link variable
        for var in link_vars:
            components.append({
                "type": "button",
                "sub_type": "url",
                "index": button_index,
                "parameters": [{"type": "text", "text": var}]
            })
            button_index += 1

    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name_new,
            "language": {
                "code": lang_code
            }
        }
    }
    logger.info(f"sending this package to facebook: {data}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    # logger.info(f"Status: {response.status}")
                    # logger.info(f"Content-type: {response.headers['content-type']}")
                    # logger.info(f"Content: {response}")
                    response_data = await response.json()

                    # Extract message_id from the response structure
                    message_id = response_data['messages'][0]['id'] if response_data.get('messages') else None
                    logger.info(f"message_id of template {template_name_new}: {message_id}")

                    # Return both the message_id and the template_name_new
                    return {"message_id": message_id, "template_name": template_name_new}
                else:
                    logger.error(f"Failed to send template message: {template_name_new} response status = {response.status}, response = {response}")
                    return None
    except aiohttp.ClientConnectorError as e:
        logger.error(f'Connection Error {str(e)}')


