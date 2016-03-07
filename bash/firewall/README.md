Use
---

-ipv4-linux.sh is a ipv4 script to generate a simple iptables 
ruleset. It also use blacklist rules from spamhaus and
dshield servers. You can also add banned IPs to another 
optional file called blacklisted.custom. The format of that file is:

 CIDR #comment

-In order to work it needs GNU awk, because regex posix intervals are
not supported in mawk.

-Put the script in some directory and create a crontab job
to periodically refresh the blacklists.

-There is also another script, adapted to routeros firewalls. To use it 
simply transfer the generated output file to the router and ban traffic 
from the "blacklist" list.
