class NetworkSwitches:

    class __metaclass__(type):
        def __iter__(self):
            return NetworkSwitches.instance.__iter__()

        def __getitem__(self, item):
            if NetworkSwitches.instance:
                return NetworkSwitches.instance[str(item)]
            return None

    class _NetworkSwitches(object):
        def __init__(self, config):
            f = open(config, 'r')
            self.switches = {}
            for line in f:
                split = line.split()
                self.switches[split[0]] = split[1]
            f.close()

        def __getitem__(self, item):
	    if item in self.switches:
		return self.switches[item]
	    else: 
		return None
	      
        def __len__(self):
            return len(self.switches)

        def __contains__(self, item):
            return item in self.switches

        def __iter__(self):
            return self.switches.__iter__()

        def has_value(self, item):
            return item in self.switches.values()

        def values(self):
            return self.switches.values()

    instance = None

    def __init__(self, config):
        if not NetworkSwitches.instance:
            NetworkSwitches.instance = NetworkSwitches._NetworkSwitches(config)

    def __getitem__(self, item):
        if NetworkSwitches.instance:
            return NetworkSwitches.instance[item]
        else:
            return None

    def __len__(self):
        if NetworkSwitches.instance:
            return len(NetworkSwitches.instance)
        else:
            return 0

    def __contains__(self, item):
        if NetworkSwitches.instance:
            return item in NetworkSwitches.instance
        else:
            return False

    @staticmethod
    def has_value(item):
        if NetworkSwitches.instance:
            return NetworkSwitches.instance.has_value(item)
        else:
            return False

    @staticmethod
    def values():
        if NetworkSwitches.instance:
            return NetworkSwitches.instance.values()
        else:
            return []
