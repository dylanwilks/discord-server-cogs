#!/bin/sh

ARP_LINE="arp -a | grep '$1'"
ARP_LINE=$(eval "$ARP_LINE")
if [ -z "$ARP_LINE" ]; then
	echo "Specified device not found."
	exit 1
fi

#IP="$ARP_LINE" | cut -d " " -f 2 | tr -d '()'
BROADCAST="192.168.0.255"
MAC=$(echo $ARP_LINE | cut -d " " -f 4)

wakeonlan -i $BROADCAST $MAC
