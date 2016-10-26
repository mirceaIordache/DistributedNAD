import threading
import urllib2
import time
import sys

from config.network_switches import NetworkSwitches
from config.controller import ControllerConfig
from config.instance import RunningInstance

from anom.stats import StatsHandler
from anom.entropy import EntropyAnomalyDetector
from anom.sketch import SketchAnomalyDetector

from rpc.api.rpc import RPC
from rpc.rpc_sender import RPCSender, RPCHost


class DistributedDetector:

    class _DistributedDetector:
        def __init__(self):
            NetworkSwitches("switches.ini")
            ControllerConfig("controller.ini")
            RunningInstance(sys.argv[1])
            self.sh = StatsHandler()
            self.ent = EntropyAnomalyDetector()
            self.skt = SketchAnomalyDetector()
            self.votes = {}
            self.my_vote = -1
            self.lock = threading.Lock()
            self.working = False
            from config.init import init_func
            self.rpc = init_func()
            self.kill_received = False
            print RunningInstance.get_dpid(), "Init done"
            self.t = threading.Thread(target = self.update_tick)
            #give time for other instances to start
            time.sleep(5)
            self.t.start()
            self.rpc.start()

        def background(self):
            # simple background task to catch Ctrl+C and stop subthreads
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                self.kill_received = True
                self.t.join()
                from rpc.rpc_receiver import RPCReceiver
                RPCReceiver.stop()
                self.rpc.join()

        def update_tick(self):
        #Update data every tick
            while not self.kill_received:
                print RunningInstance.get_dpid(), "Update tick"
                self.sh.get_stats()
                self.sh.update_anom(self.ent)
                self.sh.update_anom(self.skt)
                if RunningInstance.is_background():
                    #Run analysis if assigned to
                    print RunningInstance.get_dpid(), "Processing"
                    self.run_analysis()
                time.sleep(1)

        def run_analysis(self, requester=None):
            self.working = True
            print RunningInstance.get_dpid(), "Coarse grained analysis"
            if self.ent.find_anomalies():
                print RunningInstance.get_dpid(), "Found anomaly"
                #RPC Mechanism, non-blocking
                print RunningInstance.get_dpid(), "Contacting neighbours"
                message = lambda: RPC.request_analysys(RunningInstance.get_dpid())
                for neighbour in RunningInstance.get_neighbours():
                    if neighbour != NetworkSwitches[requester]:
                        host = RPCHost(neighbour, RunningInstance.get_neighbours()[neighbour])
                        print "Neighbour: ", host
                        RPCSender.send(host, message)
                        self.votes[neighbour] = []

                #SKT anomaly detection
                my_vote = 0
                if self.skt.find_anomalies():
                    my_vote = 1
                print "My vote is", my_vote
                print "Gathering other votes"

                count = my_vote
                voters = 1

                #gather votes
                guard = True
                while guard and not self.kill_received:
                    guard = False
                    self.lock.acquire()
                    for vote in self.votes:
                        if not self.votes[vote]:
                            guard = True
                    self.lock.release()
                    time.sleep(1)

                if self.kill_received:
                    self.working = False
                    return

                print "Done gathering votes"

                for vote in self.votes:
                    count += self.votes[vote][0]
                    voters += self.votes[vote][1]

                #Decide what to do, return to requester, notify controller or just dump everything
                if requester:
                    #return votes
                    print "Sending votes to requester", (count, voters)
                    self.working = False
                    return [count, voters]
                elif float(count)/voters > 0.5:
                    #notify controller
                    print "Notifying controller"
                    data = dict(dpid=RunningInstance.get_dpid())
                    urllib2.urlopen("{0}/{1}".format(ControllerConfig.get_url(), ControllerConfig.get_notif()), data=data).read()
                else:
                    print "False alarm, vote ratio is", float(count)/voters, "with", voters, "votes, of which", count, "are positive"

            self.working = False

            def count_votes(self, count, voters, neighbour):
                print "Getting Lock"
                self.lock.acquire()
                print "Adding Data"
                self.votes[neighbour.get_ip()] = [count, voters]
                print neighbour.get_ip(), ":", self.votes[neighbour.get_ip()]
                self.lock.release()
                print "Released Lock"
      
            def is_working(self):
                return self.working
      
    _instance = None

    def __init__(self):
        if not DistributedDetector._instance:
            DistributedDetector._instance = DistributedDetector._DistributedDetector()


    @staticmethod
    def background():
        if DistributedDetector._instance:
            DistributedDetector._instance.background()
	
	
    @staticmethod
    def requested_analysis(requester):
        if DistributedDetector._instance:
            if not RunningInstance.is_background() and not DistributedDetector._instance.is_working():
                return DistributedDetector._instance.run_analysis(requester)
        return None
      
    @staticmethod
    def return_votes(count, voters, neighbour):
        if DistributedDetector._instance:
            DistributedDetector._instance.count_votes(count, voters, neighbour)
