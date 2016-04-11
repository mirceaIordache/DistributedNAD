class RPC:
    #Simple Interface for RPC mechanism
    @staticmethod
    def request_analysys(requester):
        return "request_analysis?requester=%s" % requester
