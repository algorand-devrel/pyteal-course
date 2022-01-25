#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# create accept transaction
goal app call \
    --app-id "$APP_ID" \
    -f "$OPPONENT_ACCOUNT" \
    --app-account "$CHALLENGER_ACCOUNT" \
    --app-arg "str:accept" \
    --app-arg "str:$OPPONENT_REVEAL" \
    -o accept-call.tx

# create wager transaction
goal clerk send \
    -a "$WAGER" \
    -t "$APP_ACCOUNT" \
    -f "$OPPONENT_ACCOUNT" \
    -o accept-wager.tx

# group transactions
cat accept-call.tx accept-wager.tx > accept-combined.tx
goal clerk group -i accept-combined.tx -o accept-grouped.tx
goal clerk split -i accept-grouped.tx -o accept-split.tx

# sign individual transactions
goal clerk sign -i accept-split-0.tx -o accept-signed-0.tx
goal clerk sign -i accept-split-1.tx -o accept-signed-1.tx

# re-combine individually signed transactions
cat accept-signed-0.tx accept-signed-1.tx > accept-signed-final.tx

# send transaction
goal clerk rawsend -f accept-signed-final.tx
