from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/seedinsight'
db = SQLAlchemy(app)

class Seed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100), nullable=False)
    # Add more fields as needed

@app.route('/seeds', methods=['POST'])
def add_seed():
    data = request.json
    name = data['name']
    variety = data['variety']
    # Add more fields as needed
    new_seed = Seed(name=name, variety=variety)
    db.session.add(new_seed)
    db.session.commit()
    return jsonify({'message': 'Seed added successfully'}), 201

@app.route('/seeds', methods=['GET'])
def get_seeds():
    seeds = Seed.query.all()
    seed_list = [{'name': seed.name, 'variety': seed.variety} for seed in seeds]
    return jsonify(seed_list), 200

if __name__ == '__main__':
    app.run(debug=True)

