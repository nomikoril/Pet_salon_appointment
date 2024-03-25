from datetime import date, time
import datetime
from enum import unique
from multiprocessing import connection
from os import name

#from website.auth import appointment
from . import db
from flask_login import UserMixin, current_user
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateField, SelectMultipleField, widgets
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlite3



class Owner(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    nickname=db.Column(db.String(150), unique=True)
    email=db.Column(db.String(150), unique=True)
    password=db.Column(db.String(150))
    first_name=db.Column(db.String(150))
    last_name=db.Column(db.String(150))
    address_full=db.Column(db.String(150))
    mobile=db.Column(db.Integer)
    pets=db.relationship('Pet')
    appointments=db.relationship('Appointment')
    zip_code=db.Column(db.Integer, db.ForeignKey('address.zip_code'))

class Pet(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    type=db.Column(db.String(100))
    breed=db.Column(db.String(100))
    name=db.Column(db.String(100))
    gender=db.Column(db.String(100))
    weight=db.Column(db.Numeric(100))
    dateofbirth=db.Column(db.String(10))
    owner_id=db.Column(db.Integer, db.ForeignKey('owner.id'))
    appointments=db.relationship('Appointment')

class Address(db.Model) : 
    zip_code=db.Column(db.Integer, primary_key=True)
    city=db.Column(db.String(100))
    street=db.Column(db.String(100))
    pets=db.relationship('Owner')

class Service(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    service=db.Column(db.String(1000))
    price=db.Column(db.Numeric(100))
    appointments=db.relationship('Appointment')


class Groomer(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150))
    nickname=db.Column(db.String(150), unique=True)
    password=db.Column(db.String(150))
    appointments=db.relationship('Appointment')

class Appointment(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    owner_id=db.Column(db.Integer, db.ForeignKey('owner.id'))
    pet_id=db.Column(db.Integer, db.ForeignKey('pet.id'))
    service_id=db.Column(db.Integer, db.ForeignKey('service.id'))
    groomer_id=db.Column(db.Integer, db.ForeignKey('groomer.id'))
    date=db.Column(db.String(10))
    time=db.Column(db.String(5))

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

class PetChoiceIterable(object):
    def __iter__(self):
        pets=Pet.query.filter_by(owner_id=current_user.id).all()
        choices=[(pet.id,f'{pet.name}') for pet in pets] 
        for choice in choices:
            yield choice

class BookAppointmentForm(FlaskForm):
    pets=SelectField('Choose pet',coerce=int,choices=PetChoiceIterable())
    date=DateField('Choose date', format="%Y-%m-%d",validators=[DataRequired()])
    time=SelectField('Choose starting time(in 24hr expression)',coerce=int,choices=[(i,i) for i in range(9,19)])
    service=SelectField('Choose service',coerce=int,choices=ServiceChoiceIterable(),option_widget=widgets.CheckboxInput(),widget=widgets.ListWidget(prefix_label=False))
    groomer=SelectField('Choose groomer',coerce=int,choices=GroomerChoiceIterable(),option_widget=widgets.CheckboxInput(),widget=widgets.ListWidget(prefix_label=False))
    submit=SubmitField('Book')
    
    def validate_date(self,date):
        if self.date.data<datetime.datetime.now().date():
            raise ValidationError('You can only book for day after today.')

