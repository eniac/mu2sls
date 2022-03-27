from compiler import decorators

@decorators.service
class Text:
    def __init__(self):
        pass

    async def upload_text(self, req_id, text):
        promise = AsyncInvoke('ComposeReview', "upload_text", req_id, text)
        await Wait(promise)
