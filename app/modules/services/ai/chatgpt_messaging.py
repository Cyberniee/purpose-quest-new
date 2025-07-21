import asyncio, logging, aiofiles
from app.config.openai_config import client
from aiohttp import ClientError

from .chatgpt_services import calc_tokens, is_over_token_limit, is_within_model_lim, update_token_usage
from app.config.general_config import OpenAISettings, SubscriptionVariables
from app.utils.common_utils import async_exception_handler
from app.db.db_operations.user import get_public_user_data
from pydub.utils import mediainfo


logger = logging.getLogger(__name__)

async def fetch_gpt_response(chat_messages, max_tokens, model):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=chat_messages,
            max_tokens=max_tokens,
            top_p=0.5,
            temperature=OpenAISettings.gpt_temperature,
            frequency_penalty=0.99,
            presence_penalty=0.91
        )
        gpt_response = response.choices[0].message.content
        incoming_tokens = calc_tokens(gpt_response)
        return gpt_response, incoming_tokens
    except ClientError as e:
        logger.error(f"Error communicating with OpenAI: {e}")
        raise

async def retry_api_call(api_call, chat_messages, max_tokens, max_retry, model):
    logger.info("in retry_api_call")
    try_count = 0
    base_delay = 1
    max_delay = 30
    while try_count < max_retry:
        try:
            return await api_call(chat_messages, max_tokens, model)
        except ClientError:
            delay = min(base_delay * (2 ** try_count), max_delay)
            logger.info(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            try_count += 1

    logger.error("Maximum retries reached, sending fallback message.")
    return "We're currently experiencing technical difficulties. Please try again later.", 0

# DEV DEV DEV!!!
#main function
async def send_message_to_chatgpt(message_content:dict, user_data:dict, subscription:str):
    user_id = user_data['id']
    chat_messages = message_content #str
    logger.info(f"chat messages: {chat_messages}")
    max_tok = OpenAISettings.chat_gpt_token_resp_lim

    # getting token stuff straight
    # over_token_lim, token_data, renewal = await is_over_token_limit(user_id)
    within_model_lim = await is_within_model_lim(chat_messages)
    # limit is set to max context window (16385) - max completion (4096) = 12xxx

    if not within_model_lim:
        return "This message is a little too big for me (limit exceeded)..."

    model = OpenAISettings.model

    gpt_response, incoming_tokens = await retry_api_call(
        api_call=fetch_gpt_response, 
        chat_messages=chat_messages, 
        max_tokens=max_tok, 
        max_retry=OpenAISettings.max_retries,
        model=model
    )

    logger.info(f"response chatgpt: {gpt_response}")
    # await update_token_usage(user_id, token_data, used_tokens, incoming_tokens)
    return gpt_response, incoming_tokens


@async_exception_handler
async def perform_stt(mp3_file_path, free:bool=False) -> dict:
    logger.info("in perform STT")
    duration = 0.00
    try:
        # Get the file length in seconds
        audio_info = mediainfo(mp3_file_path)
        logger.info(f'audio_info: {audio_info}')
        duration = float(audio_info.get('duration'))
        logger.info(f"Audio duration: {duration} seconds")
        
        if free and duration >= SubscriptionVariables.free_message_length_limit:
            duration = 0.00
            message = 'Message is longer than 60 seconds. Please upgrade to transcribe longer messages. \n\nType \'*/upgrade*\' to see your options.'
            return {"status": "limit", "data": message, "duration": duration}

        # Chunk size in bytes
        chunk_size = 5 * 1024 * 1024  # 5 MB

        # Use aiofiles to read the file in chunks and write to a combined file
        combined_file_path = "./tmp/combined_audio.mp3"
        async with aiofiles.open(mp3_file_path, "rb") as audio_file, aiofiles.open(combined_file_path, "wb") as combined_file:
            while True:
                chunk = await audio_file.read(chunk_size)
                if not chunk:
                    break
                await combined_file.write(chunk)

        # Use synchronous file handling for the OpenAI API
        with open(combined_file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text"
            )
            logger.info("transcription: [redacted]")  # this is text output, is all we need to use.

        return {"status": "success", "data": transcription, "duration": duration}
    except Exception as e:
        logger.error(f'error during STT: {e}')
        return {"status": "error", "message": str(e)}



# this function outputs an MP3 file, needs to be adjusted so that the file location is correct, the naming is correct, and it handles the text output from the perform_stt() function.
# language cannot be setup here for the tts
@async_exception_handler
async def perform_tts(text: str, speech_file_path: str):
    print("speech file path: ", speech_file_path, "text: ", text)
    response = await client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=text
    )
    logging.info(f"response_audio: {response}")

    response.write_to_file(speech_file_path)
    print("successfully turned gpt reply to mp3!")
    return {"status": "success", "file_path": speech_file_path}
