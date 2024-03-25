#from curses import meta
from hashlib import new
from itertools import count
from multiprocessing import connection
from threading import currentThread
from flask import Blueprint, render_template, flash,  request, redirect, session, url_for
from numpy import append
from website import views
from .models import Appointment
from .models import Groomer
from .models import Owner
from .models import Address
from .models import Pet
from .models import Service
from .models import BookAppointmentForm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateField, SelectMultipleField, widgets
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from sqlalchemy import func
from sqlalchemy import desc
from sqlalchemy import asc
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

import pandas as pd
import sqlite3


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        nickname=request.form.get('nickname')
        password=request.form.get('password')

        user=Owner.query.filter_by(nickname=nickname).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Owner logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Nickname does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        city=request.form.get('city')
        street=request.form.get('street')
        zip_code=request.form.get('zip_code')
        nickname=request.form.get('nickname')
        password1=request.form.get('password1')
        password2=request.form.get('password2')

        user=Owner.query.filter_by(nickname=nickname).first()
        
        if user:
            flash('Nickname already exists', category='error')
        elif len(email)<4:
            flash('Email must be greater than 4 characters.', category='error')
            pass
        elif password1!=password2:
            flash('Passwords doesn\'t match.', category='error')
            pass
        elif len(password1)<7:
            flash('Password must be at least 7 characters.', category='error')
        else : 
            new_user=Owner(first_name=first_name, last_name=last_name, mobile=mobile,  email=email, nickname=nickname, zip_code=zip_code , password=generate_password_hash(password1, method='sha256') )
            db.session.add(new_user)
            db.session.commit()
            new_address=Address(zip_code=zip_code, city=city, street=street )
            db.session.add(new_address)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('auth.login'))

    return render_template("signup.html", user=current_user)


@auth.route('/petregister', methods=['GET', 'POST'])
@login_required
def petregister():
    if request.method=='POST':
        name = request.form.get('name')
        dateofbirth= request.form.get('dateofbirth')
        type= request.form.get('type')
        breed= request.form.get('breed')
        gender= request.form.get('gender')
        weight= request.form.get('weight')
        if  len(name)<1:
            flash('Name is to short!', category='error')
        else:
            new_pet=Pet(name=name, dateofbirth=dateofbirth, type=type, breed=breed, gender=gender, weight=weight, owner_id=current_user.id)
            db.session.add(new_pet)
            db.session.commit()
            flash('New pet added!', category='success')
    return render_template("petregister.html", user=current_user)

@auth.route('/appointments',methods=['GET','POST'])
@login_required
def appointments():
    form=BookAppointmentForm()
   
    if request.method=='POST':
           
        pet_id=request.form.get('pets')
        service_id=request.form.get('service')
        groomer_id=request.form.get('groomer')
        date= request.form.get('date')
        time= request.form.get('time')     
        appointment=Appointment(pet_id=pet_id, service_id=service_id, groomer_id=groomer_id, date=date, time=time, owner_id=current_user.id)
        db.session.add(appointment)
        db.session.commit()
        flash('Booking success!', category='success')
        return redirect(url_for('views.home'))
    return render_template('appointment.html',title='Appointment Booking',form=form, user=current_user)


@auth.route('/booked', methods=['GET'])
@login_required
def booked():
    bookings = db.session.query(Appointment.id, Appointment.date, Appointment.time, Owner.id.label("owner_id"), Pet.name.label("pet_name"), Pet.breed.label("breed"), Service.service.label("service"), Groomer.name.label("groomer"))\
        .outerjoin(Service).outerjoin(Groomer).outerjoin(Pet).outerjoin(Owner)\
            .filter(Appointment.owner_id==current_user.id).all()
  
    return render_template('bookedappointment.html', appointments=bookings, user=current_user)


@auth.route('/fee')
@login_required
def fee():
    services=Service.query.all()
    return render_template('services.html', services=services, user=current_user)

@auth.route('/dashboard', methods=['GET'])
def dashboard():
    top_appointment = db.session.query(Owner.first_name.label("first_name"), func.count(Appointment.id).label("count")).outerjoin(Owner).group_by(Owner.first_name).order_by(desc(func.count(Appointment.id))).limit(3)
    top_pets = db.session.query(Owner.first_name.label("first_name"), func.count(Pet.id).label("count")).outerjoin(Owner).group_by(Owner.first_name).order_by(desc(func.count(Pet.id))).limit(3)
    daily = db.session.query(Appointment.date.label("date"), func.count(Appointment.id).label("count")).group_by(Appointment.date).order_by(asc(Appointment.date)).all()
    pet_type = db.session.query(Pet.type.label("type"), func.count(Pet.id).label("count")).group_by(Pet.type).order_by(desc(func.count(Pet.id))).all()
    return render_template('dashboard.html', top_appointment=top_appointment,top_pets=top_pets, daily=daily,  pet_type=pet_type,   user=current_user)