#!/bin/bash
#########################################################
# This script is intended to create a simple iptables
# ruleset to protect most of servers.
# If you want black lists it needs GNU awk not Mawk.
# It also need to have installed wget.
#########################################################

if [ "$UID" -ne 0 ]; then
        echo "You must be administrator to run $0"
        exit 1;
fi

#Configure this if you want to use blacklists
BLACKLISTS=1

#tmp files
file1=/tmp/drop.lasso
file2=/tmp/edrop.lasso
file3=/tmp/top20.txt
#URL of most used black lists
uf1="http://www.spamhaus.org/drop/drop.lasso"
uf2="http://www.spamhaus.org/drop/edrop.lasso"
uf3="http://feeds.dshield.org/block.txt"

#anti-flood
#if its configured then traffic becoming from
#offender IP it is blocked if it generates more
#than 15 new connections in 30 seconds
FLOOD=1

#unicast traffic only
UNICAST=1

#Ssh brute
#it blocks ssh connections if offender IP generates
#more than 5 new connections in 6 seconds
SSHBRUTE=1

#Disable forwarding
FORWARDING=0

#List of allowed tcp ports
tcp4_ports=(22 25 53 80 143 443 35555)

#List of allowed udp ports
udp4_ports=(53 123)

#List of available ICMP types
icmp4_types=(8)


#Cleaning up
iptables -F
iptables -X
iptables -F
#Default policy rule
iptables -P FORWARD ACCEPT
iptables -P INPUT   ACCEPT
iptables -P OUTPUT  ACCEPT

#Default chains
iptables -N LOGDROP
iptables -A LOGDROP -p tcp -m limit --limit 30/min -j LOG --log-prefix "firewall - Denied TCP4: " --log-level debug
iptables -A LOGDROP -p udp -m limit --limit 30/min -j LOG --log-prefix "firewall - Denied UDP4: " --log-level debug
iptables -A LOGDROP -p icmp -m limit --limit 30/min -j LOG --log-prefix "firewall - Denied ICMP4: " --log-level debug
iptables -A LOGDROP -j DROP


if [ $BLACKLISTS -eq 1 ]; then
	iptables -N SPAMHAUS
	iptables -A SPAMHAUS -p tcp -m limit --limit 30/min -j LOG --log-prefix "SPAMHAUS - TCP4: " --log-level debug
	iptables -A SPAMHAUS -p udp -m limit --limit 30/min -j LOG --log-prefix "SPAMHAUS - UDP4: " --log-level debug
	iptables -A SPAMHAUS -p icmp -m limit --limit 30/min -j LOG --log-prefix "SPAMHAUS - ICMP4: " --log-level debug
	iptables -A SPAMHAUS -j DROP
fi

iptables -N ILOGDROP
iptables -A ILOGDROP -m limit --limit 120/min -j LOG --log-prefix "firewall - Denied Invalid4:" --log-level debug
iptables -A ILOGDROP -j DROP

iptables -N LOGACCEPT
iptables -A LOGACCEPT -m limit --limit 120/min -j LOG --log-prefix "firewall - Accept4:" --log-level debug
iptables -A LOGACCEPT -j ACCEPT


#Deshabilitamos reenvio mediante policita por defecto.
if [ $FORWARDING -eq 0 ]; then
	echo 0 > /proc/sys/net/ipv4/ip_forward	
	iptables -A FORWARD -j LOG --log-prefix "firewall - FWD Denied4:" --log-level debug
	iptables -A FORWARD -j DROP
fi

if [ $SSHBRUTE -eq 1 ]; then
	iptables -N SSHBRUTE
	iptables -A SSHBRUTE -m recent --name SSH --set
	iptables -A SSHBRUTE -m recent --name SSH --update --rttl --seconds 6 --hitcount 5 -j LOG --log-prefix "firewall[SSH-brute]: " --log-level debug
	iptables -A SSHBRUTE -m recent --name SSH --update --rttl --seconds 6 --hitcount 5 -j DROP
	iptables -A SSHBRUTE -j ACCEPT
fi

