#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2017/01/06

import threading

from optimizer.utils import daemon
from optimizer import app

def run_in_thread():
    
    def start_and_init_server(app):
        app.run(host='0.0.0.0', port=8848, threaded=True)
        
    server_thread = threading.Thread(target=start_and_init_server, args=(app, ))
    server_thread.start()

class OptimizerDaemon(daemon.Daemon):
    def __init__(self, pidfile, config={}):
        super(OptimizerDaemon, self).__init__(pidfile)
        
    def run(self):
        run_in_thread()