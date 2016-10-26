import json
import urllib2
from collections import namedtuple


from config.network_switches import NetworkSwitches
from config.controller import ControllerConfig
from config.instance import RunningInstance
from anom.api.base import BaseAnomalyDetector

#json_string = ['{"2": [{"actions": ["GOTO_TABLE:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 1, "hard_timeout": 0, "byte_count": 2398704, "length": 104, "duration_nsec": 36000000, "priority": 1000, "duration_sec": 11, "table_id": 0, "flags": 0, "match": {"dl_type": 2048, "nw_dst": "10.0.0.2", "nw_proto": 6, "tp_dst": 36345, "tp_src": 5001, "nw_src": "10.0.0.1"}}, {"actions": ["GOTO_TABLE:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 10, "hard_timeout": 0, "byte_count": 4858909568, "length": 104, "duration_nsec": 38000000, "priority": 1000, "duration_sec": 11, "table_id": 0, "flags": 0, "match": {"dl_type": 2048, "nw_dst": "10.0.0.1", "nw_proto": 6, "tp_dst": 5001, "tp_src": 36345, "nw_src": "10.0.0.2"}}, {"actions": ["OUTPUT:2"], "idle_timeout": 0, "cookie": 0, "packet_count": 36345, "hard_timeout": 0, "byte_count": 2398802, "length": 96, "duration_nsec": 56000000, "priority": 1, "duration_sec": 35, "table_id": 1, "flags": 0, "match": {"dl_dst": "c6:d9:24:56:6a:dc", "in_port": 1}}, {"actions": ["OUTPUT:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 74549, "hard_timeout": 0, "byte_count": 4858909666, "length": 96, "duration_nsec": 50000000, "priority": 1, "duration_sec": 35, "table_id": 1, "flags": 0, "match": {"dl_dst": "1a:a8:8a:a5:23:2a", "in_port": 2}}]}' , '{"2": [{"actions": ["GOTO_TABLE:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 11, "hard_timeout": 0, "byte_count": 2398704, "length": 104, "duration_nsec": 36000000, "priority": 1000, "duration_sec": 11, "table_id": 0, "flags": 0, "match": {"dl_type": 2048, "nw_dst": "10.0.0.2", "nw_proto": 6, "tp_dst": 36345, "tp_src": 5001, "nw_src": "10.0.0.1"}}, {"actions": ["GOTO_TABLE:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 20, "hard_timeout": 0, "byte_count": 4858909568, "length": 104, "duration_nsec": 38000000, "priority": 1000, "duration_sec": 11, "table_id": 0, "flags": 0, "match": {"dl_type": 2048, "nw_dst": "10.0.0.1", "nw_proto": 6, "tp_dst": 5001, "tp_src": 36345, "nw_src": "10.0.0.2"}}, {"actions": ["OUTPUT:2"], "idle_timeout": 0, "cookie": 0, "packet_count": 36345, "hard_timeout": 0, "byte_count": 2398802, "length": 96, "duration_nsec": 56000000, "priority": 1, "duration_sec": 35, "table_id": 1, "flags": 0, "match": {"dl_dst": "c6:d9:24:56:6a:dc", "in_port": 1}}, {"actions": ["OUTPUT:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 74549, "hard_timeout": 0, "byte_count": 4858909666, "length": 96, "duration_nsec": 50000000, "priority": 1, "duration_sec": 35, "table_id": 1, "flags": 0, "match": {"dl_dst": "1a:a8:8a:a5:23:2a", "in_port": 2}}]}', '{"2": [{"actions": ["GOTO_TABLE:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 21, "hard_timeout": 0, "byte_count": 2398704, "length": 104, "duration_nsec": 36000000, "priority": 1000, "duration_sec": 11, "table_id": 0, "flags": 0, "match": {"dl_type": 2048, "nw_dst": "10.0.0.2", "nw_proto": 6, "tp_dst": 36345, "tp_src": 5001, "nw_src": "10.0.0.1"}}, {"actions": ["GOTO_TABLE:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 30, "hard_timeout": 0, "byte_count": 4858909568, "length": 104, "duration_nsec": 38000000, "priority": 1000, "duration_sec": 11, "table_id": 0, "flags": 0, "match": {"dl_type": 2048, "nw_dst": "10.0.0.1", "nw_proto": 6, "tp_dst": 5001, "tp_src": 36345, "nw_src": "10.0.0.2"}}, {"actions": ["OUTPUT:2"], "idle_timeout": 0, "cookie": 0, "packet_count": 36345, "hard_timeout": 0, "byte_count": 2398802, "length": 96, "duration_nsec": 56000000, "priority": 1, "duration_sec": 35, "table_id": 1, "flags": 0, "match": {"dl_dst": "c6:d9:24:56:6a:dc", "in_port": 1}}, {"actions": ["OUTPUT:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 74549, "hard_timeout": 0, "byte_count": 4858909666, "length": 96, "duration_nsec": 50000000, "priority": 1, "duration_sec": 35, "table_id": 1, "flags": 0, "match": {"dl_dst": "1a:a8:8a:a5:23:2a", "in_port": 2}}]}']


class StatsHandler(object):
    def __init__(self):
        if not RunningInstance.get_dpid():
            raise ValueError("Unable to get Runtime information. Is it initialised?")
        if not ControllerConfig.get_address() or not ControllerConfig.get_port() or not ControllerConfig.get_url():
            raise ValueError("Unable to get Controller information. Is it initialised?")
        self.NetworkFlow = namedtuple("NetworkFlow", "src_ip dst_ip src_port dst_port packets")
        self.id = RunningInstance.get_dpid()
        self.url = "{0}/stats/{1}".format(ControllerConfig.get_url(), self.id)
        self.switch_response = json.loads("{}")
 
    def get_stats(self):
        #Update the statistics from the switch
        self.switch_response = json.loads(urllib2.urlopen(self.url).read())[str(self.id)]

    def update_anom(self, anom):
        #Update the anomaly detection algorithm with newest data
        if not issubclass(anom.__class__, BaseAnomalyDetector):
            raise ValueError("Argument must be a subclass of BaseAnomalyDetector.")

        anom.new_tick()

        for rule in self.switch_response:
            if rule["table_id"] == 1:
                continue
            match = rule["match"]
            if not NetworkSwitches.has_value(match["nw_src"]) and not NetworkSwitches.has_value(match["nw_dst"]):
                anom.add_data(match["nw_src"], match["nw_dst"], match["tp_src"], match["tp_dst"], rule["packet_count"])

        anom.clear_data()

#    def _test_stats(self, i):
#        self.switch_response = json.loads(json_string[i])[str(self.id)]
