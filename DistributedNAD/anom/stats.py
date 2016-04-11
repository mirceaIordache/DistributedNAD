import json
import urllib2
from collections import namedtuple


from config.network_switches import NetworkSwitches
from config.controller import ControllerConfig
from config.instance import RunningInstance
from anom.api.base import BaseAnomalyDetector

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
