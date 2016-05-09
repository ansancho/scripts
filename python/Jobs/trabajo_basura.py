#!/usr/bin/env python
import sys
from urllib import urlencode
from urllib2 import urlopen, URLError, build_opener
from requests import session
from argparse import ArgumentParser
from bs4 import BeautifulSoup


def parse_arguments():
    """ Process command line arguments """
    parser = ArgumentParser(description='Grabs tables from html')
    parser.add_argument('-u', '--url', help='url to grab from',
                        required=True)
    parser.add_argument('-U', '--user', 
    					help='Registered username. Necessary to retrieve the directory',
    					required=True)
    parser.add_argument('-P', '--passw',
    				    help='User password',
    				    required=True)    					
    args = parser.parse_args()
    return args


def parse_rows(rows):
    """ Get data from rows """
    results = []
    for row in rows:
        #table_headers = row.find_all('th')
        #if table_headers:
        #    results.append([headers.get_text() for headers in table_headers])		
        table_data = row.find_all('td',attrs = {'class' : ['lin0','lin1']})
        #table_data = row.find_all('td')
        if table_data:
            results.append([data.get_text() for data in table_data])
    return results


def main():
    # Get arguments
    args = parse_arguments()
    if (args.url) and (args.user) and (args.passw):
        url = args.url
        user = args.user
        passw = args.passw
  
    payload = {
    'action': 'ingresar.php',
    'emailF': user,
    'passwordF': passw }

    sess = session()  
    sess.post('http://www.trabajobasura.info/ingresar.php', data=payload)
    try:   
          response = sess.get('http://www.trabajobasura.info/directorio/')
          soup = BeautifulSoup(response.content, 'html.parser' )          
          try :
                 tabla = soup.find('table')
                
                 rows = tabla.find_all('tr')
                 table_data = parse_rows(rows)
                 for i in table_data:
                      print '\t'.join(i)
                       
          except AttributeError as e:
                 print 'No tables found, exiting'
                 sys.exit(1)

    except Exception as e:
   		  print 'An error occured fetching %s \n %s' % (url, str(e))
   		  sys.exit(1)
   		  
if __name__ == '__main__':
    status = main()
    sys.exit(status)
