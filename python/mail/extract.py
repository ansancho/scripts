#!/usr/bin/env python
#-*- coding: utf8 -*-
import email
import sys

def main():
	if len(sys.argv) != 2:
		print "Use: " + sys.argv[0] + " RFC822 file."
		sys.exit(1)
	m = email.message_from_file(open(sys.argv[1],"r")).get_payload()
	if len(m) > 0:
		for i in m:
			if ("application" in i.get_content_type()):
				open(i.get_filename(), 'wb').write(i.get_payload(decode=True))
	
		
		
if __name__ == "__main__":
        main()
