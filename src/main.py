"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, json, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from models import Contact

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/contact/all', methods=['GET'])
def get_contacts():
    # Select all entries from Contact table with flask_sqlalchemy
    # Put them inside a list variable
    contacts = Contact.query.all()
    # Check if theres any parameters in the URL to filter the list
    name = request.args.get("full_name")
    if name is not None:
        filtered_contacts = filter(lambda contact : full_name in contact.full_name, contacts)
        name = request.args.get("name")
    else:
        filtered_contacts = contacts
    # Serialize every object of the list to make a dictionary
    serialized_contacts = list(map(lambda contact: contact.serialize(), filtered_contacts))
    print(serialized_contacts)
    # return serialized lis and 200-OK
    return jsonify(serialized_contacts), 200   


@app.route('/contact', methods=['POST'])
def add_contact():
    contact_info = request.json

    new_contact = Contact.create(
        contact_info['full_name'],
        contact_info['email'],
        contact_info['phone'],
        contact_info['address']
        # contact_info['groups']
    )
    
    db.session.add(new_contact)
    try:
        db.session.commit()
        # serialize contact and return 201
        return f"{contact_info['full_name']} added succesfully", 201
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        # return error
        return jsonify({
            "resultado": f"{error.args}"
        }), 500

@app.route('/contact/<int:contact_id>', methods=['GET'])
def get_single_contact(contact_id):
    contact = [contact for contact in contacts if contact['id'] == contact_id]
    return jsonify(contact)

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
