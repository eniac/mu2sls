def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    print("Hello! You said:", req)
    return req
