#!/bin/sh

if [ -n "${PRIVATE_KEYS}" ]; then
    keychain --dir . $PRIVATE_KEYS
    . .keychain/$HOSTNAME-sh
fi

python3 main.py
