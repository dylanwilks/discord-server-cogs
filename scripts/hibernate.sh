#!/bin/sh

ARP_LINE="arp -a | grep '$1'"
ARP_LINE=$(eval "$ARP_LINE")
IP=$(echo $ARP_LINE | cut -d " " -f 2 | tr -d '()')

scp /root/discord-bot/webhooks/$1/* altar-pi@$IP:/home/altar-pi/discord-bot/webhooks/
ssh -f altar-pi@$IP "nohup doas zzz -Z > /dev/null 2>&1 &"
