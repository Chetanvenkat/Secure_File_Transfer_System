from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    filename_orig = db.Column(db.String(256), nullable=False)
    storage_path = db.Column(db.String(512), nullable=False)
    encrypted_key = db.Column(db.LargeBinary, nullable=False)
    filesize = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SharedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, nullable=False)      # File.id
    sender_id = db.Column(db.Integer, nullable=False)    # User.id
    recipient_id = db.Column(db.Integer, nullable=False) # User.id
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
