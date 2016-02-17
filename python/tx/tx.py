#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
TX script: transfer one file at a time.
arguments: file to transfer
config in tx.ini
"""
import sys
import os
import codecs
import ConfigParser
import subprocess
import fcntl
import re
import sqlite3
import logging
from time import sleep
from email.mime.text import MIMEText
from smtplib import SMTP
import datetime

def createIni(ini):
    """
            Simply create template ini
    """
    iniText="""[server]
address = example.no-ip.org
bandwith = 500
localpath = /home/user/rtorrent/download/
remotepath = /tmp/
timeout    = 60
max_attempts = 5
disabled = yes
log = yes
notify = no
emailserver = localhost
destaddress = user@localhost
"""
    ini = open(ini,'w')
    ini.write(iniText)
    ini.close()

def readIni(ini):
    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(ini,"r","utf-8"))
    product = []
    product.append(config.get('server','address'))
    product.append(config.get('server','bandwith'))
    product.append(config.get('server','timeout'))
    product.append(config.get('server','max_attempts'))
    product.append(config.get('server','localpath'))
    product.append(config.get('server','remotepath'))
    product.append(config.get('server','disabled'))
    product.append(config.get('server','log'))
    product.append(config.get('server','notify'))
    product.append(config.get('server','emailserver'))
    product.append(config.get('server','destaddress'))
    return product


class controlDB(object):
    def __init__(self,name):
        if not os.path.exists(name):
            try:
                self.conn = sqlite3.connect(name)
                self.cursor = self.conn.cursor()
                self.cursor.execute("""CREATE TABLE files
                                        (id INTEGER PRIMARY KEY, name text, lock Boolean)""")
                self.conn.commit()
            except sqlite3.Error, e:
                logging.info(e)
        else:
            try:
                self.conn = sqlite3.connect(name)
                self.cursor = self.conn.cursor()
                '''
                        Perhaps db is corrupt delete and create again, sorry.
                        You'll have to feed manually the database
                        invocating several times this script
                        with each file name lost.
                '''
            except sqlite3.Error:
                os.unlink(name)
                self.conn = sqlite3.connect(name)
                self.cursor = self.conn.cursor()

    def areThereLock(self):
        try:
            '''Is any other file in progress? '''
            self.cursor.execute("SELECT * from files where lock = 1")
            if self.cursor.fetchone() is None:
                return False
            else:
                return True
        except sqlite3.Error, e:
            logging.info(e)

    def insertTorrent(self,name,lock):
        try:
            ''' Insert torrent in db, return true if file is unique '''
            self.cursor.execute("SELECT * from files where name = ?",(name,))
            if self.cursor.fetchone() is not None:
                ''' archivo ya presente '''
                return False
            else:
                self.cursor.execute("INSERT into files (name,lock) VALUES (?,?)",(name,lock))
                self.conn.commit()
                return True
        except sqlite3.Error, e:
            logging.info(e)

    def  deleteTorrent(self):
        try:
            '''delete Torrent with lock'''
            self.cursor.execute("DELETE from files where lock = 1")
            self.conn.commit()
        except sqlite3.Error, e:
            logging.info(e)
    def acquireLock(self):
        try:
            '''
                    return next File to Download. If there is not any file
                    return false
            '''
            self.cursor.execute("SELECT * from files")
            nextTorrent = self.cursor.fetchone()
            #print "Next torrent is: " +str(nextTorrent[0]) +" "+ nextTorrent[1]
            if nextTorrent is None:
                return False
            else:
                self.cursor.execute("UPDATE files set lock = 1 where id =?",(nextTorrent[0],))
                self.conn.commit()
                return nextTorrent[1]
        except sqlite3.Error, e:
            logging.info(e)

    def fileExists(self,name):
        try:
            self.cursor.execute("SELECT * from files where name = ?",(name,))
            if self.cursor.fetchone() is None:
                return False
            else:
                return True
        except sqlite3.Error, e:
            logging.info(e)

    def __del__(self):
        self.conn.commit()
        self.conn.close()

def send_email(recipient, subject, text, srv):
    """ Send an email"""
    sender = "tx@localhost"
    msg = MIMEText(text, 'plain')
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    try:
        smtp = SMTP(srv)
        smtp.sendmail(sender,recipient,msg.as_string())
        return True
    except Exception:
        return False
    finally:
        smtp.quit()

def main():
    """ First execution of this program will start downloading files until
        there is not any file waiting to  transfer.
        Next executions only feed the database """
    sleepInterval = 300 #secs between retries if transfer fail
    inifile = 'tx.ini'
    dbfile =  'tx.db'
    server = None
    bwith =  None
    bandwith = None
    timeout = None
    attempts = None
    localpath = None
    remotepath = None
    disabled = None
    log = None
    notify = None
    emailserver = None
    destaddress = None
    pgram = "rsync"
    lockfile = 'tx.lock'
    logfile = 'tx.log'

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        import sqlite3
        path=os.getenv('PATH')
        ok = False
        for p in path.split(os.path.pathsep):
            p=os.path.join(p,pgram)
            if os.path.exists(p) and os.access(p,os.X_OK):
                ok = True
                pgram = p
        if not ok:
            raise Exception("Rsync must be in the execution path")

    except ImportError, e:
        print "Module python sqlite must be installed"
        sys.exit(2)
    except Exception, e:
        print e
        sys.exit(2)

    if not os.path.exists(inifile):
        createIni(inifile)
        print "Please modify tx.ini"
        sys.exit(2)

    p=readIni(inifile)
    server = p[0]; bwith = p[1]; timeout = p[2]; attempts = p[3]; localpath = p[4];
    remotepath = p[5]; disabled = p[6]; log = p[7]; notify = p[8]; emailserver = p[9]; destaddress = p[10];

    if disabled == "yes":
        print "TX is currently disabled. Please modify tx.ini"
        sys.exit(2)

    if log == "yes":
        logging.basicConfig(filename=logfile,level=logging.INFO,format='%(asctime)s %(message)s')

    if len(sys.argv) > 2:
        print "Use: " + sys.argv[0] + " file or directory to transfer."
        logging.info('Use: ' + sys.argv[0] + ' file or directory to transfer.')
        logging.shutdown()
        sys.exit(2)
    elif len(sys.argv) == 2:
        torrentfile = unicode(sys.argv[1],"utf-8")
        dB=controlDB(dbfile)
    else:
        #resume a previous failed transfer
        dB=controlDB(dbfile)
        torrentfile = dB.acquireLock()
        if not torrentfile:
	    logging.info('There are no files to transfer')
	    logging.shutdown()
	    sys.exit(2)


    if not os.path.exists(localpath+torrentfile):
                print "File to transfer must exist"
                logging.info('File to transfer must exist')
                logging.info('File asked is in ' + localpath+torrentfile)
                logging.shutdown()
                sys.exit(2)

    if dB.areThereLock():
        ''' If there is another transfer, only feed db '''
        if not dB.fileExists(torrentfile):
            dB.insertTorrent(torrentfile,0)
        '''
                If there are another instance exit, else continue.
                This lock is Linux OS based, whereas dB.areThereLock
                is only used to discern what file is transfering
        '''
        lock = open(lockfile, 'w')
        try:
            fcntl.lockf(lock , fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            logging.info('There is a file lock. Another instance will transfer the file')
            logging.shutdown()
            lock.close()
            sys.exit(0)
    else:
        lock = open(lockfile, 'w')
        try:
            fcntl.lockf(lock , fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            logging.info('Can not acquire file lock')
            logging.shutdown()
            lock.close()
            sys.exit(0)
        fcntl.lockf(lock , fcntl.LOCK_EX | fcntl.LOCK_NB)
        dB.insertTorrent(torrentfile,1)

    r = True
    error = 0
    while r:
        ''' Check if the file is still waiting '''
        try:
            logging.info('Trying to transmit '+ torrentfile)
            subprocess.check_call([
                    pgram,
                    "--bwlimit="+bwith,
                    "--copy-links",
                    "--recursive",
                    "--partial",
                    "--log-file="+logfile,
                    "--rsh=ssh",
                    "--timeout="+timeout,
                    localpath+torrentfile,
                    server+":"+remotepath
                    ])
            logging.info('File '+ torrentfile + ' transmitted correctly')
            subprocess.check_call([
                    "ssh",
                    server,
                    "chmod -R 777",
                    remotepath + re.escape(torrentfile)
                    ])
            logging.info('File '+ torrentfile + ' applied permissions.')
            dB.deleteTorrent()
            torrentfile=dB.acquireLock()

            if torrentfile is False:
                ''' All files has been transfered '''
                logging.info('All files has been transferred')
                break

        except subprocess.CalledProcessError, e:
            error += 1
            sleep (sleepInterval)
	    logging.info('Something weird happened '+ str(e))
            if error == int(attempts):
                r = False
                logging.info('Reached max attempts trying transfering '+ torrentfile)
                logging.info('Server is: '+ server )
                if notify == "yes":
                    msg = "["+str(datetime.datetime.now())+"]"+" Error transfering " +  torrentfile
                    if not send_email(destaddress,"[tx.py] Error transfering " + torrentfile, msg, emailserver):
                        logging.info('Something went wrong when trying to send an email')
                logging.shutdown()
                fcntl.lockf(lock , fcntl.LOCK_UN)
                lock.close()
                os.unlink(lockfile)
                sys.exit(2)
    logging.shutdown()
    fcntl.lockf(lock , fcntl.LOCK_UN)
    lock.close()
    os.unlink(lockfile)
    sys.exit(0)

if __name__ == "__main__":
    ''' Double fork is needed to avoid zombie processes '''
    ''' Is not neeeded here because we exit on parent fork '''
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print e
        sys.exit(1)
    main()
