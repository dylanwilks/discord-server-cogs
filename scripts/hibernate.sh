#!/bin/sh

ARP_LINE="arp -a | grep '$1'"
ARP_LINE=$(eval "$ARP_LINE")
IP=$(echo $ARP_LINE | cut -d " " -f 2 | tr -d '()')

scp /usr/src/app/webhooks/$1/* $2@$IP:$3
scp /usr/src/app/message.sh $2@$IP:$4
ssh -f $2@$IP "nohup doas zzz -Z > /dev/null 2>&1 &"
