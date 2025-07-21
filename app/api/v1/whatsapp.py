import logging
from app.config.general_config import WaVariables

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from app.modules.services.whatsapp.whatsapp_utils import handle_status_update
from app.modules.services.whatsapp.whatsapp_services import handle_new_message

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get('hub.mode')
    token = params.get('hub.verify_token')
    challenge = params.get('hub.challenge')

    if mode and token and mode == 'subscribe' and token == WaVariables.verification_token:
        return PlainTextResponse(content=challenge)
    return PlainTextResponse(content="Verification failed", status_code=403)

@router.post("/whatsapp")
async def handle_message(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    # logging.info(f"Data received (raw): {data}")

    try:
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']

        if 'messages' in value:
            background_tasks.add_task(handle_new_message, message_data=value['messages'][0])

        elif 'statuses' in value:
            logger.info(f"status message contains: (raw) {data}")
            background_tasks.add_task(handle_status_update, value['statuses'][0])
        else:
            logger.warning("No 'messages' or 'statuses' key in the data")

    except Exception as e:
        logger.debug(f"Error processing incoming data: {e}")
        return {"error": "Error"}, 500

    return {"message": "Data processing in background"}

