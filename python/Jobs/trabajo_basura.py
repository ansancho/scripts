#!/usr/bin/env python
import sys
from urllib import urlencode
from urllib2 import urlopen, URLError, build_opener
from requests import session, RequestException
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from time import sleep
import logging

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
    		'Grabs full directory of companies from http://trabajobasura.info')    
    parser.add_argument('-u', '--user', 
    					help='Registered username. Necessary to retrieve the directory',
    					required=True)
    parser.add_argument('-p', '--passw',
    				    help='User password',
    				    required=True)
    parser.add_argument('-d','--debug',                        
    					help='Print debug messages, write something like true or True',
    					required=False)
    args = parser.parse_args()
    return args


def parse_table(table):
     results = []
     for i in table.find_all('tr'):
          tmp = []
          for j in i.find_all('td',attrs = {'class' : ['lin0','lin1']}):            
              print j.get_text()        
          print "****"
     return "\n".join(results)
     
def main():
    # Get arguments
    args = parse_arguments()
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    if (args.user) and (args.passw):        
        params['emailF']= args.user
        params['passwordF'] = args.passw
    if (args.debug):
    	logger.setLevel(logging.DEBUG)
    else:
    	logger.setLevel(logging.INFO)
  
    

    try:
        sess = session()  
        sess.post(authurl, data=params)
        response = sess.get(directorio,headers=headers)
        soup = BeautifulSoup(response.content,'html.parser')
        ''' The index of directory pages are in the font tags '''
        index = len(soup.find_all('table')[0].find_all('font'))
        logger.debug(index)
        
        tables = ""
        for i in range (1,3):
            logger.info("Procesando " + directorio+ "?pag=" + str(i))
            response = sess.get(directorio+ "?pag=" + str(i),headers=headers)
            soup = BeautifulSoup(response.content,'html.parser')
            tables += str(soup.find_all('table')[-1])
            ''' We do not want to make DDOS '''
            sleep (0.5)
        soupTables=BeautifulSoup(tables,'html.parser')
      
        '''		
            for i in range(2,indice):
			response = sess.get(directorio+ "?pag=" + str(i),headers=headers)
			soup = BeautifulSoup(response.content,'html.parser')
        '''

    except RequestException as sessionError:
        logger.info('An error occured fetching trabajobasura.info page \n %s\n' % str(sessionError))
        sys.exit(1)
    except Exception as e:
        logger.info( 'An error occured\n %s\n' % str(e),exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    status = main()
    sys.exit(status)
