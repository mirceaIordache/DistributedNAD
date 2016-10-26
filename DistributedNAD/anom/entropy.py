from collections import namedtuple
from math import log
import copy

from api.base import BaseAnomalyDetector
from config.instance import RunningInstance

class EntropyAnomalyDetector(BaseAnomalyDetector):

    def __init__(self):
        super(EntropyAnomalyDetector, self).__init__()
        self.network_data = {}
        self.DataFlow = namedtuple("DataFlow", "src_ip dst_ip src_port dst_port")
        self.known_entropy = [0.75, 0.75, 0.75, 0.75]
        self.threshold = [0.1, 0.1, 0.1, 0.1]
        self.updated = []

    def add_data(self, src_ip, dst_ip, src_port, dst_port, packets=1):
        data = self.DataFlow(src_ip, dst_ip, src_port, dst_port)
        if data in self.network_data:
            self.network_data[data] = packets - self.network_data[data]
            if self.network_data[data] > 0:
                self.updated.append(data)
        elif packets > 0:
            self.network_data[data] = packets
            self.updated.append(data)

    def new_tick(self):
        del self.updated[:]

    def clear_data(self):
        data_copy = copy.deepcopy(self.network_data)
        for data in data_copy:
            if data not in self.updated:
                self.network_data.pop(data)

    def find_anomalies(self):
        print "------------", RunningInstance.get_dpid(), "Entropy Run------------"
        current_data_image = copy.deepcopy(self.network_data)
        criterions = range(4)
        for i in criterions:
            print RunningInstance.get_dpid(), ": Calculating entropy for", self.DataFlow._fields[i], ":",
            datasets = self._calculate_datasets(i, current_data_image)
            probability = self._calculate_probability(datasets)
            entropy = self._calculate_entropy(probability)
            print entropy
            sentinel = False
            if self._anomaly_from_entropy(entropy, i):
                sentinel = True
            self.known_entropy[i] = entropy
            if sentinel:
                return True
        return False

    def _anomaly_from_entropy(self, entropy, criteria):
        return abs(entropy-self.known_entropy[criteria]) > self.threshold[criteria]

    @staticmethod
    def _calculate_entropy(probability):
        entropy = 0
        for i in probability:
            entropy += probability[i]*log(probability[i], 2)
        if entropy:
            return -(entropy/log(len(probability), 2))
        return 0.0

    @staticmethod
    def _calculate_datasets(criteria, data):
        datasets = {}
        for i in data:
            if i[criteria] in datasets:
                datasets[i[criteria]] += data[i]
            else:
                datasets[i[criteria]] = data[i]
        return datasets

    @staticmethod
    def _calculate_probability(dataset):
        probability = {}
        total = 0.0
        for i in dataset:
            probability.update({i: dataset[i]})
            total += dataset[i]

        for i in probability:
            if total != 0:
                probability[i] /= total
            else:
                probability[i] = 1
        return probability

    def debug_print(self):
        print '----!Entropy Debug!---'
        for key in self.network_data.keys():
            print '(', key.src_ip, ':', key.src_port, ' -> ', key.dst_ip, ':', key.dst_port, ')', ":", self.network_data[key]
        print '-----!Entropy End!----'
        print
