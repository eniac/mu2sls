import decorators

class Client:
    def request():
        return "hi"

def init_thrift_client():
    return Client()

## Q: Maybe there is a better way to identify services (as a subclass)?
@decorators.service
class Handler:
    ## Question: Should we allow any argument in the init? 
    ##           Probably not, because we wouldn't know how to get them
    ##
    ## In contrast, by having well defined initialization functions for each field, we can
    ## call them on demand.
    ##
    ## That way, they can depend on environment variables or files,
    ##   which we can copy in the container.
    def __init__(self):
        ## This is a simple primitive persistent object that tracks how many requests have been processed for statistics.
        self.counter = 0 # type: Persistent[int]

        ## This contains a list/set of short-long url pairs
        self.collection = [] # type: Persistent[list]

        ## Represents a Thrift client 
        self.client = init_thrift_client() # type: ThriftClient
    
    ## Decision: Either do initializations in init or in separate functions
    ##
    ## Decision: Either do annotations in type comments, or in a function or field of the handler that contains
    ##           the external call names, and the persistent field names.

    def ComposeUrls(self, req_id, urls, carrier):
        logging.debug("Processing request: " + str(req_id))
        self.counter += 1

        target_urls = []
        for url in urls:
            ## NonDeterministic!!!!
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