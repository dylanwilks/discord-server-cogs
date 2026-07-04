#!/bin/sh

ARP_LINE="arp -a | grep '$1'"
ARP_LINE=$(eval "$ARP_LINE")
if [ -z "$ARP_LINE" ]; then
	echo "Specified device not found."
	exit 1
fi

#IP="$ARP_LINE" | cut -d " " -f 2 | tr -d '()'
MAC=$(echo $ARP_LINE | cut -d " " -f 4)

wakeonlan -i $2 $MAC
