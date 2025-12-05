import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask secret key for sessions
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-123")

    # SQLite DB inside project folder
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Where encrypted files are stored
    UPLOAD_FOLDER = os.path.join(basedir, "instance", "uploads")

    # Master key for file encryption (Fernet base64 key)
    # In production: set FILE_MASTER_KEY in environment.
    FILE_MASTER_KEY = os.environ.get(
        "FILE_MASTER_KEY",
        "R6a1x8FhUwwZI8pHGhYkfj0wS6ZQG4FZUp3WjpPYNf4="  # dev only
    )
