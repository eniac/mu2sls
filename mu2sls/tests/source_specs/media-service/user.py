import hashlib
from uuid import uuid4
import jwt

from compiler import decorators

@decorators.service
class User(object):
    def __init__(self):
        self.users = {"a": "b"} # type: Persistent[dict]

    def register_with_user_id(self, user_id, first_name, last_name, username, password):
        salt = str(uuid4())
        password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        print(type(self.users))
        self.users.username = {
        # self.users.update([(username, {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': password,
            'salt': salt
        }
        # })])

    def register_user(self, first_name, last_name, username, password):
        self.register_with_user_id(str(uuid4()), first_name, last_name, username, password)

    def login(self, username, password):
        user = self.users.get(username)
        hashpass = hashlib.sha256((password + user['salt']).encode('utf-8')).hexdigest()
        if hashpass != user['password']:
            return None
        return jwt.encode({'user_id': user['user_id']}, 'secret', algorithm='HS256')

    def upload_user(self, req_id, username):
        user = self.users.get(username)
        promise = AsyncInvoke('ComposeReview', "upload_user_id", req_id, user['user_id'])
        ## TODO: DAG doesn't wait here
        Wait(promise)
