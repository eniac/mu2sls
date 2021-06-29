import logging

## Not sure whether logging needs to happen like this, but this certainly works and prints output to the logs
logging.basicConfig(level=logging.DEBUG)

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    # print(req)
    logging.debug(req)
    return {}
