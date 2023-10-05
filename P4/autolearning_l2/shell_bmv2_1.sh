#!/bin/sh

docker run -v ./:/tmp/ -it p4lang/p4runtime-sh --config /tmp/prog.p4info.txt,/tmp/prog.json --device-id 0 --grpc-addr 192.168.212.101:50001
