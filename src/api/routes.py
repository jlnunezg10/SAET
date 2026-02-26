"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta, timezone, datetime

api = Blueprint('api', __name__)

bcrypt = Bcrypt()

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


# Ruta para crear un nuevo usuario

@api.route('/create-user', methods=['POST'])
def create_user():
    try:
        
        data = request.get_json()
        
        name = data.get("name")
        user = data.get("user")
        password = data.get("password")
        role = data.get("role")
        email = data.get("email")
        
        if not name or not user or not password or not role:
            return jsonify({'msg':'Datos incompletos'}), 402
        
        
        validate_user = User.query.filter_by(user=user).first()
        
        if validate_user:
            return (
                jsonify(
                    {
                        "msg": "El email utilizado ya esta registrado, por favor utilizar otro"
                    }
                ),
                400,
            )
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(name=name, password=password_hash,user=user,email=email, role=role)
        
        db.session.add(new_user)
        db.session.flush()
        
        db.session.commit()

        return jsonify(new_user.serialize()), 201
    
        
        
    except Exception as e:
        return jsonify({"msg": f"El siguiente error acaba de ocurrir: {e}"}), 500





# Ruta para Loguear un usuario
@api.route('/login',methods = ['POST'])
def login():
    try:
        
        data = request.get_json()
        user = data.get("user")
        password = data.get("password")
        
        if not user or not password:
            return jsonify({'msg':"Faltan los datos de user o password"}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'msg':'Usuario no encontrado'})
        
        password_db = user.password
        
        true_false = bcrypt.check_password_hash(password_db, password)
        if true_false:
            expires = timedelta(days=1)
            user_id = user.id
            user_role = user.role

            access_token = create_access_token(
                identity=str(user_id),
                expires_delta=expires,
                additional_claims={"role": user_role},
            )

            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            return(
                jsonify(
                    {"msg":"Login exitoso", "access_token": access_token}
                ), 203,
            )
            
        else:
            return jsonify({'msg':"contraseña incorrecta"}), 401
         

            
    except Exception as e:
            return jsonify({"msg": f"El siguiente error acaba de ocurrir: {e}"}), 503
