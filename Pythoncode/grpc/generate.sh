#!/bin/bash

proto_dir=../../Gocode/proto
proto_file=protobuf.proto
out_dir=.

py -m grpc_tools.protoc -I $proto_dir --python_out=$out_dir --pyi_out=$out_dir --grpc_python_out=$out_dir $proto_dir/$proto_file