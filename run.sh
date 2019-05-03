#!/bin/bash

cd proto
python -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. transfer.proto