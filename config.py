import os

class Config:
    # 데이터베이스 URI 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://lee:lee@localhost/blog_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 제한
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')  # 비밀 키 설정 