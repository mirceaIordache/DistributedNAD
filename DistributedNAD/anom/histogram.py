import copy
import math

from api.base import BaseAnomalyDetector

class HistogramAnomalyDetector(BaseAnomalyDetector):

    def __init__(self):
        super(HistogramAnomalyDetector, self).__init__()
        self.h = {"src_ip": {}, "src_port": {}, "dst_ip": {}, "dst_port": {}}
        self.prev_h = {"src_ip": {}, "src_port": {}, "dst_ip": {}, "dst_port": {}}
        self.total = {"src_ip": {}, "src_port": {}, "dst_ip": {}, "dst_port": {}}
        self.upd = {"src_ip": [], "src_port": [], "dst_ip": [], "dst_port": []}
        self.threshold = {"src_ip": 0.05, "src_port": 0.05, "dst_ip": 0.05, "dst_port": 0.05}
        self.prev_dist = {"src_ip": 0, "src_port": 0, "dst_ip": 0, "dst_port": 0}

    def add_data(self, src_ip, dst_ip, src_port, dst_port, packets=1):
        if src_ip not in self.h["src_ip"]:
            self.h["src_ip"][src_ip] = 0
        if src_port not in self.h["src_port"]:
            self.h["src_port"][src_port] = 0
        if dst_ip not in self.h["dst_ip"]:
            self.h["dst_ip"][dst_ip] = 0
        if dst_port not in self.h["dst_port"]:
            self.h["dst_port"][dst_port] = 0

        if src_ip not in self.total["src_ip"]:
            self.total["src_ip"][src_ip] = 0
        if src_port not in self.total["src_port"]:
            self.total["src_port"][src_port] = 0
        if dst_ip not in self.total["dst_ip"]:
            self.total["dst_ip"][dst_ip] = 0
        if dst_port not in self.total["dst_port"]:
            self.total["dst_port"][dst_port] = 0

        self.h["src_ip"][src_ip] = packets - self.total["src_ip"][src_ip]
        self.h["src_port"][src_port] = packets - self.total["src_port"][src_port]
        self.h["dst_ip"][dst_ip] = packets - self.total["dst_ip"][dst_ip]
        self.h["dst_port"][dst_port] = packets - self.total["dst_port"][dst_port]

        self.total["src_ip"][src_ip] = packets
        self.total["src_port"][src_port] = packets
        self.total["dst_ip"][dst_ip] = packets
        self.total["dst_port"][dst_port] = packets

        self.upd["src_ip"].append(src_ip)
        self.upd["src_port"].append(src_port)
        self.upd["dst_ip"].append(dst_ip)
        self.upd["dst_port"].append(dst_port)


    def new_tick(self):
        for feature in self.h:
            self.upd[feature] = []
            self.prev_h[feature] = copy.deepcopy(self.h[feature])

    def clear_data(self):
        for feature in self.h:
            keys = copy.deepcopy(self.h[feature].keys())
            for feat in keys:
                if feat not in self.upd[feature]:
                    self.h[feature].pop(feat)

    def find_anomalies(self):
        sentinel = False
        for feature in self.h:
            kl_dist = 0
            for key in self.h[feature]:
                if key in self.prev_h[feature]:
                    curr_packets = self.h[feature][key]
                    prev_packets = self.prev_h[feature][key]
                    kl_dist += prev_packets * math.log(float(prev_packets) / curr_packets)
                else:
                    continue
            if self.prev_dist[feature] - kl_dist > self.threshold[feature]:
                print "Anomaly on", feature
                sentinel = True
            self.prev_dist[feature] = kl_dist
        return sentinel
