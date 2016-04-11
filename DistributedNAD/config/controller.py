class ControllerConfig:
    class _ControllerConfig:
        def __init__(self, config):
            f = open(config, 'r')
            split = f.readline().split()
            self.controller_address = split[0]
            self.controller_port = int(split[1])
            self.controller_notification = split[2]
            self.controller_url = "http://{0}:{1}".format(self.controller_address, self.controller_port)
            f.close()

        def get_address(self):
            return self.controller_address

        def get_port(self):
            return self.controller_port

        def get_url(self):
            return self.controller_url

        def get_notification(self):
            return self.controller_notification

    instance = None

    def __init__(self, config):
        if not ControllerConfig.instance:
            ControllerConfig.instance = ControllerConfig._ControllerConfig(config)

    @staticmethod
    def get_address():
        if ControllerConfig.instance:
            return ControllerConfig.instance.get_address()
        else:
            return None

    @staticmethod
    def get_port():
        if ControllerConfig.instance:
            return ControllerConfig.instance.get_port()
        else:
            return None

    @staticmethod
    def get_url():
        if ControllerConfig.instance:
            return ControllerConfig.instance.get_url()
        else:
            return None

    @staticmethod
    def get_notif():
        if ControllerConfig.instance:
            return ControllerConfig.instance.get_notification()
        else:
            return None