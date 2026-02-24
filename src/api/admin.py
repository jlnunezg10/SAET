  
import os
from flask_admin import Admin
from .models import db, User,Department,Permit,Station,Region,ContactStation,Market,PersonalInfo,Contractor
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin')

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Department, db.session))
    admin.add_view(ModelView(Permit, db.session))
    admin.add_view(ModelView(Station, db.session))
    admin.add_view(ModelView(Region, db.session))
    admin.add_view(ModelView(ContactStation, db.session))
    admin.add_view(ModelView(Market, db.session))
    admin.add_view(ModelView(PersonalInfo, db.session))
    admin.add_view(ModelView(Contractor, db.session))
    

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))