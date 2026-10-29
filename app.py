from pathlib import Path
from contextlib import contextmanager
import sqlite3
import secrets
import math
from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import uuid4
from flask import Flask, render_template, request, abort, session, redirect, url_for
from technical_posts import TECH_POSTS

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
DB = Path(__file__).parent / 'blog.sqlite3'
CATEGORIES = ['全部文章', '设计灵感', '技术手记', '生活方式', '漫游日记']
SEEDS = [
('less-but-better', '把生活留给真正重要的事', '在信息过载的日子里，重新发现少即是多的力量。关于专注、留白，以及一种更轻盈的生活方式。', '生活方式', 'photo-1441974231531-c6227db76b6e', '2026-10-24', 8),
('quiet-design', '好的设计，往往安静得恰到好处', '从一把椅子、一束光到一个界面，寻找那些不动声色的设计细节。', '设计灵感', 'photo-1600210492486-724fe5c67fb0', '2026-10-22', 6),
('python-craft', '写代码，也是一种整理思绪的方式', '用 Python 把重复的事情交给机器，把好奇心留给自己。', '技术手记', 'photo-1499750310107-5fef28a66643', '2026-10-20', 10),
('mountain-weekend', '去山里，找回自己的节奏', '关掉通知，沿着一条没有名字的小路，走进秋天深处。', '漫游日记', 'photo-1464822759023-fed622ff2c3b', '2026-10-18', 7),
('morning-ritual', '一杯咖啡的时间，慢慢醒来', '清晨不需要立刻高效。有时候，发一会儿呆就是最好的开始。', '生活方式', 'photo-1442512595331-e89e73853f31', '2026-10-15', 5),
('digital-garden', '建立一个属于自己的数字花园', '记录未完成的想法，让知识在连接中生长，而不是在收藏夹里落灰。', '技术手记', 'photo-1449247709967-d4461a6a6103', '2026-10-12', 9),
('warm-palette', '在日常里，收集温柔的颜色', '旧书的米黄、树影的深绿、日落的陶土色，都是生活递来的调色板。', '设计灵感', 'photo-1494438639946-1ebd1d20bf85', '2026-10-09', 6),
]

@contextmanager
def connect():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()

def init_db():
    with connect() as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, title TEXT, excerpt TEXT, category TEXT, image TEXT, date TEXT, minutes INTEGER)')
        if 'body' not in {row[1] for row in connection.execute('PRAGMA table_info(posts)')}:
            connection.execute("ALTER TABLE posts ADD COLUMN body TEXT NOT NULL DEFAULT ''")
        connection.executemany('INSERT OR IGNORE INTO posts (slug,title,excerpt,category,image,date,minutes) VALUES (?,?,?,?,?,?,?)', SEEDS)
        connection.executemany('INSERT OR IGNORE INTO posts (slug,title,excerpt,category,image,date,minutes,body) VALUES (?,?,?,?,?,?,?,?)', TECH_POSTS)

@app.route('/write', methods=['GET', 'POST'])
def write():
    session.setdefault('csrf', secrets.token_hex(32))
    values = request.form if request.method == 'POST' else {}
    errors = []
    if request.method == 'POST':
        if not secrets.compare_digest(request.form.get('csrf', ''), session['csrf']):
            abort(400)
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        category = request.form.get('category', '')
        excerpt = request.form.get('excerpt', '').strip()
        if not 1 <= len(title) <= 120:
            errors.append('请填写 1–120 字的标题。')
        if not 1 <= len(body) <= 100000:
            errors.append('请填写正文，最多 100,000 字。')
        if category not in CATEGORIES[1:]:
            errors.append('请选择有效的分类。')
        if len(excerpt) > 300:
            errors.append('摘要最多 300 字。')
        if not errors:
            slug = uuid4().hex
            with connect() as connection:
                connection.execute('INSERT INTO posts (slug,title,excerpt,category,image,date,minutes,body) VALUES (?,?,?,?,?,?,?,?)',
                    (slug, title, excerpt or body.replace('\n', ' ')[:120], category, 'photo-1499750310107-5fef28a66643', datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat(), max(1, math.ceil(len(body)/400)), body))
            return redirect(url_for('article', slug=slug), code=303)
    return render_template('write.html', categories=CATEGORIES[1:], values=values, errors=errors), (422 if errors else 200)

@app.route('/')
def index():
    category = request.args.get('category', '全部文章')
    query = request.args.get('q', '').strip()
    sql, params = 'SELECT * FROM posts WHERE 1=1', []
    if category in CATEGORIES[1:]:
        sql += ' AND category=?'
        params.append(category)
    if query:
        sql += ' AND (title LIKE ? OR excerpt LIKE ? OR body LIKE ?)'
        params.extend([f'%{query}%'] * 3)
    with connect() as connection:
        posts = connection.execute(sql + ' ORDER BY date DESC, id DESC', params).fetchall()
        featured = connection.execute("SELECT * FROM posts WHERE slug='less-but-better'").fetchone()
    return render_template('index.html', posts=posts, featured=featured, categories=CATEGORIES, category=category, query=query)

@app.route('/posts/<slug>')
def article(slug):
    with connect() as connection:
        post = connection.execute('SELECT * FROM posts WHERE slug=?', (slug,)).fetchone()
        if post is None:
            abort(404)
        related = connection.execute('SELECT * FROM posts WHERE slug != ? ORDER BY (category=?) DESC, date DESC LIMIT 2', (slug, post['category'])).fetchall()
    return render_template('article.html', post=post, related=related)

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

init_db()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
