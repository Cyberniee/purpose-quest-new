# whatsapp_utils.py
import logging
from datetime import datetime
from app.modules.services.ai.chatgpt_utils import transcribe_audio
from app.modules.services.users.user_services import update_consumption, check_and_reset_usage
from app.modules.services.journal.journal_services import log_entry_from_whatsapp
from app.config.general_config import SubscriptionVariables
from app.utils.messaging_utils import wa_text_msg_handler
from app.db.db_operations.messages import update_msg_status, insert_message
from app.db.db_operations.whatsapp_accounts import get_user_from_number
from .whatsapp_utils import is_old_msg, process_command, extract_message_details, cleanup_audio_files
from .whatsapp_utils import link_new_phone_number

logger = logging.getLogger(__name__)

# messages that are not found in DB come in here, as they are likely new.
# DEV changed this one...
async def handle_new_message(message_data):
    logger.info(f"in handle new msg with: {message_data}")
    try:
        message_id, from_num, content, message_type, timestamp, audio_id, mime_type, context_msg_id = await extract_message_details(message_data)
        entry_id = None
        
        if await is_old_msg(message_id=message_id, timestamp=timestamp):
            logger.warning(f"Discarding old message from {from_num}.")
            return {'status': 'info', 'message': 'discarded old message'}

        # Validate message content
        if not content:
            logger.error(f"No content found in message {message_id}. Skipping - keep an eye out.")
            return {'status': 'warning', 'message': 'No content in message'}

        # User data retrieval and handling
        logger.info(f"Retrieving user data with number: {from_num}")
        user_data = await get_user_from_number(phone_number=from_num)
        logger.info(f"User data retrieved: {user_data}")

        if user_data and isinstance(user_data, dict):
            user_id = user_data.get('user_id')
            if not user_id:
                logger.error(f"User ID not found for phone: {from_num}") # check in the demo time if they actually reg correctly
                return {'status': 'warning', 'message': 'user_id not found from phone number'}

            else:
                msg_process_status, entry_id = await process_existing_user_message(
                    user_data=user_data, from_num=from_num, content=content, 
                    message_id=message_id, message_type=message_type, timestamp=timestamp, 
                    audio_id=audio_id, mime_type=mime_type, context_msg_id=context_msg_id #, file_size=file_size
                )
        else:
            try:
                await link_new_phone_number(from_num=from_num, content=content)
                return
            except Exception as e:
                logger.error(f"Error linking phone to user account: {e}")
            # create new user, give them the free plan, welcome them, give them an idea of what is possible and what not.

    except Exception as e:
        logger.error(f"Error in handle_new_message: {e}")
    finally:
        # Always update message status, regardless of previous errors
        status = "processed"
        await update_msg_status(message_id=message_id, status=status, entry_id=entry_id)


# we essentially want to reply to the same source as that we got the msg from.
async def process_existing_user_message(user_data: dict, from_num: str, content, message_id, message_type, timestamp, audio_id=None, mime_type=None, context_msg_id=None):
    logger.info(f"we enter the loop with content: {content}")
    try:
        user_id = user_data['user_id']
        timestamp = datetime.fromtimestamp(int(timestamp))

        # Initialize default values
        command = None
        error_occured = False
        reply_content = None
        duration = 0.00
        entry_id = None
        free = True if user_data['subscriptions'][0]['subscription'].lower() == 'free' or not user_data['subscriptions'][0]['active'] else False
        

        # here we will add the if audio_id bla bla, to get to the content part. If media in, we choose for media out.
        if audio_id:
            just_reset = await check_and_reset_usage(user_id) if free else False

            if user_data['subscriptions'][0]['message_count'] >= SubscriptionVariables.free_message_count and free and not just_reset:
                message = 'You\'ve reached the free limit for this month. If you want to upgrade and transcribe longer messages, upgrade your subscription in the Purpose Quest dashboard.'
                await wa_text_msg_handler(user_id=user_id, msg=message, from_num=from_num)
                return False, None
            
            message = "Transcribing and processing message... ✍️"
            await wa_text_msg_handler(user_id=user_id, msg=message, from_num=from_num)

            # gotta transcribe here.
            transcribe_response = await transcribe_audio(audio_id=audio_id, message_id=message_id, mime_type=mime_type, user_data=user_data)
            
            if transcribe_response['status'] == "error":
                content = 'something went wrong on our side, pelase make sure the file is <20mb, <20 minutes, and is an audio file (no video file). \n\nIf the issue persists, please contact info@voice-vault.com and we\'ll help you out.'
            
            if transcribe_response['status'] == 'limit':
                # limit is reached, notify user
                content = transcribe_response['data']
                
            if transcribe_response['status'] == 'success':
                # this content is taken out to be input as the user message, before its input "audio file!" which is a bit weird
                content = transcribe_response['data']
                duration = transcribe_response['duration']

            await update_consumption(duration=duration, user_id=user_id, free=free)
            # this is the input of the user
            content, ogg_in_file_path, mp3_in_file_path = transcribe_response['data'], transcribe_response['ogg_in_file_path'], transcribe_response['mp3_in_file_path']
            await cleanup_audio_files(ogg_in_file_path=ogg_in_file_path, mp3_in_file_path=mp3_in_file_path)

        else:
            content_stripped = content.strip().lower()
            # Commands can only be done via text messages
            command, reply_content = await process_command(content_stripped=content_stripped, user_data=user_data, context_msg_id=context_msg_id)
            if command:
                content = reply_content
                if reply_content == 'billing':
                    logging.info(f'processed billing command, and sent message. Returning')
                    return True, None
            
        if isinstance(content, list):
            # If the content is a list, send each chunk as a separate message
            for chunk in content:
                # here we want to make sure the chunks are added to the users entry for today. Appended or inserted.
                status = await log_entry_from_whatsapp(user_id=user_id, user_offset=user_data['user_settings'][0]['tz_offset'], content=chunk)
                if not status:
                    logger.error(f"Failed to log entry for user {user_id} with content: {chunk}")
                    error_occured = True
                    continue

        else:
            # If the content is not a list, we want to add the full content to the user entry for today.
            status, entry_id = await log_entry_from_whatsapp()
            if not status:
                logger.error(f"Failed to log entry for user {user_id} with content: {content}")
                error_occured = True
        
        if error_occured:
            message_content = "An error occurred while processing your message. Please try again later."

        else:
            message_content = "Your message has been processed successfully."

        # Send the processed message back to the user
        await wa_text_msg_handler(
            user_id=user_id, 
            msg=message_content, 
            from_num=from_num
        )

        return True, entry_id
            
                    
    except Exception as e:
        logger.error(f"error in process_existing_user_message: {e}")

    finally:
        # Insert incoming message with updated or default values
        await insert_message(user_id=user_id, message_id=message_id, msg_content=content, incoming_tokens = 0, role='user', status='received', msg_type=message_type, media_id=audio_id)