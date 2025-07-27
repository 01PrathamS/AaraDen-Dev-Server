from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import jwt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy 
from models import db, User

from dotenv import load_dotenv 

load_dotenv() 

DB_HOST = os.getenv("DB_HOST", "mysql-2d.com")
DB_USER = os.getenv("DB_USER", "amin")
DB_PASS = os.getenv("DB_PASS", "AVJ_tr8")
DB_NAME = os.getenv("DB_NAME", "aaen")
DB_PORT = int(os.getenv("DB_PORT", 244))


app = Flask(__name__)
app.secret_key = 'your-jwt-secret-key-change-this-in-production'  # Change this in production
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = F'mysql+pymysql://{DB_USER}:{DB_PASS}@localhost:3306/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db.init_app(app)

# JWT Configuration
JWT_SECRET_KEY = 'your-jwt-secret-key-change-this-in-production'  # Should match app.secret_key
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(hours=24)  # Token expires in 24 hours

# # File to store user data
# USER_DATA_FILE = 'users.json'

# def load_users():
#     """Load users from JSON file"""
#     if os.path.exists(USER_DATA_FILE):
#         with open(USER_DATA_FILE, 'r') as f:
#             return json.load(f)
#     return {}

# def save_users(users):
#     """Save users to JSON file"""
#     with open(USER_DATA_FILE, 'w') as f:
#         json.dump(users, f, indent=2)

# def create_default_users():
#     """Create some default users for testing"""
#     users = load_users()
#     if not users:  # Only create if no users exist
#         default_users = {
#             'admin@example.com': {
#                 'id': str(uuid.uuid4()),
#                 'name': 'Admin User',
#                 'email': 'admin@example.com',
#                 'password_hash': generate_password_hash('admin123'),
#                 'created_at': datetime.now().isoformat()
#             },
#             'user1@example.com': {
#                 'id': str(uuid.uuid4()),
#                 'name': 'Test User',
#                 'email': 'user1@example.com',
#                 'password_hash': generate_password_hash('password123'),
#                 'created_at': datetime.now().isoformat()
#             }
#         }
#         save_users(default_users)
#         print("Default users created: admin@example.com/admin123, user1@example.com/password123")



def generate_jwt_token(user_id, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token):
    """Decode JWT token and return user info"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def jwt_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Decode token
        payload = decode_jwt_token(token)
        if payload is None:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user info to request context
        request.current_user = {
            'user_id': payload['user_id'],
            'email': payload['email']
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        print(f"Registration request data: {data}")  # Debug log
        
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            print("Missing required fields")  # Debug log
            return jsonify({'error': 'Name, email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        name = data['name'].strip()
        
        print(f"Attempting to register user: {email}")  # Debug log
        
        # Basic email validation
        if '@' not in email:
            print("Invalid email format")  # Debug log
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            print("Password too short")  # Debug log
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        if len(name) < 2:
            print("Name too short")  # Debug log
            return jsonify({'error': 'Name must be at least 2 characters long'}), 400
        
        # users = load_users()
        # print(f"Current users: {list(users.keys())}")  # Debug log
        
        # if email in users:
        #     print("Email already exists")  # Debug log
        #     return jsonify({'error': 'Email already exists'}), 400
        
        existing_user = User.query.filter_by(email=email).first() 
        if existing_user: 
            return jsonify({"error": "Email already exists"}), 400
        # Create new user
        user_id = str(uuid.uuid4())
        new_user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        # users[email] = new_user
        # print(f"Created new user: {email}")  # Debug log
        
        # save_users(users)
        # print("User saved successfully")  # Debug log
        
        # Generate JWT token for the new user
        token = generate_jwt_token(user_id, email)
        
        return jsonify({
            'access_token': token,
            'user': {
                'id': user_id,
                'name': name,
                'email': email
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug log
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        print(f"Login request data: {data}")  # Debug log
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # users = load_users()
        
        # if email not in users:
        #     return jsonify({'error': 'Invalid email or password'}), 401
        
        # user = users[email]
        
        # if not check_password_hash(user['password_hash'], password):
        #     return jsonify({'error': 'Invalid email or password'}), 401
        
        user = User.query.filter_by(email=email).first() 
        if not user or not check_password_hash(user.password_has, password): 
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate JWT token
        token = generate_jwt_token(user['id'], email)
        
        print(f"Login successful for user: {email}")  # Debug log
        
        return jsonify({
            'access_token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': email
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
@jwt_required
def logout():
    """Logout user (with JWT, this is mainly for client-side cleanup)"""
    # With JWT, logout is typically handled client-side by removing the token
    # Server-side logout would require token blacklisting (more complex)
    return jsonify({'message': 'Logout successful. Please remove token from client.'}), 200

@app.route('/api/verify-token', methods=['GET'])
@jwt_required
def verify_token():
    """Verify JWT token and return user info"""
    users = load_users()
    user_email = request.current_user['email']
    
    if user_email not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[user_email]
    
    return jsonify({
        'valid': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }), 200

@app.route('/api/me', methods=['GET'])
@jwt_required
def get_current_user():
    """Get current user info"""
    users = load_users()
    user_email = request.current_user['email']
    
    if user_email not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[user_email]
    
    return jsonify({
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }), 200

@app.route('/api/protected', methods=['GET'])
@jwt_required
def protected_route():
    """Example protected route"""
    return jsonify({
        'message': f'Hello {request.current_user["email"]}, this is a protected route!',
        'user_id': request.current_user['user_id']
    }), 200

@app.route('/api/users', methods=['GET'])
@jwt_required
def list_users():
    """List all users (for admin purposes)"""
    users = load_users()
    user_list = []
    
    for email, user_data in users.items():
        user_list.append({
            'id': user_data['id'],
            'name': user_data.get('name', 'Unknown'),
            'email': user_data['email'],
            'created_at': user_data['created_at']
        })
    
    return jsonify({'users': user_list}), 200

@app.route('/api/refresh-token', methods=['POST'])
@jwt_required
def refresh_token():
    """Refresh JWT token"""
    # Generate new token with extended expiration
    new_token = generate_jwt_token(
        request.current_user['user_id'], 
        request.current_user['email']
    )
    
    return jsonify({
        'access_token': new_token
    }), 200

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'message': 'Flask JWT Auth API is running'}), 200

@app.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized requests"""
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(403)
def forbidden(error):
    """Handle forbidden requests"""
    return jsonify({'error': 'Forbidden access'}), 403

if __name__ == '__main__':
    # Create default users on startup
    create_default_users()
    
    print("Starting Flask JWT Auth API...")
    print("Default users: admin@example.com/admin123, user1@example.com/password123")
    print("JWT tokens expire in 24 hours")
    app.run(debug=True, host='0.0.0.0', port=5000)