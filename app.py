from flask import Flask ,render_template, flash, redirect, url_for, session, request, logging
# from data import Articles
import pymysql
from passlib.hash import pbkdf2_sha256
from functools import wraps
import json
import paho.mqtt.client as mqtt

temperature = []

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='1234', db='dryroom')

app = Flask(__name__)
app.debug=False

def on_connect( client, userdata, flags, rc ):
    # print("Connect with result code" + str(rc) )
    client.subscribe('temp')

def on_message( client, userdata, msg ):
    # print(float(msg.payload))
    # temp = []
    temperature.append(float(msg.payload))
    # cursor = db.cursor()
    # sql =  '''
    #      INSERT INTO arduino(humidity, temperature) 
    #      VALUES (%s, %s);
    #     '''
    # cursor.execute(sql, (temp[0], temp[1]))
    # db.commit()
    # db.close()
    print(float(msg.payload))
    # print(temp[1])


    
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
@is_logged_in
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

@app.route('/graph', methods=['GET', 'POST'])
@is_logged_in
def graph():
    cursor = db.cursor()
    sql = 'SELECT humidity, register_date FROM arduino ORDER BY register_date DESC limit 10;'
    cursor.execute(sql)
    db.commit()
    data_all = cursor.fetchall()
    print(data_all)
    data_temperature = []
    data_register_date = []
  
    for i, j  in reversed(data_all):
        data_temperature.append(i)
        data_register_date.append(str(j.date()))

    print(data_register_date)

    return render_template('graph.html', data1 = data_temperature, data2 = data_register_date)

    # for i in data_all:
    #     # print(i)
    #     # data_temperature.append(int(i[1]))
    #     print(len(data_temperature))
    #     print(data_all)
    #     if len(data_temperature) > 9:
    #         del data_temperature[0]
            
    #         data_temperature.append(int(data_all[len(data_all)-1][1]))
    #         # print(data_all[len(data_all)-1][1])
    #         # print(len(data_temperature))
    #         # data_temperature.append(int(i[1]))

    #     else:
    #         data_temperature.append(int(i[1]))
        
    #     # data_register_date.append(str(j.time()))
    
    # print(data_temperature)


@app.route('/test')
def test():
    cursor = db.cursor()
    sql = 'SELECT temperature, register_date FROM temperature;'
    cursor.execute(sql)
    data_all = cursor.fetchall()
    data_temperature = []
    data_register_date = []
    for i, j  in data_all :
        data_temperature.append(int(i))
        data_register_date.append(str(j))

    return render_template('test.html', data = [data_temperature, data_register_date])

@app.route('/interval')
def interval():
    return render_template('interval.html')

@app.route('/arduino', methods = ['GET'])
def hello_world():
    return str(temperature)
    # return render_template('interval.html', data =str(temperature) )  

if __name__ =='__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()

    app.secret_key = 'secretkey123456789'
    app.run(host='0.0.0.0', port='8000')