from . import users, logger, validate_data_presence, async_exception_handler


async def get_all_user_data():
    try:
        resp = users.select('*').execute()
        if validate_data_presence(resp):
            return resp.data
        else:
            logger.warning(f"No user data found {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching any user data {e}")
        return None


async def get_user_data_id(user_id:int):
    try:
        resp = users.select('*').eq('id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No data found for user_id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user data for user_id {user_id}: {e}")
        return None

async def get_user_data_share_token(token_id:str):
    try:
        resp = users.select('*').eq('share_token', token_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No data found for token_id {token_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user data for token_id {token_id}: {e}")
        return None

    
async def get_user_data_supabase_id(sub:str):
    logger.info(f"getting userdata against this ID: {sub}")
    try:
        resp = users.select('*').eq('supabase_id', sub).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No data found for sub_id {sub}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user data for user_id {sub}: {e}")
        return None

@async_exception_handler
async def get_user_data_cus_id(stripe_cust_id: int):
    resp = users.select('*, convo(*)').eq('stripe_cust_id', stripe_cust_id).execute()
    if validate_data_presence(resp):
        return resp.data[0]
    else:
        logger.warning(f"No data found for stripe_cust_id {stripe_cust_id}, {resp}")
        return None
    
@async_exception_handler
async def get_user_data_phone(number: str):
        resp = users.select('*, subscriptions(active, subscription, limit, message_count)').eq('phone_number', number).execute()
        # logger.info(f'resp user data: {resp}')
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.warning(f"No data found for phone number {number}, {resp}")
            return None
  
async def get_user_data_stripeid(stripe_cust_id: str):
    try:
        resp = users.select('*').eq('stripe_cust_id', stripe_cust_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No data found for Stripe customer ID {stripe_cust_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user data for Stripe customer ID {stripe_cust_id}: {e}")
        return None

async def fetch_user_id_by_supabase_id(sub: str):
    try:
        resp = users.select('id').eq('supabase_id', sub).execute()
        if validate_data_presence(resp):
            return resp.data[0]['id'] if 'id' in resp.data[0] else None
        else:
            logger.info(f"No user id found for supabase id {sub}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID for supabase id {sub}: {e}")
        return None
    
async def fetch_stripe_id_by_user_id(user_id: str):
    try:
        resp = users.select('stripe_cust_id').eq('id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]['stripe_cust_id'] if 'stripe_cust_id' in resp.data[0] else None
        else:
            logger.info(f"No stripe_cust_id found for supabase id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching stripe_cust_id for supabase id {user_id}: {e}")
        return None
    
async def fetch_stripe_id_by_supabase_id(sub: str):
    try:
        resp = users.select('stripe_cust_id').eq('supabase_id', sub).execute()
        if validate_data_presence(resp):
            return resp.data[0]['stripe_cust_id'] if 'stripe_cust_id' in resp.data[0] else None
        else:
            logger.info(f"No stripe_cust_id found for supabase id {sub}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching stripe_cust_id for supabase id {sub}: {e}")
        return None
    
async def fetch_account_ids_by_sub(sub: str):
    try:
        resp = users.select('id', 'stripe_cust_id', 'phone_number').eq('supabase_id', sub).execute()
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.warning(f"No data found for sub ID {sub}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID for sub ID {sub}: {e}")
        return None


async def fetch_phone_by_supabase_id(sub: str):
    try:
        resp = users.select('phone_number').eq('supabase_id', sub).execute()
        if validate_data_presence(resp):
            return resp.data[0]['phone_number'] if 'phone_number' in resp.data[0] else None
        else:
            logger.info(f"No phone_number found for supabase id {sub}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching phone_number for supabase id {sub}: {e}")
        return None

async def fetch_phone_by_user_id(user_id: str):
    try:
        resp = users.select('phone_number').eq('id', user_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]['phone_number'] if 'phone_number' in resp.data[0] else None
        else:
            logger.info(f"No phone_number found for user id {user_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching phone_number for user id {user_id}: {e}")
        return None
    
async def fetch_user_id_by_phone(number: int):
    try:
        resp = users.select('id').eq('phone_number', number).execute()
        if validate_data_presence(resp):
            return resp.data[0]['id'] if 'id' in resp.data[0] else None
        else:
            logger.info(f"No user id found for phone number {number}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID for phone number {number}: {e}")
        return None
    
async def fetch_user_id_by_share_token(share_token:str):
    try:
        resp = users.select('id').eq('share_token', share_token).execute()
        if validate_data_presence(resp):
            return resp.data[0]['id'] if 'id' in resp.data[0] else None
        else:
            logger.error(f"No user id found for share_token {share_token}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID for share_token {share_token}: {e}")
        return None
    
async def fetch_user_id_by_share_secret(share_secret:str):
    try:
        resp = users.select('id').eq('share_secret', share_secret).execute()
        if validate_data_presence(resp):
            return resp.data[0]['id']
        else:
            logger.error(f"No user id found for share_secret {share_secret}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID for share_secret {share_secret}: {e}")
        return None

async def fetch_user_id_by_stripe_id(stripe_cust_id: str):
    try:
        resp = users.select('id').eq('stripe_cust_id', stripe_cust_id).execute()
        if validate_data_presence(resp):
            return resp.data[0]['id']
        else:
            logger.warning(f"No data found for cus_id {stripe_cust_id}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID for cus_id {stripe_cust_id}: {e}")
        return None
    
async def fetch_user_id_by_email(email: str):
    try:
        resp = users.select('id').eq('email', email).execute()
        if validate_data_presence(resp):
            return resp.data[0]['id']
        else:
            logger.error(f"No data found for email {email}, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID for email {email}: {e}")
        return None

    
# This one is used by stripe if a user adjusts their data in the portal
async def update_user_data(user_id:int, update_data:dict):
    try:
        # Perform the database update
        resp = users.update(update_data).eq('id', user_id).execute()

        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"couldnt update user data: {resp}")
            return None
    except Exception as e:
        logger.error(f"Error in update_user_data: {e}")
        return None

async def update_user_checkin(user_id, current_date):
    try:
        # Update user record
        users.update({
            'has_responded_today': False,
            'awaiting_reply': True,
            'last_habit_checkin_date': current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        }).eq('id', user_id).execute()
    except Exception as e:
        logger.error(f"error in update_user_checking {e}")

async def update_user_nudge(user_id):
    users.update({'sent_nudge_today':True}).eq('id', user_id).execute()

async def update_has_buddy(user_id, buddy_id):
    users.update({'has_buddy':True}).eq('id', user_id).execute()
    users.update({'has_buddy':True}).eq('id', buddy_id).execute()

async def insert_user_data(data:dict):
    resp = users.insert(data).execute()
    try:
        if validate_data_presence(resp):
            return resp.data[0]
        else:
            logger.error(f"No data found after insert_user_data, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error inserting user data: {e}")
        return None

async def update_stripe_user_data_dict(data:dict, cus_id:str):
    try:
        resp = users.update(data).eq('stripe_cust_id', cus_id).execute()
        if 'message' in resp:
            logger.error(f"we have an issue updating the last_msg of the user {resp}")
    except Exception as e:
        logger.error(f"error in update_stripe_user_data_dict: {e}")
        
async def update_last_msg(timestamp_iso, user_id:int):
    try:
        resp = users.update({'last_message': timestamp_iso}).eq('id', user_id).execute()
        if 'message' in resp:
            logger.error(f"we have an issue updating the last_msg of the user {resp}")
    except Exception as e:
        logger.error(f"error in update_last_msg: {e}")

async def reset_user_resp_state(user_id:int):
    try:
        resp = users.update({"has_responded_today": False, "awaiting_reply": False, 'sent_nudge_today': False}).eq("id", user_id).execute()
        if 'message' in resp:
            logger.error(f"we have an issue updating the response status of the user {resp}")
    except Exception as e:
        logger.error(f"error in reset_user_resp_state: {e}")


async def get_public_user_data(user_id:int):
    try:
        resp = users.select('name').eq('id', user_id).execute()
        if validate_data_presence(resp):
                return resp.data[0]
        else:
            logger.error(f"No user_data found for public user_data, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching public user data: {e}")
        return None
    
async def get_user_data_for_buddy(user_id:int):
    try:
        resp = users.select('name', 'last_message').eq('id', user_id).execute()
        if validate_data_presence(resp):
                return resp.data[0]
        else:
            logger.error(f"No user_data found for user_id, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching username and last message from user_id: {e}")
        return None


async def get_user_settings_data(user_id:int):
    try:
        resp = users.select('name', 'tz', 'reach_out', 'activity_schedule').eq('id', user_id).execute()
        if validate_data_presence(resp):
                return resp.data[0]
        else:
            logger.error(f"No user_data found for user_settings_data, {resp}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user_settings_data: {e}")
        return None
    
async def get_public_user_data_bulk(buddy_ids:list):
    try:
        response = users\
            .select("id", "name", "share_token")\
            .in_("id", buddy_ids)\
            .execute()
        if validate_data_presence(response):
            return {user['id']: user for user in response.data}
        else:
            logger.error(f"No user_data found for buddy_ids, {response}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user_data found for buddy_ids: {e}")
        return None

async def get_users_from_list_of_ids(user_ids:list):
    try:
        response = users\
            .select("id", "name", "last_message", "phone_number")\
            .in_("id", user_ids)\
            .execute()
        logger.info(f"response from userdata list: {response.data}")
        if validate_data_presence(response):
            return response.data #is a list of dicts
        else:
            logger.error(f"No user_data found for user_ids, {response}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user data for user_ids: {e}")
        return None
