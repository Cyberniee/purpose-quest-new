import logging, os
from .chatgpt_messaging import perform_stt, perform_tts
from app.utils.common_utils import async_exception_handler, generate_filename, convert_media
from app.modules.services.whatsapp.whatsapp_utils import get_media_url, download_media
from app.config.general_config import MediaDirSettings

logger = logging.getLogger(__name__)


@async_exception_handler
async def transcribe_audio(audio_id: str, message_id: str, mime_type: str = None, user_data: dict = None):
    media_url = await get_media_url(media_id=audio_id)
    if not media_url:
        logger.error("Failed to get media URL for media ID: %s", audio_id)
        return {'status': 'error'}

    logger.info(f"media_url: {media_url}")

    # Download as OGG
    ogg_in_filename = generate_filename(message_id=message_id, audio_id=audio_id, extension=mime_type.split('/')[1].split(';')[0])
    ogg_in_file_path = os.path.join(MediaDirSettings.incoming_ogg_dir, ogg_in_filename)

    download_status = await download_media(url=media_url, file_path=ogg_in_file_path)
    if download_status['status'] != "success":
        return {'status': 'error'}

    conversion_result = await convert_media(file_path=ogg_in_file_path, target_format="mp3", output_dir=MediaDirSettings.incoming_mp3_dir)
    if conversion_result['status'] != "success":
        return {'status': 'error'}
    mp3_in_file_path = conversion_result['file_path']

    # Perform speech-to-text
    transcribed_message_resp = await perform_stt(mp3_in_file_path, user_data['users']['subscriptions'][0]['subscription'] == 'free')
    if transcribed_message_resp['status'] == "error":
        return {'status': 'error'}
    
    logger.info(f"transcribed message: {transcribed_message_resp['data'][:50]}, length: {transcribed_message_resp['duration']}")
    
    return {
        'status': transcribed_message_resp['status'],
        'data': transcribed_message_resp['data'],
        'ogg_in_file_path': ogg_in_file_path,
        'mp3_in_file_path': mp3_in_file_path,
        'duration': transcribed_message_resp['duration']
    }


@async_exception_handler
async def generate_audio_response(reply_message_gpt:str, message_id:str, audio_id:str):
    mp3_out_filename = generate_filename(message_id=message_id, audio_id=f"{audio_id}_reply", extension="mp3")
    mp3_out_file_path = os.path.join(MediaDirSettings.outgoing_mp3_dir, mp3_out_filename)

    tts_status = await perform_tts(text=reply_message_gpt, speech_file_path=mp3_out_file_path)  # Assuming perform_tts creates mp3 in OUTGOING_MP3_DIR
    if tts_status['status'] != "success":
        return {'status': 'error'}

    mp3_conv_status = await convert_media(mp3_out_file_path, "ogg", MediaDirSettings.outgoing_ogg_dir)
    if mp3_conv_status['status'] != 'success':
        return {'status': 'error'}
    
    return {'status': 'success', 'ogg_out_file_path': mp3_conv_status['file_path'], 'mp3_out_file_path': mp3_out_file_path}
