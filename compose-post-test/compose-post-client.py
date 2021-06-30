import sys
sys.path.append('gen-py')

from thrift.transport import THttpClient
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol, TJSONProtocol

from social_network import TextService, UrlShortenService

from concurrent.futures import ThreadPoolExecutor, TimeoutError
import traceback
import inspect
import pdb

URL="http://127.0.0.1:8090/function/compose-post"

## An HTTP Client is necessary to interact with FaaS
transport = THttpClient.THttpClient(URL)

## Adding buffering to the transport actually leads to a bug, where some of the connections fail.
# transport = TTransport.TBufferedTransport(transport)

## The protocol also probably doesn't matter, but it is good to start with JSON for better observability.
protocol = TJSONProtocol.TJSONProtocol(transport)

## TODO: Is this a thread safe client?????
client = TextService.Client(protocol)

# Connect!
transport.open()

def gather_res(res, i):
    try:
        print(res.result(5))
    except TimeoutError:
        print("timeout for:", i)
    except Exception as inst:
        print("Exception!")
        print(inst)
        traceback.print_exc()
        ## TODO: Old debugging
        # traceback.print_tb(tb)
        # frames = inspect.trace()
        # for frame in frames:
        #     argvalues = inspect.getargvalues(frame[0])
        #     print('Argvalues: %s', inspect.formatargvalues(*argvalues))
        # pdb.post_mortem(tb)

## Make a request
max_workers = 1
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    results = []
    for i in range(1):
        print(i)
        results.append(executor.submit(client.ComposeText, i, "popopo", {}))
        res = results[i]
        executor.submit(gather_res, res, i)
    # ret = client.ComposeText(5, "popopo", {})

    # for i in range(len(results)):
    #     res = results[i]
    #     executor.submit(gather_res, res, i)
# print(ret)