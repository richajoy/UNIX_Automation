import subprocess
import logging
import sys

svc = str(sys.argv[1])

logging.basicConfig(filename='svc.log' ,
                    format = '%(asctime)s - %(levelname)s: %(message)s' ,
                    level=logging.DEBUG)

logging.info('Checking if process' + svc + 'is running')

service_is_running = subprocess.call(["ps", "-C", svc])

if service_is_running == 1:
    logging.warning('Process ' + svc + ' is not running')
    logging.info('Attempting to start: ' + svc)
    restart_sts = subprocess.call(["sudo", "/etc/init.d/%s" % svc, "start"])
    if restart_sts == 1:
        logging.error("Unable to start %s please check the logs" % svc)
    else:
        loging.info("%s successfully started" % svc)
else:
    logging.info("%s is currently running" % svc)
