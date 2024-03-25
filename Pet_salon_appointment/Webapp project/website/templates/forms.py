from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateField, SelectMultipleField, widgets
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_login import current_user
from app.models import *
import datetime

class PetChoiceIterable(object):
    def __iter__(self):
        pets=Pet.query.all()
        choices=[(pets.id,pets.name) for pet in pets] 
        for choice in choices:
            yield choice

class BookAppointmentForm(FlaskForm):
    pets=SelectField('Choose room',coerce=int,choices=PetChoiceIterable())
    date=DateField('Choose date', format="%m/%d/%Y",validators=[DataRequired()])
    time=SelectField('Choose starting time(in 24hr expression)',coerce=int,choices=[(i,i) for i in range(9,19)])
    service=SelectField('Choose service',coerce=int,choices=ServiceChoiceIterable(),option_widget=widgets.CheckboxInput(),widget=widgets.ListWidget(prefix_label=False))
    groomer=SelectField('Choose groomer',coerce=int,choices=GroomerChoiceIterable(),option_widget=widgets.CheckboxInput(),widget=widgets.ListWidget(prefix_label=False))
    submit=SubmitField('Book')
    
    def validate_date(self,date):
        if self.date.data<datetime.datetime.now().date():
            raise ValidationError('You can only book for day after today.')

class ServiceChoiceIterable(object):
    def __iter__(self):
        services=Service.query.all()
        choices=[(service.id,f'{service.service}') for service in services] 
        #choices=[choice for choice in choices if choice[1]!='admin'] # do not delete admin
        for choice in choices:
            yield choice

class GroomerChoiceIterable(object):
    def __iter__(self):
        groomers=Groomer.query.all()
        choices=[(groomer.id,f'{groomer.name}') for groomer in groomers] 
        #choices=[choice for choice in choices if choice[1]!='admin'] # do not delete admin
        for choice in choices:
            yield choice