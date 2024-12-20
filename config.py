import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://lee:lee@localhost/blog_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 제한
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    SECRET_KEY = os.urandom(24)