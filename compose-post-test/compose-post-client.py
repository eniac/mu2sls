import sys
sys.path.append('gen-py')

from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TJSONProtocol

from social_network import TextService


URL="http://127.0.0.1:8080/function/compose-post"



transport = THttpClient.THttpClient(URL)
transport = TTransport.TBufferedTransport(transport)
protocol = TJSONProtocol.TJSONProtocol(transport)
client = TextService.Client(protocol)

# Connect!
transport.open()

## Make a request
client.ComposeText(5, "popopo", {})
