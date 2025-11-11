#!/bin/sh

ssh altar-pi@altar-server "doas -u $1 sh -c '(
	cd ~;
	podman exec $2 rcon-cli $3 
)'"
