import logging
import re

from compiler import decorators



## TODO: Do we actually need the async keywords here?
async def shorten_urls(url_shorten_service_client, urls, req_id):

    ## Call the UrlShorten Service
    shortened_urls = url_shorten_service_client.ComposeUrls(req_id, urls)
    return shortened_urls

async def compose_user_mentions(user_mention_service_client, mention_usernames, req_id):
    ## Call the UrlShorten Service
    return_user_mentions = user_mention_service_client.ComposeUserMentions(req_id, mention_usernames)
    return return_user_mentions

@decorators.service
class ComposePost:
    def __init__(self, clientFactory):
        ## TODO: Determine how to parse those. What should the term be
        self.url_shorten_service_client = clientFactory("UrlShortener") # type: Client
        self.user_mention_service_client = clientFactory("UserMentions") # type: Client

    def ComposeText(self, req_id, text):
        logging.debug("Processing request: " + str(req_id))
        
        ## Gather a list of all mentioned usernames
        matches = re.findall('@[a-zA-Z0-9-_]+', text)
        mention_usernames = [match[1:] for match in matches]
        logging.debug("Mentioned usernames: " + str(mention_usernames))

        ## Gather a list of urls
        url_matches = re.findall("(http://|https://)([a-zA-Z0-9_!~*'().&=+$%-]+)", text)
        urls = ["".join(match) for match in url_matches]
        logging.debug("Urls: " + str(urls))

        ## Shorten urls and compose user mentions

        ## TODO: The `compose user mentions` seems to return empty list so there might be a bug.
        ##
        ## TODO: Make it work with asyncio
        # results = await asyncio.gather(
        #     shorten_urls(self.url_shorten_service_client, span, urls, req_id),
        #     compose_user_mentions(self.user_mention_service_client, span, mention_usernames, req_id),
        # )
        
        ## TODO: First handle just client requests
        # results = (shorten_urls(self.url_shorten_service_client, urls, req_id), 
        #            compose_user_mentions(self.user_mention_service_client, mention_usernames, req_id))
        
        results = ([], [])


        return_urls, return_mentions = results
        
        logging.debug("Shortened Urls: " + str(return_urls))
        logging.debug("Composed Mentions: " + str(return_mentions))

        ## Replace the big urls with the small ones
        ##
        ## TODO: Naive implementation... Optimize!
        new_text = text
        for i in range(len(urls)):
            from_url = urls[i]
            to_url = return_urls[i].shortened_url
            new_text = new_text.replace(from_url, to_url, 1)

        ## TODO: Allow correct imports
        # ret = ttypes.TextServiceReturn(new_text,
        #                                 user_mentions=return_mentions,
        #                                 urls=return_urls)

        ret = (new_text, return_mentions, return_urls)
        return ret