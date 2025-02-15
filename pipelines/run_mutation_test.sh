#!/bin/bash
cd ..
export PYTHONPATH=./
flake8 /home/huck/petprojects/priceformation/src --select=WPS

# mutmut run