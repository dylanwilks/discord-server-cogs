#!/bin/sh

ARP_LINE="arp -a | grep '$1'"
ARP_LINE=$(eval "$ARP_LINE")
if [ -z "$ARP_LINE" ]; then
	echo "Specified device not found."
	exit 1
fi

scp /usr/src/app/webhooks/$1/* $2@$1:$3
scp /usr/src/app/scripts/message.sh $2@$1:$4
ssh -f $2@$1 "nohup doas zzz -Z > /dev/null 2>&1 &"
