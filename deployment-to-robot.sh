#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit
fi

echo "Compiling protofiles"
cd ./Gocode/proto/ || exit
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative protobuf.proto

cd ..
echo "Compiling binary"
GOOS=linux GOARCH=arm GOARM=5 go build -o robot-grpc

echo "Stopping old gRPC service"
ssh robot@$1 "sudo systemctl stop robot.service" 
if [ $? -eq 1 ]; then 
  echo "Failed to stop service..." && exit
fi
echo "Deploying new binary"
scp ./robot-grpc robot@$1:~/robot-grpc
if [ $? -eq 1 ]; then 
  echo "Failed to copy binary..." && exit
fi

echo "Restarting gRPC service"
ssh robot@$1 "sudo systemctl start robot.service"
if [ $? -eq 1 ]; then 
  echo "Failed to start service..." && exit
fi

echo "Done"

