#!/usr/bin/env bash

# load variables from config file
source "$(dirname ${BASH_SOURCE[0]})/config.sh"

goal clerk send \
    -a 1 \
    -f "$SIGNATURE_ADDRESS" \
    -t "$BENEFICIARY_ADDRESS" \
    -F "$COMPILED_TEAL_PATH" \
    --argb64 "$(echo -n "$PASSWORD_ATTEMPT" | base64 -w0)"
