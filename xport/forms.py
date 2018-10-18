from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SubmitGromacsForm(FlaskForm):
        validators = [
                      FileRequired(),
                      FileAllowed(['tpr'], 'Must be a .tpr file')
                     ]
        tprfile = FileField(validators=validators)
        submit = SubmitField('Upload and submit')
    
class SubmitAmberForm(FlaskForm):
        validators = [
                      FileRequired(),
                     ]
        mdinfile = FileField(validators=validators)
        inpcrdfile = FileField(validators=validators)
        prmtopfile = FileField(validators=validators)
        submit = SubmitField('Upload and submit')
    
