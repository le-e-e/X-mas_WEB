from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    preview_image = db.Column(db.LargeBinary, nullable=True)
    image_mime_type = db.Column(db.String(32), nullable=True)

    def __repr__(self):
        return f'<Post {self.title}>' 