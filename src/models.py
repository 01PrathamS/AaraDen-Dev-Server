from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ----------------------------
# User model
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ----------------------------
# CallLog model
# ----------------------------
class CallLog(db.Model):
    __tablename__ = 'call_logs'

    id = db.Column(db.String(50), primary_key=True)
    session_id = db.Column(db.String(50))
    telephony_session_id = db.Column(db.String(50))
    party_id = db.Column(db.String(50))
    start_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    duration_ms = db.Column(db.BigInteger)
    type = db.Column(db.String(50))
    internal_type = db.Column(db.String(50))
    direction = db.Column(db.String(20))
    action = db.Column(db.String(50))
    result = db.Column(db.String(50))
    reason = db.Column(db.String(255))
    reason_description = db.Column(db.Text)
    from_name = db.Column(db.String(255))
    from_number = db.Column(db.String(50))
    from_location = db.Column(db.String(255))
    to_name = db.Column(db.String(255))
    to_number = db.Column(db.String(50))
    to_location = db.Column(db.String(255))
    uri = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    recordings = db.relationship('Recording', backref='call_log', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "telephony_session_id": self.telephony_session_id,
            "party_id": self.party_id,
            "start_time": self.start_time,
            "duration": self.duration,
            "duration_ms": self.duration_ms,
            "type": self.type,
            "internal_type": self.internal_type,
            "direction": self.direction,
            "action": self.action,
            "result": self.result,
            "reason": self.reason,
            "reason_description": self.reason_description,
            "from_name": self.from_name,
            "from_number": self.from_number,
            "from_location": self.from_location,
            "to_name": self.to_name,
            "to_number": self.to_number,
            "to_location": self.to_location,
            "uri": self.uri,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "recordings": [r.to_dict() for r in self.recordings]
        }


# ----------------------------
# Recording model
# ----------------------------
class Recording(db.Model):
    __tablename__ = 'recordings'

    recording_id = db.Column(db.String(50), primary_key=True)
    call_log_id = db.Column(db.String(50), db.ForeignKey('call_logs.id'), index=True)
    recording_uri = db.Column(db.Text)
    recording_type = db.Column(db.String(50))
    content_uri = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    downloaded_at = db.Column(db.DateTime)
    transcript = db.Column(db.Text)
    transcription_status = db.Column(
        db.Enum('pending', 'processing', 'complete', 'error'),
        default='pending'
    )
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    observation = db.Column(db.String(100))
    remark_on_observation = db.Column(db.String(100))
    tags = db.Column(db.String(255))
    speakers = db.Column(db.String(500))
    diarize_segments = db.Column(db.JSON)
    missed_opportunity = db.Column(db.Text)
    explaination = db.Column(db.Text)
    suggested_better_reply = db.Column(db.Text)
    recorded_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "recording_id": self.recording_id,
            "call_log_id": self.call_log_id,
            "recording_uri": self.recording_uri,
            "recording_type": self.recording_type,
            "content_uri": self.content_uri,
            "file_path": self.file_path,
            "downloaded_at": self.downloaded_at,
            "transcript": self.transcript,
            "transcription_status": self.transcription_status,
            "created_at": self.created_at,
            "observation": self.observation,
            "remark_on_observation": self.remark_on_observation,
            "tags": self.tags,
            "speakers": self.speakers,
            "diarize_segments": self.diarize_segments,
            "missed_opportunity": self.missed_opportunity,
            "explaination": self.explaination,
            "suggested_better_reply": self.suggested_better_reply,
            "recorded_date": self.recorded_date
        }


