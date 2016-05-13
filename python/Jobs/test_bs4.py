#!/usr/bin/env python
# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import re
import urllib2
import os
from requests import session
import time

#url = "./directorio2.html"
directorio = 'http://www.trabajobasura.info/directorio/'
authurl = 'http://www.trabajobasura.info/ingresar.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'    
}
payload = {
 'action': 'ingresar.php',
 'emailF': 'u@pepe.es',
 'passwordF': 'pepe'
}
#page = open(url)
sess = session()
sess.post(authurl, data=payload)
response = sess.get(directorio,headers=headers)
soup = BeautifulSoup(response.content,'html.parser')
indice = len(soup.find_all('table')[0].find_all('font'))

for i in range(2,indice+1):
	response = sess.get(directorio+ "?pag=" + str(i),headers=headers)
	soup = BeautifulSoup(response.content,'html.parser')
	print "*******************"
	print soup.find_all('table')[-1]
	print "*******************"
	time.sleep(1)
	
	
''' 
	La estructura es una tabla con tres tablas descendientes directas
    y al mismo nivel.
    El objetivo es etiquetar la tabla 3 que es donde esta el listado de
    empresas
'''
'''tablas = ['primera','segunda','tercera']
l = 0
for i in soup.table.children:
	if hasattr(i, 'children'):
		for j in i.children:
			if hasattr(j, 'children'):				
				for k in j.children:					
					if k.name == 'table':											
						k['class']=tablas[l]
						print k['class']
						l+=1
tabla = soup.find_all('table',attrs={'class':'tercera'})'''
'''j=0
for i in soup.find_all('table'):
	print j
	j+=1'''

''' 
	Esto es mas rápido que todo lo anterior. Recuerda
	que las empresas son la última tabla. Por lo menos
	en la página 1 del índice.
'''
'''print soup.find_all('table')[-1]'''

'''
	Ahora vamos a ver como sacamos el índice para ir iterando.
	EL índice está incluido en la tabla contenedora principal.
'''



'''print indice'''






