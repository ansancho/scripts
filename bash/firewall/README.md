Use
---

ipv4-linux.sh is a ipv4 script to generate a simple iptables 
ruleset. It also use blacklist rules from spamhaus and
dshield servers.

Put the script in some directory and create a crontab job
to periodically refresh the blacklists.

There is also another script, adapted to routeros firewalls. Simply,
transfer the generated output file to the router and ban traffic from
the "blacklist" list.
