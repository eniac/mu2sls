import sys
sys.path.append('gen-py')

from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TJSONProtocol

from social_network import TextService


URL="http://127.0.0.1:8080/function/compose-post"


## An HTTP Client is necessary to interact with FaaS
transport = THttpClient.THttpClient(URL)

## TODO: Transport probably doesn't really matter
transport = TTransport.TBufferedTransport(transport)

## The protocol also probably doesn't matter, but it is good to start with JSON for better observability.
protocol = TJSONProtocol.TJSONProtocol(transport)
client = TextService.Client(protocol)

# Connect!
transport.open()

## Make a request
ret = client.ComposeText(5, "popopo", {})

print(ret)