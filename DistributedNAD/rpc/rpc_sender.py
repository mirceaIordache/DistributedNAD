import urllib2
import threading
import json

class RPCSender:
    def __init__(self):
        pass

    @staticmethod
    def send(host, message):
        threading.Thread(target = RPCSender._send, args = [host, message]).start()
    
    @staticmethod
    def _send(host, message):
        url = "{}/{}".format(host.get_url(), message())
        reply = json.loads(urllib2.urlopen(url).read())
        print "Got reply", reply
        print reply[0], reply[1]
	
        from main import DistributedDetector
        DistributedDetector.return_votes(reply[0], reply[1], host)

class RPCHost:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port

    def get_url(self):
        return "http://{}:{}".format(self.ip, self.port)

    def __str__(self):
        return self.get_url()
