import copy

from api.base import BaseAnomalyDetector

class HistogramAnomalyDetector(BaseAnomalyDetector):

    def __init__(self):
        super(HistogramAnomalyDetector, self).__init__()
        self.h_src_ip = {}
        self.h_src_port = {}
        self.h_dst_ip = {}
        self.h_dst_port = {}

    def add_data(self, src_ip, dst_ip, src_port, dst_port, packets=1):
        if src_ip not in self.h_src_ip:
            self.h_src_ip[src_ip] = 0
        if src_port not in self.h_src_port:
            self.h_src_port[src_port] = 0
        if dst_ip not in self.h_dst_ip:
            self.h_dst_ip[dst_ip] = 0
        if dst_port not in self.h_dst_port:
            self.h_dst_port[dst_port] = 0

        self.h_src_ip[src_ip] = packets - self.h_src_ip[src_ip]
        self.h_src_port[src_port] = packets - self.h_src_port[src_port]
        self.h_dst_ip[dst_ip] = packets - self.h_dst_ip[dst_ip]
        self.h_dst_port[dst_port] = packets - self.h_dst_port[dst_port]

    def new_tick(self):
        pass

    def clear_data(self):
        pass

    def find_anomalies(self):
        pass