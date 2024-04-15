from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ
import logging

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL', 'postgresql://postgres:postgres@flask_db:5432/postgres')
    
  db.init_app(app)

  logging.basicConfig(level=logging.DEBUG)

  class User(db.Model):
    tablename = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)

    def json(self):
      return {'id': self.id, 'username': self.username, 'email': self.email}

  with app.app_context():
    db.create_all()

  @app.route('/')
  def home():
    return jsonify({'message': 'Welcome to the Flask App'})


  @app.route('/users', methods=['POST'])
  def create_user():
    try:
      data = request.get_json()
      new_user = User(username=data['username'], email=data['email'])
      db.session.add(new_user)
      db.session.commit()
      return make_response(jsonify({'message': 'user created'}), 201)
    except Exception as e:
      app.logger.error('Failed to creare user: %s', str(e))
      return make_response(jsonify({'message': 'error creating user'}), 500)


  @app.route('/users', methods=['GET'])
  def get_users():
    try:
      users = User.query.all()
      if len(users):
        return make_response(jsonify([user.json() for user in users]), 200)
      return make_response(jsonify({'message': 'no users found'}), 404)
    except Exception as e:
      return make_response(jsonify({'message': 'error getting users'}), 500)


  @app.route('/users/<int:id>', methods=['GET'])
  def get_user(id):
    try:
      user = User.query.filter_by(id=id).first()
      if user:
        return make_response(jsonify({'user': user.json()}), 200)
      return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
      return make_response(jsonify({'message': 'error getting user'}), 500)


  @app.route('/users/<int:id>', methods=['PUT'])
  def update_user(id):
    try:
      user = User.query.filter_by(id=id).first()
      if user:
        data = request.get_json()
        user.username = data['username']
        user.email = data['email']
        db.session.commit()
        return make_response(jsonify({'message': 'user updated'}), 200)
      return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
      return make_response(jsonify({'message': 'error updating user'}), 500)


  @app.route('/users/<int:id>', methods=['DELETE'])
  def delete_user(id):
    try:
      user = User.query.filter_by(id=id).first()
      if user:
        db.session.delete(user)
        db.session.commit()
        return make_response(jsonify({'message': 'user deleted'}), 200)
      return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
      return make_response(jsonify({'message': 'error deleting user'}), 500)
  

  return app

if __name__ == "__main__":
  app = create_app()
  app.run(host='0.0.0.0', port=8080)