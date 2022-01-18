#!/usr/bin/env bash

APP_ID=14
APP_ACCOUNT="LQRH3CW2MZGN2TOCTVBOOJVS42BZZKJ5PML6BPABTU4M7QULXOQNSZDO6E"
CHALLENGER_ACCOUNT="IJ3G6V2QVF5FATT724TDL3FL6GJQ3OKMA3EWLB56EVRSPYMSUI4LL5P4YE"
WAGER=123456
OPPONENT_ACCOUNT="PNATILPEKI5NCL6N5SAHFBQR76SERK3ZB6TBSU2K3RZU3QAZB5VBIR6AIU"
OPPONENT_REVEAL="p"

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
