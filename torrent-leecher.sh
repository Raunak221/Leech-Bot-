#!/bin/bash

aria2c \
	--enable-rpc \
	--conf-path=/app/publicleechgroup/aria2/aria2.conf &
python3 -m publicleechgroup
