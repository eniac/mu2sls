from compiler import decorators

@decorators.service
class UrlShortener:
    def __init__(self):
        self.urls = {} # type: Persistent[dict]

    ## This method returns a short url, 
    ##   either by making it on the spot, or by looking in the dict.
    ##
    ## TODO: Enable transactoions in the source spec of the compiler
    def ShortenUrls(self, long_url):
        
        ## TODO: Add transactions
        if not long_url in self.urls.keys():
            ## TODO: Do that in a separate method
            short_url = long_url + "+hash"
            self.urls.update([(long_url, short_url)])
            return ("NotFound", short_url)
        else:
            return ("Found", self.urls.get(long_url))

    def ComposeUrls(self, _req_id, long_urls):
        urls = [self.ShortenUrls(long_url)[1] for long_url in long_urls]
        return urls
