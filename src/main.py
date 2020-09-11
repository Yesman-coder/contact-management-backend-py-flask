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
from models import Contact, Group

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

# -------------GET ALL THE EXISTING CONTACT OBJECTS-----------------------

@app.route('/contact/all', methods=['GET'])
def get_contacts():
    # Select all entries from Contact table with flask_sqlalchemy
    # Put them inside a list variable
    contacts = Contact.query.all()
    # Check if theres any parameters in the URL to filter the list
    name = request.args.get("full_name")
    if name is not None:
        filtered_contacts = filter(lambda contact : full_name in contact.full_name, contacts)
    else:
        filtered_contacts = contacts
    # Serialize every object of the list to make a dictionary
    serialized_contacts = list(map(lambda contact: contact.serialize(), filtered_contacts))
    print(serialized_contacts)
    # return serialized lis and 200-OK
    return jsonify(serialized_contacts), 200   

# -------------CREATE A NEW CONTACT-----------------------

@app.route('/contact', methods=['POST'])
def add_contact():
    contact_info = request.json
    new_contact = Contact.create(
        contact_info['full_name'],
        contact_info['email'],
        contact_info['address'],
        contact_info['phone']
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

# -------------GET A CONTACT OBJECTS BY ITS ID-----------------------

@app.route('/contact/<contact_id>', methods=['GET'])
def get_single_contact(contact_id):
        contact = Contact.query.get(contact_id)
        if isinstance(contact, Contact):
            return jsonify(contact.serialize()), 200
        else:
            return jsonify({"result": f"No match found {error.args}"}), 404

# -------------DELETE A CONTACT OBJECT BY ITS ID-----------------------

@app.route('/contact/<contact_id>', methods=['DELETE'])
def delete_single_contact(contact_id):
    contact = Contact.query.get(contact_id)
    if contact is None:
     raise APIException('Contact not found', status_code=404)

    db.session.delete(contact)
    try:
        db.session.commit()
        return jsonify({"result": "deleted succesfully"}), 204
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        return jsonify({
            "resultado": f"{error.args}"
        }), 500

# -------------UPDATES INFORMATION OF A CONTACT-----------------------

@app.route('/contact/<contact_id>', methods=['PATCH'])
def update_contact(contact_id):
    contact = Contact.query.get(contact_id)
    dictionary = request.get_json()
    contact.update_contact(dictionary)
    try:
        db.session.commit()
        # devolver el donante serializado y jsonificado. Y 200 
        return jsonify(contact.serialize()), 200
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        return jsonify({
            "resultado": f"{error.args}"
        }), 500

# -------------CREATE A NEW GROUP-----------------------

@app.route('/group', methods=['POST'])
def add_group():
    group_info = request.json
    new_group = Group.create_group(
        group_info["group_name"]
    )   
    db.session.add(new_group)
    try:
        db.session.commit()
        # serialize contact and return 201
        return f"{group_info['group_name']} group added succesfully", 201
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        # return error
        return jsonify({
            "result": f"{error.args}"
        }), 500

# -------------GET ALL THE EXISTING GROUP OBJECTS-----------------------

@app.route('/group/all', methods=['GET'])
def get_groups():
    groups = Group.query.all()
    name = request.args.get("group_name")
    if name is not None:
        filtered_groups = filter(lambda group : group_name in group.group_name, groups)
    else:
        filtered_groups = groups
  
    serialized_groups = list(map(lambda group: group.serialize(), filtered_groups))
    print(serialized_groups)

    return jsonify(serialized_groups), 200 

# -------------GET A GROUP OBJECTS BY ITS ID-----------------------

@app.route('/group/<group_id>', methods=['GET'])
def get_single_group(group_id):
        group = Group.query.get(group_id)
        if isinstance(group, Group):
            return jsonify(group.serialize()), 200
        else:
            return jsonify({"result": f"No match found {error.args}"}), 404

# -------------DELETE A GROUP OBJECT BY ITS ID-----------------------

@app.route('/group/<group_id>', methods=['DELETE'])
def delete_single_group(group_id):
    group = Group.query.get(group_id)
    if group is None:
     raise APIException('Group not found', status_code=404)

    db.session.delete(group)

    try:
        db.session.commit()
        return jsonify({"result" : "Group has been eliminated"}), 204
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        return jsonify({
            "resultado": f"{error.args}"
        }), 500
        
# -------------UPDATES INFORMATION OF A GROUP-----------------------

@app.route('/group/<group_id>', methods=['PATCH'])
def update_group(group_id):
    group = Group.query.get(group_id)
    dictionary = request.get_json()
    group.update_group(dictionary)
    try:
        db.session.commit()
        # devolver el donante serializado y jsonificado. Y 200 
        return jsonify(group.serialize()), 200
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        return jsonify({
            "resultado": f"{error.args}"
        }), 500



if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
