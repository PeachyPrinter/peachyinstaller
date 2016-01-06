import threading

class InstallApplication(threading.thread):
    def __init__(self, application, status_call_back, complete_callback):
        threading.Thread.__init__(self)
        pass

    def run(self):
        pass
