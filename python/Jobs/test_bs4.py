#!/usr/bin/env python
# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import re
import urllib2
import os

url = "./directorio.html"
page = open(url)
soup = BeautifulSoup(page.read(),'html.parser')

''' 
	La estructura es una tabla con tres tablas descendientes directas
    y al mismo nivel.
    El objetivo es etiquetar la tabla 3 que es donde esta el listado de
    empresas
'''
tablas = ['primera','segunda','tercera']
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
tabla = soup.find_all('table',attrs={'class':'tercera'})
j=0
for i in soup.find_all('table'):
	print j
	j+=1

''' 
	Esto es mas rápido que todo lo anterior. Recuerda
	que las empresas son la última tabla. Por lo menos
	en la página 1 del índice.
'''
#print soup.find_all('table')[-1]

'''
	Ahora vamos a ver como sacamos el índice para ir iterando.
	EL índice está incluido en la tabla contenedora principal.
'''

indice = soup.find_all('table')[0].find_all('font')

print len(indice)






