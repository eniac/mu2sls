import asyncio
import logging
import os
import random
import string
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

from social_network import UrlShortenService, ttypes

## For Jaeger
from jaeger_client import Config
import opentracing
from opentracing.propagation import Format

## For MongoDB
from pymongo import MongoClient

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

def SetupMongoDBClient(addr, port):
    return MongoClient(addr,port)

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
    set_up_tracer("TODO", 'url-shorten-service')


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

## TODO: Figure out what to do with handler fields, and how they differ from the original ones
class UrlShortenHandler:
    def __init__(self, 
                 mongodb_client):
        self.mogodb_client = mongodb_client
        ## TODO: Do the rest of the initializations

    def ComposeUrls(self, req_id, urls, carrier):
        return asyncio.run(self.ComposeUrlsAIO(req_id, urls, carrier))

    async def ComposeUrlsAIO(self, req_id, urls, carrier):
        logging.debug("Processing request: " + str(req_id))
        tracer = opentracing.global_tracer()

        parent_span_context = tracer.extract(format=Format.TEXT_MAP,
                                             carrier=carrier)
        # log("ParentContext:", parent_span_context)
        with tracer.start_span(operation_name='compose_urls_server', 
                               child_of=parent_span_context) as span:

            ## Get a database
            db = self.mogodb_client['url-shorten']

            logging.debug("Collections: " + str(db.list_collection_names()))

            ## Get the collection
            url_collection = db['url-shorten']

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
                url_collection.insert_one(url_object)

            ## Just print one random entry to see
            # logging.debug("Random entry: " + str(url_collection.find_one()))

            ## Perform concurrent calls
            # results = await asyncio.gather(
            #     shorten_urls(self.url_shorten_service_client, span, urls, req_id),
            #     compose_user_mentions(self.user_mention_service_client, span, mention_usernames, req_id),
            # )
            # return_urls, return_mentions = results
            
            # logging.debug("Shortened Urls: " + str(return_urls))


            return target_urls

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    # print(req)
    logging.debug("Input: " + str(req))
    logging.debug("Pid: " + str(os.getpid()))


    setup()

    ## Initialize the clients, 
    ## TODO: Make these ports taken from some configuration this is very ad-hoc.
    mongodb_client = SetupMongoDBClient("host.k3d.internal", 27021)

    ## Create a processor object
    handler = UrlShortenHandler(mongodb_client=mongodb_client)
    processor = UrlShortenService.Processor(handler)

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
    