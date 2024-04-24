#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit
fi

cd ./Gocode/proto/ || exit
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative protobuf.proto

cd ..
GOOS=linux GOARCH=arm GOARM=5 go build -o robot-grpc

ssh robot@$1 "sudo systemctl stop robot.service" || exit
scp ./robot-grpc robot@$1:~/robot-grpc || exit
ssh robot@$1 "sudo systemctl start robot.service"

