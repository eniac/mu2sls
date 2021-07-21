## This file contains the goal of what our compiler should produce.

class Client:
    def request():
        return "hi"

def init_thrift_client():
    return Client()

class Handler:
    def __init__(self):
        pass

    ###############################################################################

    ## The following function implements the getter for collection
    # self.collection = [] # type: Persistent[list]
    ##
    ## TODO: It is infuiriatingly naive, since for every load(!) it calls beldi get.
    ##       There needs to be some caching behavior here.
    @property
    def collection(self):
        ret = beldi.get('collection')
        return ret

    ## TODO: Do we ever need to set for non-primitive types?
    ##       This is something that we need to investigate. Changes in python
    ##       happen most of the time when calling object methods, and not when setting.
    ##       This means that we need to:
    ##         1. Update Beldi 'collection' whenever a method on it is called.
    ##         2. Develop concurrent versions of non-primitive data structures 
    ##            that can be used in place of the normal ones.
    ##         3. Update Beldi 'collection' in the end too.
    @collection.setter
    def collection(self, collection):
        beldi.set('collection', collection)
        ## TODO: For non-primitives we need to raise an exception when setting.
        ##
        ## It should be illegal. We should only allow setting through methods.

    ###############################################################################

    # self.counter = 0 # type: Persistent[int]
    @property
    def counter(self):
        ret = beldi.get('counter')
        return ret

    @counter.setter
    def counter(self, counter):
        beldi.set('counter', counter)

    ###############################################################################

    def client_init(self):
        self._client = init_thrift_client()
        self.init_fields['client'] = True

    ## Thrift client only has a getter
    # self.client = init_thrift_client() # type: ThriftClient
    @property
    def client(self):
        if(not ('client' in self.init_fields
                and self.init_fields['client'])):
            self.client_init()
        return self._client

    ## Note: There is no setter for Thrift client

    ###############################################################################


    def ComposeUrls(self, req_id, urls, carrier):
        logging.debug("Processing request: " + str(req_id))
        
        ## TODO: Even this is not doable easily!!!!
        self.counter += 1

        target_urls = []
        for url in urls:
            ## TODO: NonDeterministic!!!!
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=10))
            short_url = "http://short-url/" + random_suffix
            target_url = ttypes.Url(shortened_url=short_url, expanded_url=url)
            target_urls.append(target_url)

        ## TODO: Make this a bulk insert
        for target_url in target_urls:
            logging.debug("Dealing with url: " + str(target_url))
            url_object = {"shortened_url": target_url.shortened_url,
                            "expanded_url": target_url.expanded_url}
            self.collection.append(url_object)
        
        ## We can identify those (and handle them) automatically
        self.client.request()

        return target_urls