if [ $FLOOD -eq 1 ]; then
	iptables -N FLOOD
	iptables -A FLOOD -m recent --name FLOOD --set
	iptables -A FLOOD -m recent --name FLOOD --update --rttl --seconds 30 --hitcount 15 -m limit --limit 1/second --limit-burst 15 -j LOG --log-prefix "[FLOOD]:"
	iptables -A FLOOD -m recent --name FLOOD --update --rttl --seconds 30 --hitcount 15 -j DROP
	iptables -A FLOOD -j ACCEPT
fi

#Accept stablished connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
#Accept connections coming from our loopback interface
iptables -A INPUT -i lo -j ACCEPT


if [ $BLACKLISTS -eq 1 ]; then
	KO=0
	#si wget no descargó nada salimos.
	wget --timeout=5 --quiet $uf1 -O $file1 || KO=1
	wget --timeout=5 --quiet $uf2 -O $file2 || KO=1
	wget --timeout=5 --quiet $uf3 -O $file3 || KO=1

	if [ $KO -eq 0 ]; then

		awk --posix \
			'BEGIN { 
				comm ="^#|^;|^$"             
				f12="^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}/[0-9]{1,2}"
				f3="^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}"
				rfc1918="^192.168.[0-9]{1,3}.[0-9]{1,3}|^172.16.[0-9]{1,3}.[0-9]{1,3}|^10.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}"
				all="0.0.0.0"
				file = 0
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
						system("iptables -A INPUT -s " substr($0,RSTART,RLENGTH) " -j SPAMHAUS -m comment --comment Spamhaus-drop")
				}
				} else if (file == 2){
					if (match($0,f12)){
						system("iptables -A INPUT -s " substr($0,RSTART,RLENGTH) " -j SPAMHAUS -m comment --comment Spamhaus-edrop")
					}	
				}else{
				if (match($0,f3)){
						system("iptables -A INPUT -s " substr($0,RSTART,RLENGTH) " -j SPAMHAUS -m comment --comment Dshield-top20")
					}
				}
			}

			END { 
				if(file!=3){
					print "Error de procesado: deberia haber 3 ficheros"
					exit 1
			} else {
					exit 0
			}  
		
			}' $file1 $file2 $file3
		rm -f $file1 $file2 $file3
	else
		echo "The black lists could not been downloaded"
	fi		
fi

if [ $UNICAST -eq 1 ]; then

	#filtrado de broadcasts sin LOGGING
	iptables -A INPUT -m addrtype --dst-type broadcast -j DROP
	#filtrado de multicasts sin LOGGING
	iptables -A INPUT -m addrtype --dst-type multicast -j DROP
	#anycast
	iptables -A INPUT -m addrtype --dst-type anycast -j DROP
	iptables -A INPUT -d 224.0.0.0/4 -j DROP

fi


#Filtering of packets coming from internet but not generated in loopback interface
iptables -A INPUT -s 127.0.0.0/8 ! -i lo -j DROP
#Filtering invalid packets
iptables -A INPUT -m conntrack --ctstate INVALID -j ILOGDROP
#Filtering of null scan
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j LOGDROP

for i in ${icmp4_types[@]}; do
	if [ $FLOOD -eq 1 ]; then
		iptables -A INPUT -p icmp -m icmp --icmp-type $i -j FLOOD
	else
		iptables -A INPUT -p icmp -m icmp --icmp-type $i -j ACCEPT
	fi
done

for i in ${tcp4_ports[@]}; do
        if [ $FLOOD -eq 1 ]; then
		if [ $i -eq 22 ] && [ $SSHBRUTE -eq 1 ]; then
			iptables -A INPUT -p tcp -m state --state NEW --dport $i -j SSHBRUTE
		else
			iptables -A INPUT -p tcp -m state --state NEW --dport $i -j FLOOD
		fi
        else
			iptables -A INPUT -p tcp -m state --state NEW --dport $i -j ACCEPT
        fi
done


for i in ${udp4_ports[@]}; do
        if [ $FLOOD -eq 1 ]; then
        	iptables -A INPUT -p udp -m state --state NEW --dport $i -j FLOOD
        else
        	iptables -A INPUT -p udp -m state --state NEW --dport $i -j ACCEPT
        fi
done

#Deny everything else
iptables -A INPUT -j LOGDROP

if [ ! `pgrep fail2ban`  ]; then
	/etc/init.d/fail2ban restart
fi

exit 0;
