#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import os
import time
from argparse import ArgumentParser
from signal import SIGTERM
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError, e:
    print str(e)
    sys.exit(2)

NUL='/dev/null'
PID='/tmp/filemon.pid'
BASEDIR=os.path.abspath(os.path.dirname(__file__))


def parse_arguments():
    """ Process command line arguments """
    parser = ArgumentParser(description='Monitoring given file path changes')
    parser.add_argument('-d','--daemon',action='store_true', 
            help='Daemonize this process', required=False)
    parser.add_argument('-a','--address',help='email address',
    required=False)
    parser.add_argument('-f','--file',help='File to watch', required=False)
    parser.add_argument('-k','--kill',action='store_true', 
    help='Send kill signal to daemonized process', required=False)
    return parser.parse_args()
    
class eventHandler(FileSystemEventHandler):
    def __init__(self, observer, filename):
        self.observer = observer
        self.filename = filename

    def on_created(self, event):
        print "e=", event
        if not event.is_directory and event.src_path.endswith(self.filename):
            print "file created"
            self.observer.unschedule_all()
            self.observer.stop()
   
def daemonize():
    stdin=NUL
    stdout=NUL
    stderr=NUL
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("Error when forking process: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)
    
    os.chdir("/")
    os.setsid()
    os.umask(0)
    
    #It is not necessary a second fork.
    
    #redirection of IO, latter we will write log management
    sys.stdout.flush()
    sys.stderr.flush()
    
    stdi= file(stdin, 'r')
    stdo= file(stdout, 'a+')
    stde= file(stderr, 'a+', 0)
    
    try:
        pidFile = file(PID,'r')
        pid = int(pidFile.read().strip())
        pidFile.close()
    except IOError:
        pid = None
        
    if pid:
        sys.stderr.write("pid file %s already exist. If there are not \
                                    other filemon processes running please delete it." % PID)
        
    os.dup2(stdi.fileno(), sys.stdin.fileno())
    os.dup2(stdo.fileno(), sys.stdout.fileno())
    os.dup2(stde.fileno(), sys.stderr.fileno())
    
    pid = str(os.getpid())
    file(PID,'w+').write("%s\n" % pid)
    
    

def stopDaemon():
    try:
        pidFile = file(PID,'r')
        pid = int(pidFile.read().strip())
        pidFile.close()
    except IOError:
       pid = None
       
      
    if not pid:
       sys.stderr.write("Process is not running\n")
       sys.exit(0)
     
    try:
        os.kill(pid, SIGTERM)
        time.sleep(0.1)
        os.remove(PID)
    except OSError, e:
        print str(e)
        sys.exit(1)
    sys.exit(0)
    
def main():          
    args = parse_arguments()
    if (args.kill):
        stopDaemon()
    if (args.daemon):
        daemonize()    
    observer = Observer()
    event_handler = eventHandler(observer, args.file)
    observer.schedule(event_handler, BASEDIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
        
        
if __name__ == "__main__":
    main()
