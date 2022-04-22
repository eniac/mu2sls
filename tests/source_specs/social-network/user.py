import hashlib
from uuid import uuid4
import jwt

from compiler import decorators

@decorators.service
class User(object):
    def __init__(self):
        ## Maybe it needs to be keyed on something else other than username
        self.users = {} # type: Persistent[dict]

    def register_user_with_id(self, req_id: int, 
                                    first_name: str, 
                                    last_name: str, 
                                    username: str, 
                                    password: str,
                                    user_id: int):
        if(username in self.users.keys()):
            ## Error, user exists
            ## TODO: Can we throw error?
            pass

        
        salt = str(uuid4())
        password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        self.users.update([(username, {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': password,
            'salt': salt
        })])

        ## Add to social graph
        SyncInvoke('SocialGraph', "insert_user", req_id, user_id)


    def register_user(self, first_name, last_name, username, password):
        self.register_user_with_id(uuid4(), first_name, last_name, username, password)

    def compose_creator_with_user_id(self, req_id: int,
                                           user_id: int,
                                           username: str):

        creator = {
            'username': username,
            'user_id': user_id
        }

        return creator

    def compose_creator_with_username(self, req_id: int,
                                            username: str):

        ## TODO: Normally, this first checks to find the user_id in memcached.
        ##       We need to investigate whether we can also have some cache here.

        ## In DeathstarBench this was duplicated... but it is the same as get_user_id
        # if(not username in self.users.keys()):
        #     ## Error
        #     return None

        # user = self.users.get(username)
        # user_id = user['user-id']
        user_id = self.get_user_id(req_id, username)

        creator = self.compose_creator_with_user_id(req_id, user_id, username)

        ## TODO: If we had a cache, we would also update that.

        return creator

    def login(self, req_id: int,
                    username: str, 
                    password: str):

        ## TODO: Normally, this first checks to find the user_id in memcached.
        ##       We need to investigate whether we can also have some cache here.
        
        user = self.users.get(username)
        hashpass = hashlib.sha256((password + user['salt']).encode('utf-8')).hexdigest()
        if hashpass != user['password']:
            return None
        ## This encoding is not exactly the same as in DeathstarBench but it is the
        ## same as in our implementation of media-service
        return jwt.encode({'user_id': user['user_id']}, 'secret', algorithm='HS256')

    def get_user_id(self, req_id: int,
                          username: str) -> int:

        ## TODO: Normally, this first checks to find the user_id in memcached.
        ##       We need to investigate whether we can also have some cache here.
        
        if(not username in self.users.keys()):
            ## Error
            return None

        user = self.users.get(username)
        user_id = user['user-id']
        return user_id
