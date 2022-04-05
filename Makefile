# PURE PYTHON:
CONTRACT = contracts.counter.step_01
compile:
	./build.sh $(CONTRACT)

# BRIDGE INTO algod:
SANDBOX = ../pyteal-course-sandbox/sandbox
enter-algod:
	$(SANDBOX) enter algod


# INSIDE algod:

# EG:
# make enter-algod
#> cd /data
#> make ... pick from the commands below ...

accounts:
	goal account list


# the next one only works if you use
# the following eval "trick"
#> eval "$(make one)"
# regardless, you'll need to pick another
# value of $ONE
ONE = JVWQW4FEHCKMCCLXL4SDSOJ4YLNJZJJTUGSLXPRW4IWMLCJ7VQ4M5ADTJ4
one:
	ONE=$(ONE)

# this one depends on what you ran `make compile CONTRACT = ???` with 
create-1-1-0-0:
	goal app create --creator $(ONE) --approval-prog build/approval.teal --clear-prog build/clear.teal --global-byteslices 1 --global-ints 1 --local-byteslices 0 --local-ints 0

create-0-0-3-1:
	goal app create --creator $(ONE) --approval-prog build/approval.teal --clear-prog build/clear.teal --global-byteslices 0 --global-ints 0 --local-byteslices 3 --local-ints 1

APPID = -1
info:
	goal app info --app-id $(APPID)

# counter:
global:
	goal app read --global --app-id $(APPID) --guess-format

app-call-incr:
	goal app call --app-id $(APPID) --from $(ONE) --app-arg "str:inc"

app-call-decr:
	goal app call --app-id $(APPID) --from $(ONE) --app-arg "str:dec"

# rock-paper-scissors:
optin:
	goal app optin --from $(ONE) --app-id $(APPID)

local:
	goal app read --local --app-id $(APPID) --from $(ONE) --guess-format


APP_ONE = 1
APP_TWO = 8
RPS_ONE = 15

info-one: APPID=$(APP_ONE)
info-one: info

global-one-raw:
	goal app read --global --app-id $(APP_ONE)

global-one: APPID=$(APP_ONE)
global-one: global

global-two: APPID=$(APP_TWO)
global-two: global

app-call-one-incr: APPID=$(APP_ONE)
app-call-one-incr: app-call-incr

app-call-two-incr: APPID=$(APP_TWO)
app-call-two-incr: app-call-incr

app-call-one-decr: APPID=$(APP_ONE)
app-call-one-decr: app-call-decr

app-call-two-decr: APPID=$(APP_TWO)
app-call-two-decr: app-call-decr

app-call-one-decr-dr:
	goal app call --app-id $(APP_ONE) --from $(ONE) --app-arg "str:dec" --dryrun-dump -o tx.dr

tealdbg:
	tealdbg debug -d tx.dr --listen 0.0.0.0

# Now we're in tealdbg
# ---> GO TO CHROME ---> chrome://inspect ---> CLICK inspect (if you haven't configured port 9392)

