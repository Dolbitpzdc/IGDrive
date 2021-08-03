import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

#conf
DATABASE = '/tmp/IGDrive.db'
DEBUG = True
SECRET_KEY = '2w3eefk4nbh5bfuk6dee56'
MAX_CONTENT_LENGTH = 2048 * 2048

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'IGDrive.db ')))

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    dbase = FDataBase(db)
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route('/')
@app.route('/home')
def home():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("home.html", title='Главная')


@app.route('/login', methods=["POST", "GET"])
def login():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('profile'))
        
        flash("Неверный логин или пароль", category='error')

    
    return render_template("login.html", title='Авторизация')


@app.route('/register', methods=["POST", "GET"])
def register():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == 'POST':
        if len(request.form['username']) > 3 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and len(request.form['phone']) > 6 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['username'], request.form['email'], request.form['phone'], hash)
            if res:
                flash("Ты зарегистрирован", category='success')
                return redirect(url_for('login'))
            else:
                flash("Ошибка записи в бд", category='error')
        else:
            flash("Неверно заполены поля", category='error')


    return render_template("register.html", title='Регистрация')


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/jpg'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html")

# f"""<p><a href="{url_for('logout')}">Выйти из профиля</a>
#                 <p>user info: {current_user.get_username()}"""



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))



@app.teardown_appcontext
def close_db(erro):
    if hasattr(g, 'link_db'):
        g.link_db.close()



if __name__ == "__main__":
    app.run(debug=True)

# db = get_db()
# dbase = FDataBase(db)