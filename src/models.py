from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy() 

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password_hash = db.Column(db.String(128), nullable=False) 

    def set_password(self, password): 
        # This produces hashes that are about 90–120 characters, which fit in VARCHAR(255).
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)