import datetime

from compiler import decorators

@decorators.service
class SocialGraph(object):
    def __init__(self):
        self.followees = {} # type: Persistent[dict]
        ## TODO: Maybe make this (and the one below) a dict of dicts 
        ##       instead of a dict of lists

        self.followers = {} # type: Persistent[dict]
        # self.users = {} # type: Persistent[dict]
        pass

    ## TODO: Everything here needs transactions
    def add_followee(self, user_id: int,
                              followee_id: int,
                              timestamp):
        ## Update followees
        user_followees = self.followees.get(user_id, default = [])

        ## If the followee doesn't already exist
        if not any([followee['user-id'] == followee_id for followee in user_followees]):
            user_followees.append({
                'user-id': followee_id,
                'timestamp': timestamp
            })
            self.followees.update([(user_id, user_followees)])

    def add_follower(self, user_id: int,
                              followee_id: int,
                              timestamp):
        ## Update followees
        followee_followers = self.followers.get(followee_id, default = [])

        ## If the followee doesn't already exist
        if not any([follower['user-id'] == user_id for follower in followee_followers]):
            followee_followers.append({
                'user-id': user_id,
                'timestamp': timestamp
            })
            self.followers.update([(followee_id, followee_followers)])

    def follow(self, req_id: int, 
                     user_id: int,
                     followee_id: int):
        ## TODO: They also allow for async calls to the DB
        ##       In the deathstar bench implementation, all three state accesses
        ##       happen concurrently. Could we investigate such an optimization?
        
        ## The original implementation saves the followers in both redis and mongo (?)
        ## TODO: Investigate why they do that and whether it is useful.

        timestamp = datetime.datetime.now()

        ## TODO: The original implementation doesn't have a transaction,
        ##       but maybe we should.

        ## Update followees
        self.add_followee(user_id, followee_id, timestamp)

        ## Update followers
        self.add_follower(user_id, followee_id, timestamp)


    def remove_followee(self, user_id: int,
                              followee_id: int):
        ## Update followees
        user_followees = self.followees.get(user_id, default = [])

        ## Remove the follower
        new_user_followees = [followee for followee in user_followees
                                  if not followee['user-id'] == followee_id]
        self.followees.update([(user_id, new_user_followees)])

    def remove_follower(self, user_id: int,
                              followee_id: int):
        ## Update followees
        followee_followers = self.followers.get(followee_id, default = [])

        ## Remove the follower
        new_followee_followers = [follower for follower in followee_followers
                                  if not follower['user-id'] == user_id]
        self.followers.update([(followee_id, new_followee_followers)])


    def unfollow(self, req_id: int, 
                     user_id: int,
                     followee_id: int):
        ## TODO: The same concerns that apply to follow also apply here

        ## Update followees
        self.remove_followee(user_id, followee_id)

        ## Update followers
        self.remove_follower(user_id, followee_id)

    def get_followers(self, req_id: int,
                            user_id: int):
        followers = self.followers.get(user_id, default = [])
        return followers

    def get_followees(self, req_id: int,
                            user_id: int):
        followees = self.followees.get(user_id, default = [])
        return followees

    def insert_user(self, req_id: int,
                          user_id: int):
        ## Initialize user if it doesn't exist
        ##
        ## NOTE: Could also be done with transaction
        self.followers.setdefault(user_id, default=[])
        self.followees.setdefault(user_id, default=[])

    def follow_with_username(self, req_id: int,
                                   username: str,
                                   followee_name: str):
        ## TODO: Ideally, these should be Async calls, but since they are to the same
        ##       service, maybe we have an issue with our model?
        user_id = SyncInvoke('User', "get_user_id", req_id, username)
        followee_id = SyncInvoke('User', "get_user_id", req_id, followee_name)

        if user_id is not None and followee_id is not None:
            self.follow(req_id, user_id, followee_id)

    def unfollow_with_username(self, req_id: int,
                                     username: str,
                                     followee_name: str):
        ## TODO: Ideally, these should be Async calls, but since they are to the same
        ##       service, maybe we have an issue with our model?
        user_id = SyncInvoke('User', "get_user_id", req_id, username)
        followee_id = SyncInvoke('User', "get_user_id", req_id, followee_name)

        if user_id is not None and followee_id is not None:
            self.unfollow(req_id, user_id, followee_id)