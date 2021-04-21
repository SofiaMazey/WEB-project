from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class JamsForm(FlaskForm):
    title = StringField('Название варенья/джема', validators=[DataRequired()])
    picture = StringField("Ссылка на изображение")
    about = TextAreaField("О Вашем продукте(например, из чего изготовлен продукт)")
    submit = SubmitField('Применить')
