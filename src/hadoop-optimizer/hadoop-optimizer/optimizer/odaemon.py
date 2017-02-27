#=================================================================
# Copyright(c) Institute of Software, Chinese Academy of Sciences
#=================================================================
# Author : wuyuewen@otcaix.iscas.ac.cn
# Date   : 2017/01/06

import sys, os, os.path
import traceback
from optimizer import app
import oagent

logger = app.logger

pidfile = '/var/run/optimizer/oagent.pid'

def prepare_pid_dir(path):
    pdir = os.path.dirname(path)
    if not os.path.isdir(pdir):
        os.makedirs(pdir)
    
def main():
    usage = 'usage: python -c "from optimizer import odaemon; odaemon.main()" start|stop|restart'
    if len(sys.argv) != 2 or not sys.argv[1] in ['start', 'stop', 'restart']:
        print usage
        sys.exit(1)
    
    global pidfile
    prepare_pid_dir(pidfile)

    try:
        cmd = sys.argv[1]
        agentdaemon = oagent.OptimizerDaemon(pidfile)
        if cmd == 'start':
            logger.debug('oagent starts')
            agentdaemon.start()
        elif cmd == 'stop':
            logger.debug('oagent stops')
            agentdaemon.stop()
        elif cmd == 'restart':
            logger.debug('oagent restarts')
            agentdaemon.restart()
        sys.exit(0)    
    except Exception:
        logger.warning(traceback.format_exc())
        sys.exit(1)
    
    
if __name__ == '__main__':
    main()
