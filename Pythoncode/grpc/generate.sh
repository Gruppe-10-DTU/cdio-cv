#!/bin/bash

name="$(uname -s)"
case "${name}" in
    Darwin*)    prog="python3";;
    *)          prog="python"
esac

proto_dir=../../Gocode/proto
proto_file=protobuf.proto
out_dir=.

{prog} -m grpc_tools.protoc -I $proto_dir --python_out=$out_dir --pyi_out=$out_dir --grpc_python_out=$out_dir $proto_dir/$proto_file