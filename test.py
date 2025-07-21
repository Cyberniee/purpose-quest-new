from datetime import datetime, date, timezone, timedelta
from pytz import UTC

# def get_user_local_date(tz_offset_minutes: int):
#     # Current UTC time
#     utc_now = datetime.now()
#     print(f"UTC now: {utc_now}")

#     # Create a timezone offset
#     user_timezone = timezone(timedelta(minutes=tz_offset_minutes))

#     # Apply the offset
#     user_local_datetime = utc_now.replace(tzinfo=timezone.utc).astimezone(user_timezone)

#     # Return the date part
#     return user_local_datetime.date()

# print(get_user_local_date(tz_offset_minutes=-120))

print(datetime.now(UTC).isoformat())

print(timedelta(hours=12))