from . import subs, logger, validate_data_presence, async_exception_handler

#insert operations
async def insert_sub_data(data:dict):
    subs.insert(data).execute()

#update operations
async def update_subscription(user_id:id, update_data:dict):
    try:
        resp = subs.update(update_data).eq('user_id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No subscription data found for user_id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching subscription data for user_id {user_id}: {e}")
        return None
        
async def update_sub_data(data:dict, user_id:int=None):
    try:
        resp = subs.update(data).eq('user_id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No subscription data found for user_id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching subscription data for user_id {user_id}: {e}")
        return None       
    
async def update_sub_data_sub_id(data:dict, sub_id:str):
    try:
        resp = subs.update(data).eq('sub_id', sub_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No subscription data found for sub_id {sub_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching subscription data for sub_id {sub_id}: {e}")
        return None       

async def update_token_data(new_monthly_total:int, new_total:int, new_daily_total:int, user_id:int):
    subs.update({'tokens_used_month': new_monthly_total, 'total_tokens_used': new_total, 'tokens_used_day': new_daily_total}).eq('user_id', user_id).execute()

async def update_subscription_settings(user_id:int, cleaned_data):
    try:
        resp = subs.update({'subscription': cleaned_data['subscription']}).eq('user_id', user_id). execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No subscription data found for sub_id, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching subscription data for sub_id: {e}")
        return None       

# fetch operations
async def get_sub_data_sub_id(sub_id:int):
    try:
        resp = subs.select('*').eq('sub_id', sub_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No sub data found for user_id {sub_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching sub data for user_id {sub_id}: {e}")
        return None
    
@async_exception_handler
async def get_consumption(user_id:int):
    resp = subs.select('*').eq('user_id', user_id).execute()
    if validate_data_presence(resp):
        logger.info(f'resp update consumption data: {resp}')
        return resp.data[0]
    else:
        logger.error(f"No usage data found for user_id {user_id}, {resp}")
        return None
    
@async_exception_handler
async def update_consumption_data(consumption_data:dict, user_id:int):
    resp = subs.update(consumption_data).eq('user_id', user_id).execute()
    
async def get_token_usage_data(user_id:int):
    try:
        resp = subs.select('token_usage', 'token_limit').eq('user_id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No token_use data found for user_id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching token use data for user_id {user_id}: {e}")
        return None
    
async def get_subscription_type(user_id:int):
    try:
        resp = subs.select('subscription').eq('user_id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No subscription data found for user_id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching subscription data for user_id {user_id}: {e}")
        return None
    
async def get_sub_trial_data_user_id(user_id:int):
    try:
        resp = subs.select('sub_id', 'trial', 'end_date', 'active', 'subscription').eq('user_id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No trial data found for user_id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error trial data for user_id {user_id}: {e}")
        return None
    
async def sub_active(user_id):
    try:
        sub_active = subs.select('active').eq('user_id', user_id).execute()
        if validate_data_presence(sub_active):
            return sub_active.data[0]['active']
        else:
            return False
    except Exception as e:
        logger.error(f"issue getting status of subscription")
        return False

async def get_active_subs():
    try:
        resp = subs.select('user_id').eq('active', True).execute()
        if validate_data_presence(resp):
            return resp.data
        else:
            logger.warning(f"No active subs found {resp}")
            return None
    except Exception as e:
        logger.error(f"issue getting status of subscription")

# utility operations
async def reset_token_counter(user_id:int):
    try:
        resp = subs.update({"token_usage": int(0)}).eq("user_id", user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No token reset data for user_id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"error in reset data for user_id {user_id}: {e}")
        return None
    
async def invalidate_sub(user_id:int):
    try:
        resp = subs.update({'active': False}).eq('user_id', user_id).execute()
        if validate_data_presence(resp):
            return {"status": "success"}
        else:
            logger.error(f"issue with invalidate_sub for user: {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error with invalidate_sub for user: {user_id}: {e}")
        return None