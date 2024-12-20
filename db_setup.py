from models import db

def init_db(app):
    with app.app_context():
        db.create_all()  # 테이블 생성
        # db.drop_all()  # 필요에 따라 주석 처리 