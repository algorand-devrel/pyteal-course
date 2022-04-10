#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

# create challenge transaction
goal app call \
    --app-id "$APP_ID" \
    -f "$CHALLENGER_ACCOUNT" \
    --app-account "$OPPONENT_ACCOUNT" \
    --app-arg "str:challenge" \
    --app-arg "b64:$CHALLENGE_B64" \
    -o challenge-call.tx

# create wager transaction
goal clerk send \
    -a "$WAGER" \
    -t "$APP_ACCOUNT" \
    -f "$CHALLENGER_ACCOUNT" \
    -o challenge-wager.tx

# group transactions
cat challenge-call.tx challenge-wager.tx > challenge-combined.tx
goal clerk group -i challenge-combined.tx -o challenge-grouped.tx
goal clerk split -i challenge-grouped.tx -o challenge-split.tx

# sign individual transactions
goal clerk sign -i challenge-split-0.tx -o challenge-signed-0.tx
goal clerk sign -i challenge-split-1.tx -o challenge-signed-1.tx

# re-combine individually signed transactions
cat challenge-signed-0.tx challenge-signed-1.tx > challenge-signed-final.tx

# send transaction
goal clerk rawsend -f challenge-signed-final.tx
