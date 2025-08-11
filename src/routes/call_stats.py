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
        # Base query with join
        base_query = db.session.query(func.count(Recording.recording_id)) \
            .join(CallLog, Recording.call_log_id == CallLog.id) \
            .filter(Recording.recorded_date.between(start_date, end_date))

        # Counts
        total_count = base_query.scalar()

        inbound_count = base_query.filter(CallLog.direction == 'Inbound').scalar()
        outbound_count = base_query.filter(CallLog.direction == 'Outbound').scalar()

        # Voice mail filter
        voicemail_filter = func.lower(Recording.tags).like('%voice mail%')

        voice_mail_count = base_query.filter(voicemail_filter).scalar()
        inbound_voice_mail_count = base_query.filter(CallLog.direction == 'Inbound', voicemail_filter).scalar()
        outbound_voice_mail_count = base_query.filter(CallLog.direction == 'Outbound', voicemail_filter).scalar()

        return jsonify({
            "type": type_param,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total_recordings": total_count,
            "Inbound": inbound_count,
            "Outbound": outbound_count,
            "voice_mail_count": voice_mail_count,
            "Inbound_voice_mail_count": inbound_voice_mail_count,
            "Outbound_voice_mail_count": outbound_voice_mail_count
        })

    except Exception as e:
        print("Error in get_call_direction:", str(e))
        return jsonify({"error": "Internal server error"}), 500

