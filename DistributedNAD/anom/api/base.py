class BaseAnomalyDetector(object):

    #Interface for use with the switch data handling module
    def __init__(self):
        pass

    def add_data(self, src_ip, dst_ip, src_port, dst_port, packets=1):
        pass

    def new_tick(self):
        pass

    def clear_data(self):
        pass

    def find_anomalies(self):
        pass
