#!/usr/bin/env python

from bs4 import BeautifulSoup
import re
import urllib2
import os

url = "./directorio.html"
page = open(url)
soup = BeautifulSoup(page.read(),'html.parser')


