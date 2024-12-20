# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from models import db, Post
from config import Config
from db_setup import init_db  # db_setup.py에서 init_db 함수를 가져옵니다.
import os
from PIL import Image
import io
import bleach
import secrets
from werkzeug.utils import secure_filename
import imghdr  # 이미지 타입 확인을 위한 라이브러리

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config.from_object(Config)

db.init_app(app)

# 데이터베이스 초기화
init_db(app)

def allowed_file(filename):
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in app.config['UPLOAD_EXTENSIONS']

def validate_image(file_stream):
    # 이미지 파일 검증
    header = file_stream.read(512)
    file_stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return False
    return '.' + format in app.config['UPLOAD_EXTENSIONS']

def sanitize_html(content):
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 
        'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote', 
        'code', 'pre', 'hr', 'img'
    ]
    allowed_attributes = {
        'img': ['src', 'alt', 'title'],
        'a': ['href', 'title'],
    }
    # src 속성 추가 검증
    def cleaner(tag, name, value):
        if name == 'src':
            # 허용되는 프로토콜 목록
            allowed_protocols = ['http:', 'https:']
            # data: URL이나 javascript: URL 차단
            if any(value.lower().startswith(p) for p in allowed_protocols):
                return True
            return False
        if name == 'href':
            # javascript: URL 차단
            if value.lower().startswith('javascript:'):
                return False
        return True

    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=['http', 'https'],
        strip=True,
        filters=[lambda tag, name, value: cleaner(tag, name, value)]
    )

@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            
            # 디버깅을 위한 출력
            print("받은 데이터:", title, content)
            
            if not title or not content:
                flash('제목과 내용을 모두 입력해주세요.', 'error')
                return redirect(url_for('create'))

            preview_image = None
            image_mime_type = None

            if 'preview_image' in request.files:
                file = request.files['preview_image']
                if file and file.filename:
                    if not allowed_file(file.filename):
                        flash('허용되지 않는 파일 형식입니다.', 'error')
                        return redirect(url_for('create'))

                    try:
                        image = Image.open(file)
                        max_size = (800, 800)
                        image.thumbnail(max_size)
                        
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        preview_image = img_byte_arr.getvalue()
                        image_mime_type = 'image/png'
                    except Exception as e:
                        print("이미지 처리 오류:", str(e))  # 디버깅용
                        flash('이미지 처리 중 오류가 발생했습니다.', 'error')
                        return redirect(url_for('create'))

            try:
                post = Post(
                    title=title,
                    content=content,
                    preview_image=preview_image,
                    image_mime_type=image_mime_type
                )
                
                db.session.add(post)
                db.session.commit()
                
                flash('글이 성공적으로 작성되었습니다.', 'success')
                return redirect(url_for('index'))
            
            except Exception as e:
                print("데이터베이스 오류:", str(e))  # 디버깅용
                db.session.rollback()
                flash('데이터베이스 오류가 발생했습니다.', 'error')
                return redirect(url_for('create'))

        except Exception as e:
            print("일반 오류:", str(e))  # 디버깅용
            flash('글 작성 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('create'))

    return render_template('create.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/images/<int:post_id>')
def get_preview_image(post_id):
    post = Post.query.get_or_404(post_id)
    if post.preview_image and post.image_mime_type:
        return send_file(
            io.BytesIO(post.preview_image),
            mimetype=post.image_mime_type,
            as_attachment=False
        )
    return '', 404

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(413)
def too_large_error(error):
    flash('파일이 너무 큽니다. 16MB 이하의 파일만 업로드 가능합니다.', 'error')
    return redirect(url_for('create'))

@app.route('/get_posts')
def get_posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'has_image': post.preview_image is not None
        })
    return jsonify(posts_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)