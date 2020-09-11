from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False) 

    # subscriptions = db.relationship("Subscription", backref="contact")

    def __init__(self, full_name, email, address, phone):
        """creates an instance of this class"""
        self.full_name = full_name
        self.email = email
        self.address = address
        self.phone = phone
    
    def __repr__(self):
        return '<Contact %r>' % self.full_nam

    def serialize(self):
        """returns a dictionary with data from the object"""
        return{
            "id": self.id,
            "full name" : self.full_name,
            "email" : self.email,
            "address" : self.address,
            "phone" : self.phone
            # "groups" : [subscription.serialize() for subscription in self.subscriptions]
        }
    
    @classmethod
    def create(cls, full_name, email, address, phone):
        """
            normaliza insumos nombre y apellido,
            crea un objeto de la clase Contact con
            esos insumos y devuelve la instancia creada.
        """
        new_contact = cls(
            full_name,
            email,
            address,
            phone
        )
        return new_contact
    
    def update_contact(self, dictionary):
        """updates properties of a specific instance of Contact"""
        for (key, value) in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return True

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def __init__(self, contact_id,  group_id):
        """creates an instance of this class"""
        self.contact_id = contact_id
        self.group_id = group_id

    def serialize(self):
        """returns a dictionary with data from the object"""
        return {
            "id" : self.id,
            "contact_id" : self.contact_id,
            "group_id" : self.groupd_id
        }

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(20), unique=True, nullable=False)

    subscriptions = db.relationship("Subscription", backref="groups")

    def __init__(self, group_name):
        self.group_name = group_name 

    def __repr__(self):
        return '<Group %r>' % self.name     

    def serialize(self):
        """returns a dictionary with data from the object"""
        return {
            "id" : self.id,
            "group_name" : self.group_name,
        }
    @classmethod
    def create_group(cls, group_name):
        """
            crea un objeto de la clase Group y devuelve la instancia creada.
        """
        new_group = cls(
            group_name
        )
        return new_group
    
    def update_group(self, dictionary):
        """updates properties of a specific instance of Group"""
        for (key, value) in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return True
