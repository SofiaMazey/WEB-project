from flask import Flask, render_template, redirect, abort, request
from cite.data import db_session
from cite.data.users import User
from cite.data.jams import Jams
import os
from cite.forms.jams import JamsForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from cite.forms.user import RegisterForm, LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader  # функция для получения пользователя
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jams = db_sess.query(Jams)
    user = db_sess.query(User)
    return render_template("index.html", jams=jams, user=user)


@app.route('/register', methods=['GET', 'POST'])  # регистрация пользователя
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация производителя',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация производителя',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            company_name=form.company_name.data,
            number=form.number.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация производителя', form=form)


@app.route('/login', methods=['GET', 'POST'])  # вход в аккаунт
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/jams',  methods=['GET', 'POST'])  # добавление джема
@login_required
def add_jams():
    form = JamsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jams = Jams()
        jams.title = form.title.data
        jams.picture = form.picture.data
        jams.about = form.about.data
        current_user.jams.append(jams)
        db_sess.merge(current_user)  # изменение текущего пользователя
        db_sess.commit()
        return redirect('/products')
    return render_template('jams.html', title='Добавление продукта',
                           form=form)


@app.route('/jams/<int:id>', methods=['GET', 'POST'])  # изменение
@login_required
def edit_jams(id):
    form = JamsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jams = db_sess.query(Jams).filter(Jams.id == id,
                                          Jams.user == current_user
                                          ).first()
        if jams:
            form.title.data = jams.title
            form.picture.data = jams.picture
            form.about.data = jams.about
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jams = db_sess.query(Jams).filter(Jams.id == id,
                                          Jams.user == current_user
                                          ).first()
        if jams:
            jams.title = form.title.data
            jams.picture = form.picture.data
            jams.about = form.about.data
            db_sess.commit()
            return redirect('/products')
        else:
            abort(404)
    return render_template('jams.html',
                           title='Редактирование продукта',
                           form=form
                           )


@app.route('/jams_delete/<int:id>', methods=['GET', 'POST'])  # удаление
@login_required
def jams_delete(id):
    db_sess = db_session.create_session()
    jams = db_sess.query(Jams).filter(Jams.id == id,
                                      Jams.user == current_user
                                      ).first()
    if jams:
        db_sess.delete(jams)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/products')


@app.route("/products")  # отображение всех джемов, которые есть
def products():
    db_sess = db_session.create_session()
    jams = db_sess.query(Jams)
    user = db_sess.query(User)
    return render_template("products.html", jams=jams, user=user)


@app.route("/company_products/<int:id>", methods=['GET', 'POST'])  # все продукты от конкретного производителя
def company_products(id):
    db_sess = db_session.create_session()
    jams = db_sess.query(Jams).filter(Jams.user_id == id,
                                      )
    user = db_sess.query(User)
    return render_template("company_products.html", jams=jams, user=user)


def main():
    db_session.global_init("db/shop.sqlite")
    # app.run()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
