from flask import Flask ,render_template, flash, redirect, url_for, session, request, logging
# from data import Articles
from datetime import time
import pymysql
from passlib.hash import pbkdf2_sha256
from functools import wraps

app = Flask(__name__)
app.debug=True

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='1234', db='dryroom')

# @app.route("/")
# def image():
#     return render_template('image.html', image_file="image/test1.png")


def is_logged_in(f):
    @wraps(f)
    def _wraper(*args, **kwargs):
        if 'is_logged' in session:
        # if session['is_logged']:
            return f(*args, **kwargs)
        else:
            flash('UnAuthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return _wraper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form.get('username')
        pw = request.form.get('password')
        # print([id , pw])

        sql='SELECT * FROM users WHERE username = %s'
        cursor  = db.cursor()
        cursor.execute(sql, [id])
        users = cursor.fetchone()
        # print(users)
        
        if users == None:
            return redirect(url_for('login'))
        else:
            if pbkdf2_sha256.verify(pw, users[4]):
                session['is_logged'] = True
                session['username'] = users[2]
                # print(session)
                return redirect('/')
            else:
                return redirect(url_for('login'))
        
        # return "Success"
    else:
        return render_template('login.html')

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['username'] == 'ADMIN':
            return redirect('/admin')
        else:
            return f(*args, **kwargs)
    return wrap

def is_admined(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['username'] != "ADMIN":
            return redirect('/')
        
        else:
            return f(*args, **kwargs)
    return wrap


@app.route('/admin', methods = ['GET', 'POST'])
@is_logged_in
@is_admined
def admin():
    cursor = db.cursor()
    sql = 'SELECT * FROM users;'
    cursor.execute(sql)
    admin_user = cursor.fetchall()
    return render_template('admin.html', data = admin_user)

@app.route('/user/<string:id>', methods = ['GET', 'POST'])
@is_logged_in
@is_admined
def change_level(id):
    if request.method == 'POST':
        cursor = db.cursor()
        sql = 'UPDATE `users` SET `auth` = %s WHERE `id` = %s;'
        auth = request.form['auth']
        cursor.execute(sql, [auth, id])
        return redirect('/')
    else:
        cursor = db.cursor()
        sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(sql, [id])
        user = cursor.fetchone()
        return render_template('change_level.html', users = user)


@app.route('/')
@is_logged_in
@is_admin
def index():
    # print("Success")
    # session['test'] = "Woobin Lee"
    # session_data = session
    # print(session_data)
    # return "TEST"
    return render_template('home.html')

@app.route('/about')
def about():
    # print("Success")
    # return "TEST"
    return render_template('about.html')

def is_logged_out(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_logged' in session:
            return redirect(url_for('home'))
        else:
            return f(*args, **kwargs)

    return wrap

@app.route('/register', methods=['GET','POST'])
@is_logged_out
def register():
    if request.method == 'POST':
        # data = request.body.get('author')
        name = request.form.get('name')
        email = request.form.get('email')
        password = pbkdf2_sha256.hash(request.form.get('password'))
        re_password = request.form.get('re_password')
        username = request.form.get('username')
        # name = form.name.data

        cursor = db.cursor()
        sql = 'SELECT username FROM users WHERE username = %s'
        cursor.execute(sql, [username])
        username_one = cursor.fetchone()
        if username_one:
            return redirect(url_for('register'))

        else:
            if(pbkdf2_sha256.verify(re_password, password)):
                # print(pbkdf2_sha256.verify(re_password, password))
                sql = '''
                    INSERT INTO users (name, email, username, password) 
                    VALUES (%s ,%s, %s, %s)
                '''
                cursor.execute(sql, (name, email, username, password))
                db.commit()
                # cursor = db.cursor()
                # cursor.execute('SELECT * FROM users;')
                # users = cursor.fetchall()

                return redirect(url_for('login'))
            else:
                return redirect(url_for('register'))
        db.close()
    else:
        return render_template('register.html')

@app.route('/articles')
@is_logged_in
def articles():
    # articles = Articles()
    # print(len(articles))
    cursor = db.cursor()
    sql = 'SELECT * FROM topic;'
    cursor.execute(sql)
    data = cursor.fetchall()
    # print(data)
    return render_template('articles.html', articles = data)


@app.route('/article/<string:id>')
@is_logged_in
def article(id):
    # print(type(id))
    # articles= Articles()[id-1]
    cursor = db.cursor()
    sql = 'SELECT * FROM topic WHERE id = %s;'
    cursor.execute(sql, [id])
    topic = cursor.fetchone()
    # print(topic)
    return render_template('article.html', data = topic)

@app.route('/add_articles', methods = ['GET', 'POST'])
@is_logged_in
def add_articles():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        author = request.form['author']
        cursor = db.cursor()
        sql = ''' 
        INSERT INTO topic (title, body, author) 
                VALUES (%s, %s, %s)
        '''
        cursor.execute(sql, (title, body, author))
        db.commit()
        return redirect('/articles')
    else:
        return render_template('add_articles.html')
    db.close()

@app.route('/article/<string:id>/edit_article', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        author = request.form['author']
        cursor = db.cursor()
        sql = ''' 
        UPDATE `topic` SET `title` = %s, `body` = %s, `author` = %s WHERE `id` = %s;
        '''
        cursor.execute(sql, (title, body, author, id))
        db.commit()
        # print(title)
        return redirect(url_for('articles'))
    else :
        # print(id)
        cursor = db.cursor()
        sql = 'SELECT * FROM topic WHERE id = %s;'
        cursor.execute(sql, [id])
        topic = cursor.fetchone()
        return render_template('edit_article.html', data = topic)
    db.close()

@app.route('/delete/<string:id>', methods = ['POST'])
@is_logged_in
def delete(id):
    cursor = db.cursor()
    sql = 'DELETE FROM topic WHERE id = %s;'
    cursor.execute(sql, [id])
    db.commit()
    return redirect(url_for('articles'))

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/graph")
def graph():
    legend = 'Temperatures'
    temperatures = [73.7, 73.4, 73.8, 72.8, 68.7, 65.2,
                    61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
                    70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
    times = ['12:00PM', '12:10PM', '12:20PM', '12:30PM', '12:40PM', '12:50PM',
             '1:00PM', '1:10PM', '1:20PM', '1:30PM', '1:40PM', '1:50PM',
             '2:00PM', '2:10PM', '2:20PM', '2:30PM', '2:40PM', '2:50PM']
    return render_template('graph.html', values=temperatures, labels=times, legend=legend)



if __name__ =='__main__':
    app.secret_key = 'secretkey123456789'
    app.run(host='0.0.0.0', port='8000')