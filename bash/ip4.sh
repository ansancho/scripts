#!/bin/bash
file1=/tmp/drop.lasso
file2=/tmp/edrop.lasso
file3=/tmp/top20.txt
uf1="http://www.spamhaus.org/drop/drop.lasso"
uf2="http://www.spamhaus.org/drop/edrop.lasso"
uf3="http://feeds.dshield.org/block.txt"

#si wget no descargó nada salimos.
wget --timeout=5 --quiet $uf1 -O $file1 || exit 1
wget --timeout=5 --quiet $uf2 -O $file2 || exit 1
wget --timeout=5 --quiet $uf3 -O $file3 || exit 1


#Limpiamos
iptables -F
#Borra cadenas personalizadas
iptables -X
#Borra todas las reglas de todas las cadenas
iptables -F
#Reinicionamos politicas.
iptables -P FORWARD ACCEPT
iptables -P INPUT   ACCEPT
iptables -P OUTPUT  ACCEPT


# creacion de cadenas
#Creamos CADENA personalizada para LOG
iptables -N LOGDROP
iptables -N TEST
# log null scan
#iptables -A LOGDROP -p tcp --tcp-flags ALL NONE -m limit --limit 30/min -j LOG --log-prefix "firewall - Denied TCP4 - Null scam:" --log-level debug
iptables -A LOGDROP -p tcp -m limit --limit 30/min -j LOG --log-prefix "firewall - Denied TCP4: " --log-level debug
iptables -A LOGDROP -p udp -m limit --limit 30/min -j LOG --log-prefix "firewall - Denied UDP4: " --log-level debug
iptables -A LOGDROP -p icmp -m limit --limit 30/min -j LOG --log-prefix "firewall - Denied ICMP4: " --log-level debug
iptables -A LOGDROP -j DROP

#Creamos CADENA personalizada para spamhaus edrop list
iptables -N SPAMHAUS
iptables -A SPAMHAUS -p tcp -m limit --limit 30/min -j LOG --log-prefix "SPAMHAUS - TCP4: " --log-level debug
iptables -A SPAMHAUS -p udp -m limit --limit 30/min -j LOG --log-prefix "SPAMHAUS - UDP4: " --log-level debug
iptables -A SPAMHAUS -p icmp -m limit --limit 30/min -j LOG --log-prefix "SPAMHAUS - ICMP4: " --log-level debug
iptables -A SPAMHAUS -j DROP

#Creamos CADENA personalizada para LOG_invalido
iptables -N ILOGDROP
iptables -A ILOGDROP -m limit --limit 120/min -j LOG --log-prefix "firewall - Denied Invalid4:" --log-level debug
iptables -A ILOGDROP -j DROP

#Creamos CADENA personalizada para ACCEPTS No en uso por defecto.
iptables -N LOGACCEPT
iptables -A LOGACCEPT -m limit --limit 120/min -j LOG --log-prefix "firewall - Accept4:" --log-level debug
iptables -A LOGACCEPT -j ACCEPT


#Deshabilitamos reenvio mediante policita por defecto.
iptables -A FORWARD -j LOG --log-prefix "firewall - FWD Denied4:" --log-level debug
iptables -A FORWARD -j DROP

#icmpflood
iptables -N ICMPFLOOD
iptables -A ICMPFLOOD -m recent --set --name ICMP
iptables -A ICMPFLOOD -m recent --update --seconds 11 --hitcount 20 --name ICMP --rttl -j LOG --log-prefix "firewall[ICMP-flood]: " --log-level debug
iptables -A ICMPFLOOD -m recent --update --seconds 11 --hitcount 20 --name ICMP --rttl -j DROP
iptables -A ICMPFLOOD -j ACCEPT

#ssh flood 3 conexiones permitidas cada 5 segundos
iptables -N SSHBRUTE
iptables -A SSHBRUTE -m recent --name SSH --set
iptables -A SSHBRUTE -m recent --name SSH --update --rttl --seconds 6 --hitcount 5 -j LOG --log-prefix "firewall[SSH-brute]: " --log-level debug
iptables -A SSHBRUTE -m recent --name SSH --update --rttl --seconds 6 --hitcount 5 -j DROP
iptables -A SSHBRUTE -j ACCEPT

#dns flood cada 15 segundos permitidas 15 consultas
iptables -N DNSFLOOD
iptables -A DNSFLOOD -m recent --name DNS --set
iptables -A DNSFLOOD -m recent --name DNS --update --rttl --seconds 30 --hitcount 15 -m limit --limit 1/second --limit-burst 15 -j LOG --log-prefix "firewall[DNS-Flood]: "
iptables -A DNSFLOOD -m recent --name DNS --update --rttl --seconds 30 --hitcount 15 -j DROP
iptables -A DNSFLOOD -j ACCEPT

