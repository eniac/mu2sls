import logging
import os
import sys

## Not sure whether logging needs to happen like this, but this certainly works and prints output to the logs
logging.basicConfig(level=logging.DEBUG)

## Include gen-py in path
# sys.path.append('gen-py')
gen_py_path = os.path.join(os.path.dirname(__file__), 'gen-py')
# logging.debug("Path: " + str(gen_py_path))
sys.path.append(gen_py_path)

from thrift.transport import TTransport
from thrift.protocol import TJSONProtocol

from social_network import TextService, ttypes


## Both of those transports are very naive and have bad performance
##
## TODO: Improve them!!!
##
## TODO: Move them in a different file
class DummyReadHttpTransport(TTransport.TTransportBase):
    def __init__(self, input):
        self.input = input
        self.index = 0

    def read(self, sz):
        new_index = min(len(self.input), self.index + sz)
        ret = self.input[self.index:new_index]
        self.index = new_index

        ## TODO: Not sure if ascii is the correct one
        return bytes(ret, 'ascii')


class DummyWriteTransport(TTransport.TTransportBase):
    def __init__(self):
        self.output = ""

    def write(self, buf):
        new_output = buf.decode('ascii')
        self.output += new_output
        return


## Write a proper handler!!!
class TextHandler:
    def __init__(self):
        pass

    ## TODO: Dummy
    def ComposeText(self, req_id, text, carrier):
        ret = ttypes.TextServiceReturn(text + "popo",
                                       [],
                                       [])
        return ret

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    # print(req)
    logging.debug("Input: " + str(req))

    ## Create a protocol object
    input_transport = DummyReadHttpTransport(str(req))
    output_transport = DummyWriteTransport()

    ## Maybe this is not needed either
    # transport = TTransport.TBufferedTransport(transport)
    input_protocol = TJSONProtocol.TJSONProtocol(input_transport)
    output_protocol = TJSONProtocol.TJSONProtocol(output_transport)


    ## Create a processor object
    handler = TextHandler()
    processor = TextService.Processor(handler)

    ## Process an object
    ##
    ## TODO: Actually the process should return the value instead of ending.
    processor.process(input_protocol, output_protocol)
    
    ret = output_transport.output
    logging.debug("Output: " + str(ret))

    return ret
