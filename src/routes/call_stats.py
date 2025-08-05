from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, date
from datetime import datetime, timedelta, date
from sqlalchemy import func
from src.models import db, CallLog, Recording
from src.routes.auth_decorator import token_required  

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/call-stats", methods=["GET"])
@token_required
def get_call_stats():
    type_param = request.args.get("type")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if not type_param:
        return jsonify({"error": "Missing 'type' parameter"}), 400

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
            return jsonify({"error": "For custom_range, 'start_date' and 'end_date' are required"}), 400
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    else:
        return jsonify({"error": "Invalid type. Use one of: today, yesterday, this_week, this_month, custom_range"}), 400

    try:
        count = db.session.query(func.count(Recording.recording_id)) \
            .join(CallLog, Recording.call_log_id == CallLog.id) \
            .filter(Recording.recorded_date.between(start_date, end_date)) \
            .scalar()

        return jsonify({
            "type": type_param,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "recordings_count": count
        })

    except Exception as e:
        print("Error in get_call_stats:", str(e))
        return jsonify({"error": "Internal server error"}), 500
