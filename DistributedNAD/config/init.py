import threading

from rpc.rpc_receiver import RPCReceiver


def init_func():
    thread = threading.Thread(target=RPCReceiver)
    return thread
