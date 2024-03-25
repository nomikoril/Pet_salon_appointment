#from crypt import methods
from datetime import date
from random import choices
from flask import Blueprint, jsonify, render_template, flash,  jsonify, request
from flask_login import  login_required,  current_user
from numpy import append

from .models import Appointment, Groomer, Pet, Service
from .models import Owner

from . import db
import json
import pandas as pd

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/delete-pet', methods=['POST'])
def delete_pet():
    pet=json.loads(request.name)
    petId=pet['petId']
    pet=Pet.query.get(petId)
    if pet:
        if pet.owner_id == current_user.id:
            db.session.delete(pet)
            db.session.commit()
    return jsonify({})
 

