from . import prompts, logger, async_exception_handler, validate_data_presence

@async_exception_handler
async def get_prompt(command:str):
    resp = prompts.select('prompt').eq('command', command).execute()
    if validate_data_presence(resp):
        return resp.data[0]['prompt'] #returns the text value
    else:
        logger.error(f"no rewrite command prompt has been found")
        return None