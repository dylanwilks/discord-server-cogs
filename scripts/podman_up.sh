#!/bin/sh

ARP_LINE="arp -a | grep '$1'"
ARP_LINE=$(eval "$ARP_LINE")
if [ -z "$ARP_LINE" ]; then
	echo "Specified device not found."
	exit 1
fi

echo "Starting server $2..."
ssh altar-pi@$1 "doas -u $2 sh -c '(
	cd ~;
	podman-compose up -d
)'"
