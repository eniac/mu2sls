import asyncio
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

from thrift.transport import TSocket, TTransport, THttpClient
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
    ## Setup the socket
    transport = TSocket.TSocket(host=service_addr,
                                port=service_port)
    ## Configure the transport layer to correspond to the expected transport
    transport = TTransport.TFramedTransport(transport)

    ## Configure the protocol to be binary as expected from the service
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    ## Create the client
    client = service_client_class.Client(protocol)

    ## Connect to the client
    ## TODO: Understand what this does
    ## TODO: Where do we need to catch errors?
    transport.open()

    return client

def SetupHttpClient(service_client_class, service_url):
    ## An HTTP Client is necessary to interact with FaaS
    transport = THttpClient.THttpClient(service_url)

    ## TODO: This leads to a bug, probably because it is not mirrored on the serverless side (I am not even sure it can be).
    # transport = TTransport.TBufferedTransport(transport)

    ## The protocol also probably doesn't matter, but it is good to start with JSON for better observability.
    protocol = TJSONProtocol.TJSONProtocol(transport)
    client = service_client_class.Client(protocol)

    # TODO: Unclear if this is necessary. 
    transport.open()

    return client

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

## TODO: Do we actually need the async keywords here?
async def shorten_urls(url_shorten_service_client, span, urls, req_id):
    tracer = opentracing.global_tracer()
    serialized_span_context = {}
    tracer.inject(
        span_context=span.context,
        format=Format.TEXT_MAP,
        carrier=serialized_span_context
    )

    ## Call the UrlShorten Service
    shortened_urls = url_shorten_service_client.ComposeUrls(req_id, urls, serialized_span_context)
    return shortened_urls

async def compose_user_mentions(user_mention_service_client, span, mention_usernames, req_id):
    tracer = opentracing.global_tracer()
    serialized_span_context = {}
    tracer.inject(
        span_context=span.context,
        format=Format.TEXT_MAP,
        carrier=serialized_span_context
    )

    ## Call the UrlShorten Service
    return_user_mentions = user_mention_service_client.ComposeUserMentions(req_id, mention_usernames, serialized_span_context)
    return return_user_mentions

## TODO: Write a proper handler!!!
## TODO: Figure out what to do with handler fields, and how they differ from the original ones
class TextHandler:
    def __init__(self, 
                 url_shorten_service_client,
                 user_mention_service_client):
        self.url_shorten_service_client = url_shorten_service_client
        self.user_mention_service_client = user_mention_service_client

    def ComposeText(self, req_id, text, carrier):
        return asyncio.run(self.ComposeTextAIO(req_id, text, carrier))

    async def ComposeTextAIO(self, req_id, text, carrier):
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

            ## Gather a list of urls
            url_matches = re.findall("(http://|https://)([a-zA-Z0-9_!~*'().&=+$%-]+)", text)
            urls = ["".join(match) for match in url_matches]
            logging.debug("Urls: " + str(urls))

            ## Shorten urls and compose user mentions

            ## TODO: The `compose user mentions` seems to return empty list so there might be a bug.
            results = await asyncio.gather(
                shorten_urls(self.url_shorten_service_client, span, urls, req_id),
                compose_user_mentions(self.user_mention_service_client, span, mention_usernames, req_id),
            )
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

            ret = ttypes.TextServiceReturn(new_text,
                                           user_mentions=return_mentions,
                                           urls=return_urls)
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

    ## Initialize the clients, 
    ## TODO: Make these ports taken from some configuration this is very ad-hoc.
    # url_shorten_service_client = SetupClient(UrlShortenService, "host.k3d.internal", 10004)
    ## Initialize the serverless http client instead of the original one
    ##
    ## WARNING: In Kubernetes, the gateway hostname changes to gateway.openfaas
    gateway_hostname = os.getenv("gateway_hostname", "gateway.openfaas") 
    url_shorten_service_client = SetupHttpClient(UrlShortenService, 
                                                 "http://" + gateway_hostname + ":8080/function/url-shorten-service")

    user_mention_service_client = SetupClient(UserMentionService, "host.k3d.internal", 10009)

    ## Create a processor object
    handler = TextHandler(url_shorten_service_client=url_shorten_service_client,
                          user_mention_service_client=user_mention_service_client)
    processor = TextService.Processor(handler)

    ## Up to this point all the code is run in the microservice version too
    ##
    ###########################################################################

    ## Assumption: At this point all fields and globals have been initialized.

    ###########################################################################
    ##
    ## The following code replaces the setup of a Thrift server 
    ## and the call to .serve()
    ##

    ## Create a protocol object
    input_transport = DummyReadHttpTransport(str(req))
    output_transport = DummyWriteTransport()

    ## Maybe this is not needed either
    # transport = TTransport.TBufferedTransport(transport)
    input_protocol = TJSONProtocol.TJSONProtocol(input_transport)
    output_protocol = TJSONProtocol.TJSONProtocol(output_transport)
   

    ## Process an object
    processor.process(input_protocol, output_protocol)
    
    ret = output_transport.output
    logging.debug("Output: " + str(ret))

    return ret
    