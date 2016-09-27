#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import os
from argparse import ArgumentParser
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time

NUL='/dev/null'
BASEDIR=os.path.abspath(os.path.dirname(__file__))


def parse_arguments():
    """ Process command line arguments """
    parser = ArgumentParser(description='Monitoring given file path changes')
    parser.add_argument('-d','--daemon',action='store_true', 
            help='Daemonize this process', required=False)
    parser.add_argument('-a','--address',help='email address',
    required=False)
    parser.add_argument('-f','--file',help='File to watch', required=True)
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
        print e
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
    
    os.dup2(stdi.fileno(), sys.stdin.fileno())
    os.dup2(stdo.fileno(), sys.stdout.fileno())
    os.dup2(stde.fileno(), sys.stderr.fileno())    
    
def main():

    try:
           import watchdog
    except ImportError, e:
        print "Module python watchdog must be installed"
        sys.exit(2)
        
    args = parse_arguments()
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
