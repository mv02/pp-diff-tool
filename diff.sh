#!/bin/bash
FILENAME1=callgraph1.json
FILENAME2=callgraph2.json

python diff.py $FILENAME1 $FILENAME2
