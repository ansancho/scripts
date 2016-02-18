#!/usr/bin/env bash
file1=drop.lasso
file2=edrop.lasso
file3=top20.txt
outfile=/var/www/html/blacklist.rsc
uf1="http://www.spamhaus.org/drop/drop.lasso"
uf2="http://www.spamhaus.org/drop/edrop.lasso"
uf3="http://feeds.dshield.org/block.txt"
cd /var/www/html
wget --timeout=5 -q -O $file1 $uf1 || exit 1
wget --timeout=5 -q -O $file2 $uf2 || exit 1
wget --timeout=5 -q -O $file3 $uf3 || exit 1

rm -f $outfile.prev
cp $outfile $outfile.prev
> $outfile

awk --posix -v outfile=$outfile \
'BEGIN { 
	comm ="^#|^;|^$"             
	f12="^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}/[0-9]{1,2}"
	f3="^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}"
	rfc1918="^192.168.[0-9]{1,3}.[0-9]{1,3}|^172.16.[0-9]{1,3}.[0-9]{1,3}|^10.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}"
        all="0.0.0.0"
	file = 0
	print "/ip firewall address-list remove [/ip firewall address-list find  list='blacklist']" > outfile
}      
        
{	
	if (FNR==1){
		file++
	}
	if (match($0,comm)){
		next
	}
	if (match($0,rfc1918)){
                next
        }
        if (match($0,all)){
                next
        }
	if (file == 1){
		if (match($0,f12)){
			print "ip firewall address-list add list=blacklist address=" \
			substr($0,RSTART,RLENGTH) \
			" comment=spamHaus-DROP;" >> outfile 
		}
	} else if (file == 2){
		if (match($0,f12)){
                        print "ip firewall address-list add list=blacklist address=" \
                        substr($0,RSTART,RLENGTH) \
                        " comment=spamHaus-EDROP;" >> outfile 
                }
	}else{
		if (match($0,f3)){
                        print "ip firewall address-list add list=blacklist address=" \
                        substr($0,RSTART,RLENGTH) "/"$3 \
                        " comment=Dshield-top20;" >> outfile 
                }
	}
		
}       
        
END { 
	if(file!=3){
		print "Error de procesado: deberia haber 3 ficheros"
		print "" > outfile
		exit 1
	} else {
		exit 0
	}  
	
}' $file1 $file2 $file3
rm -f $file1 $file2 $file3
