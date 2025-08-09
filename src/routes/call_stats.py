from flask import Blueprint, request, jsonify
from sqlalchemy import func
from src.models import db, CallLog, Recording
from src.routes.auth_decorator import token_required  
from src.utils import resolve_date_range

stats_bp = Blueprint("stats", __name__)
@stats_bp.route("/call-counts", methods=["GET"])
@token_required
def get_call_stats():
    type_param = request.args.get("type")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if not type_param:
        return jsonify({"error": "Missing 'type' parameter"}), 400

    try:
        # Use the shared helper function
        start_date, end_date = resolve_date_range(type_param, start_date_str, end_date_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

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


##  number of incoming and outgoing calls 
@stats_bp.route("/call-direction", methods=["GET"])
@token_required
def get_call_direction():
    type_param = request.args.get("type")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if not type_param:
        return jsonify({"error": "Missing 'type' parameter"}), 400

    try:
        # Use the shared helper function
        start_date, end_date = resolve_date_range(type_param, start_date_str, end_date_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        # Total recordings
        total_count = db.session.query(func.count(Recording.recording_id)) \
            .join(CallLog, Recording.call_log_id == CallLog.id) \
            .filter(Recording.recorded_date.between(start_date, end_date)) \
            .scalar()

        # Inbound calls
        inbound_count = db.session.query(func.count(Recording.recording_id)) \
            .join(CallLog, Recording.call_log_id == CallLog.id) \
            .filter(
                Recording.recorded_date.between(start_date, end_date),
                CallLog.direction == 'Inbound'
            ).scalar()

        # Outbound calls
        outbound_count = db.session.query(func.count(Recording.recording_id)) \
            .join(CallLog, Recording.call_log_id == CallLog.id) \
            .filter(
                Recording.recorded_date.between(start_date, end_date),
                CallLog.direction == 'Outbound'
            ).scalar()

        return jsonify({
            "type": type_param,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total_recordings": total_count,
            "Inbound": inbound_count,
            "Outbound": outbound_count
        })

    except Exception as e:
        print("Error in get_call_stats:", str(e))
        return jsonify({"error": "Internal server error"}), 500


##  number of voice mails 


##
