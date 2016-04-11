import logging

from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument

from spyne.application import Application
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase
from spyne.decorator import srpc

from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode
from spyne.model.complex import Array

from main import DistributedDetector

#logging.basicConfig(level=logging.DEBUG)


class RPCReceiver:
    
    class HelloSwitchService(ServiceBase):

        @srpc(Integer, _returns=Array(Integer))
        def request_analysis(requester):
	    print "Got Request", requester
            arr = DistributedDetector.requested_analysis(requester)
	    print arr
	    return arr
    
    class _RPCReceiver:
	def __init__(self):
	    from wsgiref.simple_server import make_server
	    self.application = Application([RPCReceiver.HelloSwitchService],
					    tns='spyne.examples.hello',
					    in_protocol=HttpRpc(validator='soft'),
					    out_protocol=JsonDocument()
					    )
	    self.wsgi_app = WsgiApplication(self.application)
	    self.server = make_server('0.0.0.0', 7846, self.wsgi_app)

	def start(self):
	    self.server.serve_forever()
	    
	def stop(self):
	    self.server.socket.close()
	    self.server.shutdown()
	    
    instance = None
    
    
    def __init__(self):
	if not RPCReceiver.instance:
            RPCReceiver.instance = RPCReceiver._RPCReceiver()
	    RPCReceiver.instance.start()
	
    @staticmethod
    def stop():
	if RPCReceiver.instance:
	    RPCReceiver.instance.stop()
	
if __name__ == '__main__':
    RPCReceiver()
