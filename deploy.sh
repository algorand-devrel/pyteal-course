#!/bin/bash
# Run with arguments: <global byteslices> <global ints> <local byteslices> <local ints>

goal app create --creator $ONE --approval-prog /data/build/approval.teal --clear-prog /data/build/clear.teal --global-byteslices $1 --global-ints $2 --local-byteslices $3 --local-ints $4