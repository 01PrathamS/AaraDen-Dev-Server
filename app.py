from flask import Flask, request, jsonify
from src.models import db, User
from src.routes.auth import auth_bp
from src.routes.call_stats import stats_bp
from src.utils import decode_token

import os 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:<DB_PASS>@localhost/<DB_PASS>'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}/{os.getenv("DB_DATABASE")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(stats_bp, url_prefix="/stats")

# @app.before_first_request
# def create_tables():
#     db.create_all()

@app.route('/protected', methods=['GET'])
def protected():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'error': 'Token missing'}), 401

    token = auth_header.split(" ")[1]
    user_id = decode_token(token)

    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    user = User.query.get(user_id)
    return jsonify({'message': f'Welcome, {user.email}'})


if __name__ == '__main__':
    app.run(debug=True)