#smtp FLOOD permitidos 15 correos en 30 segundos
iptables -N SMTPFLOOD
iptables -A SMTPFLOOD -m recent --name SMTP --set
iptables -A SMTPFLOOD -m recent --name SMTP --update --rttl --seconds 30 --hitcount 15 -m limit --limit 1/second --limit-burst 15 -j LOG --log-prefix "firewall[SMTP-brute]: "
iptables -A SMTPFLOOD -m recent --name SMTP --update --rttl --seconds 30 --hitcount 15 -j DROP
iptables -A SMTPFLOOD -j ACCEPT

#imap flood 
iptables -N IMAPFLOOD
iptables -A IMAPFLOOD -m recent --name IMAP --set
iptables -A IMAPFLOOD -m recent --name IMAP --update --rttl --seconds 30 --hitcount 15 -m limit --limit 1/second --limit-burst 15 -j LOG --log-prefix "firewall[IMAP-brute]: "
iptables -A IMAPFLOOD -m recent --name IMAP --update --rttl --seconds 30 --hitcount 15 -j DROP
iptables -A IMAPFLOOD -j ACCEPT

#https flood
iptables -N HTTPSFLOOD
iptables -A HTTPSFLOOD -m recent --name HTTPS --set
iptables -A HTTPSFLOOD -m recent --name HTTPS --update --rttl --seconds 30 --hitcount 15 -m limit --limit 1/second --limit-burst 15 -j LOG --log-prefix "firewall[HTTPS-brute]: "
iptables -A HTTPSFLOOD -m recent --name HTTPS --update --rttl --seconds 30 --hitcount 15 -j DROP
iptables -A HTTPSFLOOD -j ACCEPT

#http flood
iptables -N HTTPFLOOD
iptables -A HTTPFLOOD -m recent --name HTTP --set
iptables -A HTTPFLOOD -m recent --name HTTP --update --rttl --seconds 30 --hitcount 15 -m limit --limit 1/second --limit-burst 15 -j LOG --log-prefix "firewall[HTTP-brute]:"
iptables -A HTTPFLOOD -m recent --name HTTP --update --rttl --seconds 30 --hitcount 15 -j DROP
iptables -A HTTPFLOOD -j ACCEPT


#Entrada
#acceptamos paquetes de conexiones ya establecidas sin LOGGING
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
#aceptamos localhost sin log
iptables -A INPUT -i lo -j ACCEPT

#BLOQUEO IPS problematicas
#http://www.spamhaus.org/drop/drop.lasso

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


#filtrado de broadcasts sin LOGGING
iptables -A INPUT -m addrtype --dst-type broadcast -j DROP
#filtrado de multicasts sin LOGGING
iptables -A INPUT -m addrtype --dst-type multicast -j DROP
#anycast
iptables -A INPUT -m addrtype --dst-type anycast -j DROP
iptables -A INPUT -d 224.0.0.0/4 -j DROP




#filtrado de paquetes que dicen que vienen de loopback
iptables -A INPUT -s 127.0.0.0/8 ! -i lo -j DROP
#paquetes inválidos
iptables -A INPUT -m conntrack --ctstate INVALID -j ILOGDROP
#null scan
#iptables -A INPUT -p tcp --tcp-flags ALL NONE -j LOGDROP

#ping con flood
iptables -A INPUT -p icmp -m icmp --icmp-type 8 -j ICMPFLOOD
#ping sin flood
#iptables -A INPUT -p icmp -m icmp --icmp-type 8 -j ACCEPT
#dns
iptables -A INPUT -p udp -m state --state NEW --dport 53 -j DNSFLOOD
iptables -A INPUT -p tcp -m state --state NEW --dport 53 -j DNSFLOOD
#ntp
iptables -A INPUT -p udp -m state --state NEW --dport 123 -j ACCEPT
#ssh con brute force
iptables -A INPUT -p tcp -m state --state NEW --dport 22 -j SSHBRUTE
#ssh sin brute force chain
#iptables -A INPUT -p tcp -m state --state NEW --dport 22 -j LOGACCEPT
#smtp
iptables -A INPUT -p tcp -m state --state NEW --dport 25 -j SMTPFLOOD
#http
iptables -A INPUT -p tcp -m state --state NEW --dport 80 -j HTTPFLOOD
#imap
iptables -A INPUT -p tcp -m state --state NEW --dport 143 -j IMAPFLOOD
#https
iptables -A INPUT -p tcp -m state --state NEW --dport 443 -j HTTPSFLOOD
#rtorrent
iptables -A INPUT -p tcp -m state --state NEW --dport 35555 -j ACCEPT
#iptables -A INPUT -p udp -m state --state NEW --dport 49164 -j ACCEPT
#todo lo demas al agujero negro
iptables -A INPUT -j LOGDROP
/etc/init.d/fail2ban restart
exit 0;
