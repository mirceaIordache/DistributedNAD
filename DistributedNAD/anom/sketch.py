import copy

from api.base import BaseAnomalyDetector
from backend.sketch import AnomalyCountSketch


class SketchAnomalyDetector(BaseAnomalyDetector):
    def __init__(self):
        super(SketchAnomalyDetector, self).__init__()
        self.sketch_src = AnomalyCountSketch(1000, 10)
        self.sketch_dst = AnomalyCountSketch(1000, 10)
        self.updated_src = {}
        self.updated_dst = {}

        self.src_threshold = {'ip': 1, 'port': 1}
        self.dst_threshold = {'ip': 1, 'port': 1}

    def add_data(self, src_ip, dst_ip, src_port, dst_port, packets=1):
        current_value = self._getvals(src_ip, dst_ip, src_port, dst_port)
        self._update(self.sketch_src, src_ip, src_port, packets-(2*current_value[0]), self.updated_src)
        self._update(self.sketch_dst, dst_ip, dst_port, packets-(2*current_value[1]), self.updated_dst)

    def new_tick(self):
        self.updated_src.clear()
        self.updated_dst.clear()

    def clear_data(self):
        keys = copy.deepcopy(self.sketch_src.get_keys())
        for ip in keys:
            if ip not in self.updated_src:
                self.sketch_src.remove(ip)

        keys = copy.deepcopy(self.sketch_dst.get_keys())
        for ip in keys:
            if ip not in self.updated_dst:
                self.sketch_dst.remove(ip)

    def find_anomalies(self):
        local_sketch_src = copy.deepcopy(self.sketch_src)
        local_sketch_dst = copy.deepcopy(self.sketch_dst)
        print "Source Analysis"
        for ip in local_sketch_src.get_keys():
            table = local_sketch_src[ip]
            total = float(table['total'])
	    
	    print "Analysing IP:", ip
	    print "Total Traffic Ratio:", total/local_sketch_src.n
            if total/local_sketch_src.n > self.src_threshold['ip']:
		print "Found Anomaly in Source IP traffic ratio"
                return True

            for port in table:
                if port == 'total':
                    continue
		print "Traffic Ratio for Port ", port, ":", table[port]/total
                if table[port]/total > local_sketch_src['port']:
		    print "Found Anomaly in Source Port Traffic Ratio"
                    return True
	print "Destination Analysis"
        for ip in local_sketch_dst.get_keys():
            table = slocal_sketch_dst[ip]
            total = float(table['total'])
	    
	    print "Analysing IP:", ip
	    print "Total Traffic Ratio:", total/local_sketch_dst.n
            if total / local_sketch_dst.n > self.dst_threshold['ip']:
	        print "Found Anomaly in Destination IP traffic ratio"
                return True

            for port in table:
                if port == 'total':
                    continue
		print "Traffic Ratio for Port ", port, ":", table[port]/total
                if table[port] / total > self.dst_threshold['port']:
		    print "Found Anomaly in Destination Port Traffic Ratio"
                    return True
	
	print "No anomaly found"
        return False

    @staticmethod
    def _update(sketch, ip, port, val, updated):
        sketch.add(ip, port, val)
        if val > 0:
            if ip in updated:
                if port in updated[ip]:
                    updated[ip][port] += 1
                else:
                    updated[ip][port] = 1
            else:
                updated[ip] = {}
                updated[ip][port] = 1

    def _getvals(self, src_ip, dst_ip, src_port, dst_port):
        vals = [0, 0]
        if src_ip in self.sketch_src.get_keys():
            if src_port in self.sketch_src[src_ip]:
                vals[0] = self.sketch_src[src_ip][src_port]
        if dst_ip in self.sketch_dst.get_keys():
            if dst_port in self.sketch_dst[dst_ip]:
                vals[1] = self.sketch_dst[dst_ip][dst_port]

        return vals

    def debug_print(self):
        print '----!Sketch Debug!----'
        print '----Source Sketch-----'
        for ip in self.sketch_src.get_keys():
            print ip, ":", self.sketch_src[ip]['total']
        print '--------SS End--------'
        print "--Destination Sketch--"
        for ip in self.sketch_dst.get_keys():
            print ip, ":", self.sketch_dst[ip]['total']
        print '--------DS End--------'
        print '-----!Sketch End!-----'
        print
