import time
import os
from flask import Flask, jsonify, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
from passlib.hash import pbkdf2_sha512
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path="")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rmpy.db')
auth = HTTPBasicAuth()
db = SQLAlchemy(app)


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String)
    email = db.Column(db.String)
    role = db.Column(db.String)
    datecreated = db.Column(db.String)

    def __init__(self, name, password, email, role):
        self.name = name
        self.password = password
        self.email = email
        self.role = role
        self.datecreated = time.time()

    def _asdict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result


class Server(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    public = db.Column(db.Boolean)
    owner = db.Column(db.String)
    game = db.Column(db.String)
    plugins = db.Column(db.String)
    datecreated = db.Column(db.String)

    def __init__(self, name, public, owner, game, plugins):
        self.name = name
        self.public = public
        self.owner = owner
        self.game = game
        self.plugins = plugins
        self.datecreated = time.time()

    def _asdict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

db.create_all()


@auth.verify_password
def verify_password(username, password):
    return pbkdf2_sha512.verify(password, User.query.filter_by(name=username).first().password)


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found404(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/rmpy/api/v1.0/servers', methods=['GET'])
def get_servers():
    if auth.username() and User.query.filter_by(name=auth.username()).first().role == "admin":
        servers = Server.query.all()
    else:
        servers = []
        servers += Server.query.filter_by(owner=auth.username(), public=False).all()
        servers += Server.query.filter_by(public=True).all()
    return make_response(jsonify(data=[a._asdict() for a in servers]))


@app.route('/rmpy/api/v1.0/servers', methods=['POST'])
@auth.login_required
def add_server():
    server = Server(
        name=request.form["name"],
        public=request.form["public"],
        owner=auth.username(),
        game=request.form["game"],
        plugins=request.form["plugins"]
    )
    db.session.add(server)
    db.session.commit()
    return make_response(jsonify(data=server))


@app.route('/rmpy/api/v1.0/servers/<string:serverId>', methods=['DELETE'])
@auth.login_required
def delete_server(serverId):
    try:
        server = Server.query.filter_by(uid=serverId).first()
        if server.owner != auth.username():
            if User.query.filter_by(name=auth.username()).first().password != "admin":
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        db.session.delete(server)
        db.session.commit()
        return make_response(jsonify(servers=[a._asdict() for a in Server.query.all()]))
    except:
        return make_response(jsonify({'error': 'couldn\'t delete server'}), 400)


@app.route('/rmpy/api/v1.0/users', methods=['GET'])
@auth.login_required
def get_users():
    if User.query.filter_by(name=auth.username()).first().role != "admin":
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    users = [a._asdict() for a in User.query.all()]
    for user in users:
        i = users.index(user)
        del user["password"]
        users[i] = user
    return make_response(jsonify(users=users))


@app.route('/rmpy/api/v1.0/users', methods=['POST'])
@auth.login_required
def add_user():
    if User.query.filter_by(name=auth.username()).first().role != "admin":
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    if User.query.filter_by(name=request.form["username"]).first():
        return make_response(jsonify({'error': 'username taken'}), 400)
    user = User(
        request.form["username"],
        pbkdf2_sha512.encrypt(request.form["password"]),
        request.form["email"],
        request.form["role"])
    db.session.add(user)
    db.session.commit()
    return make_response(jsonify(users=user._asdict()))


@app.route('/rmpy/api/v1.0/users', methods=['DELETE'])
@auth.login_required
def delete_user():
    if User.query.filter_by(name=auth.username()).first().role != "admin":
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    user = User.query.filter_by(name=request.form["username"])
    db.session.delete(user)
    db.session.commit()
    return make_response(jsonify(users=[a._asdict() for a in User.query.all()]))


@app.route('/rmpy/api/v1.0/users', methods=['PUT'])
@auth.login_required
def update_user():
    if User.query.filter_by(name=auth.username()).first().role != "admin":
        if auth.username() == request.form["username"]:
            request.form["role"] = "user"
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    allowed_keys = ["email", "username", "password", "role"]
    for key in request.form.keys():
        if key not in allowed_keys:
            return make_response(jsonify({'error': 'illegal key provided'}), 400)
    user = User.query.filter_by(name=request.form["username"]).first()
    if request.form.get("password", False):
        request.form["password"] = pbkdf2_sha512.encrypt(request.form["password"])
    user.update(request.form)
    db.session.commit()
    return make_response(jsonify(users=[a._asdict() for a in User.query.all()]))

if __name__ == '__main__':
    app.run(debug=True)
