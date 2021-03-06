#!/bin/bash

# Define a timestamp function
timestamp=$(date +"%Y-%m-%d_%T")
logfile=./.log/test_$timestamp.log # print timestamp
echo $logfile

export THEANO_FLAGS=device=gpu0,floatX=float32

python ./translate_gpu.py -m $1 -p test -step $2 | tee $logfile
python ./score.py -m $1 | tee -a $logfile
python ./split.py | tee -a $logfile
