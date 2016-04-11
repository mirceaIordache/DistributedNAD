class RunningInstance:
    class _RunningInstance:
        def __init__(self, config):
            f = open(config, 'r')
            self.dpid = int(f.readline())
            self.background = f.readline()[:-2] == 'true'
            self.neighbours = {}
            for lines in f:
                split = lines.split()
                self.neighbours[split[0]] = split[1]
            f.close()

        def get_dpid(self):
            return self.dpid

        def get_neighbours(self):
            return self.neighbours

        def is_background(self):
            return self.background

    instance = None

    def __init__(self, config):
        if not RunningInstance.instance:
            RunningInstance.instance = RunningInstance._RunningInstance(config)

    @staticmethod
    def get_dpid():
        if RunningInstance.instance:
            return RunningInstance.instance.get_dpid()
        else:
            return None

    @staticmethod
    def get_neighbours():
        if RunningInstance.instance:
            return RunningInstance.instance.get_neighbours()
        else:
            return None

    @staticmethod
    def is_background():
        if RunningInstance.instance:
            return RunningInstance.instance.is_background()
        else:
            return None
