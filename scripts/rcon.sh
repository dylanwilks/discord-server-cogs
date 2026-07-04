#!/bin/sh

ssh $5@$1 "doas -u $2 sh -c '(
	cd ~;
	podman exec $3 rcon-cli $4 
)'"
