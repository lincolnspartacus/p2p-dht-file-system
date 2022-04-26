PROTOS_FILES=protos/chord.proto
protos: $(PROTOS_FILES)
	python -m grpc_tools.protoc -Iprotos/ --python_out=. --grpc_python_out=. protos/chord.proto