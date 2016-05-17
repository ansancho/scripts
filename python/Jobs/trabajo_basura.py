#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
from urllib import urlencode
from urllib2 import urlopen, URLError, build_opener
from requests import session, RequestException
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from time import sleep
import logging
import csv

'''
Global variables
'''
directorio = 'http://www.trabajobasura.info/directorio/'
authurl = 'http://www.trabajobasura.info/ingresar.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'    
}
params = {
    'action': 'ingresar.php',
    'emailF': "",
    'passwordF': ""
}


def parse_arguments():
    """ Process command line arguments """
    parser = ArgumentParser(description=
'Grabs full directory of companies  from http://trabajobasura.info and export them  to a csv file')    
    parser.add_argument('-u', '--user', 
    					help='Registered username. Necessary to retrieve the directory',
    					required=False)
    parser.add_argument('-p', '--passw',
    				    help='User password',
    				    required=False)
    parser.add_argument('-d','--debug', action='store_true',
    					help='Print debug messages',
    					required=False)
    parser.add_argument('-f','--file', nargs='?',
    					help='Output csv file, if ommitted then will be junkcs.csv',
    					required=False)
    parser.add_argument('-s','--sort',
                        choices=['r','R','p','P'],
                        default='r',
                        help="Sort companies by rate (r) or popularity (p) ",
                        required=False)
    args = parser.parse_args()
    return args


def parse_table(table):
    logger = logging.getLogger(__name__)
    results = []
    company = []
    for i in table.find_all('tr'):
            tmp = i.find_all('td')
            if tmp:
                #nombre de la empresa y enlace interno                
                a = tmp[0].find_all('a',href=True)
                for j in a:
                    company.append(j.getText().encode('utf-8'))
                    company.append(directorio+j['href'].encode('utf-8'))
                #votos
                company.append(float(tmp[1].getText()))
                #numero de comentarios - popularidad
                company.append(float(tmp[2].getText()))
                #Enlace externo
                a = tmp[3].find_all('a',href=True)
                if a:
                    for j in a:                    
                        company.append("http:"+j['href'].encode('utf-8'))
                else:
                    company.append("")
                results.append(company)                
                company = []
    return results           
     
def main():
    # Get arguments
    args = parse_arguments()
    logging.basicConfig()
    logger = logging.getLogger(__name__)    
    sess = session()
    if (args.user) and (args.passw):        
        params['emailF']= args.user
        params['passwordF'] = args.passw
        sess.post(authurl, data=params)
    if (args.debug):
    	logger.setLevel(logging.DEBUG)
    	logger.debug("Debug mode ON")
    else:
    	logger.setLevel(logging.INFO)
    if (args.file):
        logger.debug("Opening %s"%args.file)
        fichero = open(args.file,'w')
    else:
        logger.debug("Opening %s"%"junkcs.csv")
        fichero = open('junkcs.csv','w')
    excel   = csv.writer(fichero)
        
  
    

    try:        
        response = sess.get(directorio,headers=headers)
        soup = BeautifulSoup(response.content,'html.parser')
        ''' The index of directory pages are in the font tags '''
        index = len(soup.find_all('table')[0].find_all('font'))
        logger.debug("There are %s company pages to retrieve\n" % str(index))      
        
        tables = ""
        for i in range (1,index+1):
            logger.info("Procesando " + directorio+ "?pag=" + str(i))
            response = sess.get(directorio+ "?pag=" + str(i),headers=headers)
            soup = BeautifulSoup(response.content,'html.parser')
            tables += str(soup.find_all('table')[-1])
            ''' We do not want to make DDOS '''
            sleep (0.3)        
        listado = parse_table(BeautifulSoup(tables,'html.parser'))
        
        #ordenar por puntuacion o por popularidad
        if (args.sort == 'r') or (args.sort == 'R'):
            logger.debug("Ordering by rating")
            listado.sort(key=lambda x: x[2], reverse=True)
        else:
            logger.debug("Ordering by popularity")
            listado.sort(key=lambda x: x[3], reverse=True)
            
        excel.writerow(['Name','Database link','Rating','Votes','Company external link'])
        excel.writerows(listado)
        fichero.close()
        sys.exit(1)
        
        
    except RequestException as sessionError:
        logger.debug('An error occured fetching trabajobasura.info page \n %s\n' % str(sessionError))
        sys.exit(1)
    except Exception as e:
        logger.debug( 'An error occured\n %s\n' % str(e),exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    status = main()
    sys.exit(status)
