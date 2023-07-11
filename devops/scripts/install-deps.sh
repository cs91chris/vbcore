#!/bin/bash

apt update && apt install -y \
	graphviz

make install-deps
