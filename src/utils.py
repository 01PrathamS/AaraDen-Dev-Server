import jwt
from datetime import datetime, timedelta, date

SECRET_KEY = "your-secret-key"  # Change this in production

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Fixed timedelta usage
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def resolve_date_range(type_param, start_date_str=None, end_date_str=None):
    today = date.today()
    start_date = end_date = None

    if type_param == "today":
        start_date = end_date = today

    elif type_param == "yesterday":
        start_date = end_date = today - timedelta(days=1)

    elif type_param == "this_week":
        start_date = today - timedelta(days=today.weekday())
        end_date = today

    elif type_param == "this_month":
        start_date = today.replace(day=1)
        end_date = today

    elif type_param == "custom_range":
        if not start_date_str or not end_date_str:
            raise ValueError("For custom_range, 'start_date' and 'end_date' are required")
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    else:
        raise ValueError("Invalid type. Use one of: today, yesterday, this_week, this_month, custom_range")

    return start_date, end_date
