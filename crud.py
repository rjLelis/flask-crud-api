from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os
import sqlalchemy.exc as db_exceptions

app = Flask(__name__)

cors = CORS(app, resources={
    r"/user/*": {
        "origin": "*"
    }
})

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'crud.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email


class UserSchema(ma.Schema):
    class Meta():
        fields = ('id', 'username', 'email')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/user', methods=['POST'])
def add_user():
    username = request.json['username']
    email = request.json['email']

    new_user = User(username, email)

    try:
        db.session.add(new_user)
        db.session.commit()
    except db_exceptions.IntegrityError as e:
        return jsonify(message='username or email already stored'), 409

    return user_schema.jsonify(new_user), 201


@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    return users_schema.jsonify(all_users)


@app.route('/user/<int:id>', methods=['GET'])
def user_detail(id):
    user = User.query.get(id)

    if user is None:
        return jsonify(message=f'User not found with id {id}'), 404
    return user_schema.jsonify(user)


@app.route('/user/<int:id>', methods=['PUT'])
def user_update(id):
    user = User.query.get(id)

    if user is None:
        return jsonify(message=f'User not found with id {id}'), 404

    user.username = request.json['username']
    user.email = request.json['email']

    try:
        db.session.commit()
    except db_exceptions.IntegrityError:
        return jsonify(message='username or email already stored')

    return user_schema.jsonify(user)


@app.route('/user/<int:id>', methods=['DELETE'])
def user_delete(id):
    user = User.query.get(id)

    if user is None:
        return jsonify(message=f'User not found with id {id}'), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify(message=f'User with id {id} was deleted'), 204


if __name__ == "__main__":
    app.run(debug=True)
