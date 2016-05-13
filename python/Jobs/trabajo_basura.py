#!/usr/bin/env python
import sys
from urllib import urlencode
from urllib2 import urlopen, URLError, build_opener
from requests import session
from argparse import ArgumentParser
from bs4 import BeautifulSoup


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
    args = parser.parse_args()
    return args


def parse_table(table):
     results = []
     for i in table.find_all('tr'):
          tmp = []
          for j in i.find_all('td',attrs = {'class' : ['lin0','lin1']}):            
              print j.get_text()        
          print "****"
            #tmp.append(j.get_text())
            #print j.getText(separator='\t',strip=True)          	
#        results.append("\t".join(tmp))
     return "\n".join(results)
     
def main():
    # Get arguments
    args = parse_arguments()
    if (args.user) and (args.passw):        
        user = args.user
        passw = args.passw
  
  	directorio = 'http://www.trabajobasura.info/directorio/?pag='
    authurl = 'http://www.trabajobasura.info/ingresar.php'
    payload = {
    'action': 'ingresar.php',
    'emailF': user,
    'passwordF': passw }
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'    
	}

    sess = session()  
    sess.post(authurl, data=payload)
    
    try:   
          response = sess.get(directorio,headers=headers)
          soup = BeautifulSoup(response.content, 'html.parser' )
          try :
                 table = soup.find('table')
                 
                 datos = parse_table(table)
                 print datos
                                        
          except AttributeError as e:
                 print 'No tables found, exiting'
                 sys.exit(1)

    except Exception as e:
   		  print 'An error occured fetching trabajobasura table \n %s' % str(e)
   		  sys.exit(1)
   		  
if __name__ == '__main__':
    status = main()
    sys.exit(status)
