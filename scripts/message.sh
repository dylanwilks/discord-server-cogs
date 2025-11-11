#!/bin/sh

WEBHOOK_URL="cat $1"
WEBHOOK_URL=$(eval "$WEBHOOK_URL")

send_message() {
	local message=$1
	local payload=$(cat <<EOF
	{
	"content": "$message"
	}
EOF
)
	curl -H "Content-Type: application/json" -X POST -d "$payload" $WEBHOOK_URL
}
