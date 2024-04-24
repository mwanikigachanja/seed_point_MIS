from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/seedinsight'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password'}), 401
    token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'message': 'Login successful', 'token': token}), 200

@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': 'You are authorized'}), 200

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({'username': current_user.username}), 200

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.json
    current_user.username = data.get('username', current_user.username)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)

