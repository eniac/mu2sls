# uncompyle6 version 3.8.0
# Python bytecode 3.8.10
# Decompiled from: Python 3.8.10 (default, Jun 16 2021, 07:32:00) 
# [GCC 9.3.0]
# Embedded file name: <ast>
from runtime import wrappers
from runtime.knative.invoke import *
from runtime import store_stub
import json
from flask import Flask
from flask import request
app = Flask(__name__)
import hashlib
from uuid import uuid4
import jwt
from compiler import decorators

@decorators.service
class User(object):

    class Wrapperusers:

        def __get__(self, obj, objtype=None):
            value = obj._wrapper_users
            return value

        def __set__(self, obj, value):
            if isinstance(value, wrappers.WrapperTerminal):
                obj._wrapper_users = value
            else:
                obj._wrapper_users._wrapper_set(value)

    users = Wrapperusers()

    def __init__(self, store):
        store.init_env(self.__class__.__name__)
        users_key = 'test-users'
        users_init_val = {}
        self.users = wrappers.wrap_terminal(users_key, users_init_val, store)

    def init_clients(self, clients={}):
        self.ComposeReview_client = clients['ComposeReview']

    def register_with_user_id(self, user_id, first_name, last_name, username, password):
        salt = str(uuid4())
        password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        self.users.update([
         (username,
          {'user_id':user_id, 
           'first_name':first_name, 
           'last_name':last_name, 
           'username':username, 
           'password':password, 
           'salt':salt})])

    def register_user(self, first_name, last_name, username, password):
        self.register_with_user_id(str(uuid4()), first_name, last_name, username, password)

    def login(self, username, password):
        user = self.users.get(username)
        hashpass = hashlib.sha256((password + user['salt']).encode('utf-8')).hexdigest()
        if hashpass != user['password']:
            return
        return jwt.encode({'user_id': user['user_id']}, 'secret', algorithm='HS256')

    def upload_user(self, req_id, username):
        user = self.users.get(username)
        promise = AsyncInvoke(self.ComposeReview_client, 'upload_user_id', req_id, user['user_id'])
        Wait(promise)


instance = User(store_stub.Store())
instance.init_clients({k:k for k in ('CastInfo', 'ComposeReview', 'Frontend', 'MovieId',
                                     'MovieInfo', 'MovieReview', 'Page', 'Plot',
                                     'Rating', 'ReviewStorage', 'Text', 'UniqueId',
                                     'User', 'UserReview')})

@app.route('/register_with_user_id', methods=['GET', 'POST'])
def register_with_user_id():
    return json.dumps((instance.register_with_user_id)(**request.args.to_dict()))


@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    return json.dumps((instance.register_user)(**request.args.to_dict()))


@app.route('/login', methods=['GET', 'POST'])
def login():
    return json.dumps((instance.login)(**request.args.to_dict()))


@app.route('/upload_user', methods=['GET', 'POST'])
def upload_user():
    return json.dumps((instance.upload_user)(**request.args.to_dict()))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=(int(os.environ.get('PORT', 8080))))