from sqlalchemy.orm import validates

from project import db, app
from project.validators import validate_text, validate_age


# Customer model
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    city = db.Column(db.String(64))
    age = db.Column(db.Integer)

    def __init__(self, name, city, age):
        self.name = name
        self.city = city
        self.age = age

    # Walidatory uruchamiane przy tworzeniu i przy edycji klienta.
    @validates('name')
    def _check_name(self, key, value):
        return validate_text(value, 'Name')

    @validates('city')
    def _check_city(self, key, value):
        return validate_text(value, 'City')

    @validates('age')
    def _check_age(self, key, value):
        return validate_age(value)

    def __repr__(self):
        return f"Customer(ID: {self.id}, Name: {self.name}, City: {self.city}, Age: {self.age})"


with app.app_context():
    db.create_all()
