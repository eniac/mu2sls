import time
import logging
import hashlib
from uuid import uuid4
import jwt

from compiler import decorators

@decorators.service
class User(object):
    def __init__(self):
        self.users = {} # type: Persistent[dict]

    def register_with_user_id(self, user_id, first_name, last_name, username, password):
        salt = str(uuid4())
        password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        self.users[username] = {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': password,
            'salt': salt
        }

    def register_user(self, first_name, last_name, username, password):
        self.register_with_user_id(str(uuid4()), first_name, last_name, username, password)

    def login(self, username, password):
        user = self.users[username]
        hashpass = hashlib.sha256((password + user['salt']).encode('utf-8')).hexdigest()
        if hashpass != user['password']:
            return None
        ret = {'user_id': user['user_id']}
        ## TODO: It is not possible to JSON decode this, so we just return the internal dic
        # return jwt.encode(ret, 'secret', algorithm='HS256')
        return ret


    async def upload_user(self, req_id, username):
        start = time.perf_counter_ns()
        user = self.users[username]
        promise = AsyncInvoke('ComposeReview', "upload_user_id", req_id, user['user_id'])
        ## TODO: DAG doesn't wait here
        await Wait(promise)
        end = time.perf_counter_ns()
        duration = (end - start) / 1000000
        logging.error(f'APP User.upload_user: {duration}')
