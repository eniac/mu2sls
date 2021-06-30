import logging
import os
import re
import sys

## Not sure whether logging needs to happen like this, but this certainly works and prints output to the logs
logging.basicConfig(level=logging.DEBUG)

## Include gen-py in path
# sys.path.append('gen-py')
gen_py_path = os.path.join(os.path.dirname(__file__), 'gen-py')
# logging.debug("Path: " + str(gen_py_path))
sys.path.append(gen_py_path)

from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol, TJSONProtocol

from social_network import TextService, UrlShortenService, UserMentionService, ttypes

## For Jaeger
from jaeger_client import Config
import opentracing
from opentracing.propagation import Format

global_cnt = 0

## TODO: For now we do this everytime this is called, 
##       but normally we would want to actually do it once and keep it initialized.
##
## TODO: We also need to modify its initialization with environment variables (or maybe a config file)
def set_up_tracer(config_file_path, service):
    ## TODO: Properly read YAML config
    config = Config(
        config={
            # 'disabled': False,
            ## For some reason, the yaml looks different for C++ and python...
            # 'reporter': {
                # 'logSpans': False,
                # 'localAgentHostPort': "jaeger-agent:6831",
                # 'queueSize': 1000000,
                # 'bufferFlushInterval': 10              
            # },
            'local_agent': {
                'reporting_host': 'jaeger-agent',
                'reporting_port': '6831',
            },
            'reporter_queue_size': 1000000,
            'reporter_flush_interval': 10,
            'sampler': {
                'type': "probabilistic",
                'param': 0.01
            },
            'enabled': True,
            ## TODO: Do we need this?
            # 'logging': True
        },
        service_name=service,
        validate=True
    )
    try:
        ## Initialize the tracer and set the global opentracing tracer
        # opentracing.set_global_tracer(tracer)
        config.initialize_tracer()
    except:
        log("WTF")
        exit(1)
 

## TODO: This is copied...
def SetupClient(service_client_class, service_addr, service_port):
    return None
    # ## Setup the socket
    # transport = TSocket.TSocket(host=service_addr,
    #                             port=service_port)
    # ## Configure the transport layer to correspond to the expected transport
    # transport = TTransport.TFramedTransport(transport)

    # ## Configure the protocol to be binary as expected from the service
    # protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # ## Create the client
    # client = service_client_class.Client(protocol)

    # ## Connect to the client
    # ## TODO: Understand what this does
    # ## TODO: Where do we need to catch errors?
    # transport.open()

    # return client

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
        # logging.debug(" -- chars:" + str(buf))
        new_output = buf.decode('ascii')
        self.output += new_output
        return


## This is the setup function that is called before the body of the handle
def setup():
    set_up_tracer("TODO", 'text-service')

def check_dir():
    pid = os.getpid()
    for root, dirs, files in os.walk("/tmp"):
        for filename in files:
            logging.debug("file: " + filename)
    
    pid_fname = "/tmp/" + str(pid) + ".txt"
    with open(pid_fname, "w") as f:
        f.write(str(pid) + "\n")
    
    logging.debug("wrote file: " + pid_fname)

## TODO: Write a proper handler!!!
## TODO: Figure out what to do with handler fields, and how they differ from the original ones
class TextHandler:
    def __init__(self, 
                 url_shorten_service_client,
                 user_mention_service_client):
        self.url_shorten_service_client = url_shorten_service_client
        self.user_mention_service_client = user_mention_service_client

    ## TODO: Dummy
    def ComposeText(self, req_id, text, carrier):
        logging.debug("Processing request: " + str(req_id))
        tracer = opentracing.global_tracer()

        parent_span_context = tracer.extract(format=Format.TEXT_MAP,
                                             carrier=carrier)
        # log("ParentContext:", parent_span_context)
        with tracer.start_span(operation_name='compose_text_server', 
                               child_of=parent_span_context) as span:

            ## Gather a list of all mentioned usernames
            matches = re.findall('@[a-zA-Z0-9-_]+', text)
            mention_usernames = [match[1:] for match in matches]
            logging.debug("Mentioned usernames: " + str(mention_usernames))

            ret = ttypes.TextServiceReturn("",
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
    logging.debug("Pid: " + str(os.getpid()))

    global global_cnt
    global_cnt += 1
    # logging.debug("Global cnt: " + str(global_cnt))

    setup()

    ## Inspect the directory to determine how many functions are spawned
    # check_dir()

    ## Create a protocol object
    input_transport = DummyReadHttpTransport(str(req))
    output_transport = DummyWriteTransport()

    ## Maybe this is not needed either
    # transport = TTransport.TBufferedTransport(transport)
    input_protocol = TJSONProtocol.TJSONProtocol(input_transport)
    output_protocol = TJSONProtocol.TJSONProtocol(output_transport)

    ## Initialize the clients, 
    url_shorten_service_client = SetupClient(UrlShortenService, "url-shorten-service", 9090)
    user_mention_service_client = SetupClient(UserMentionService, "user-mention-service", 9090)

    ## Create a processor object
    handler = TextHandler(url_shorten_service_client=url_shorten_service_client,
                          user_mention_service_client=user_mention_service_client)
    processor = TextService.Processor(handler)

    ## Process an object
    processor.process(input_protocol, output_protocol)
    
    ret = output_transport.output
    logging.debug("Output: " + str(ret))

    return ret
