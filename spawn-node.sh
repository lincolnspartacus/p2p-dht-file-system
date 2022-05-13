#!/bin/bash
LAT=1
MAXNODES=50

i=0
#Port number input - j
j=50000
while [ $i -lt $MAXNODES ]
do
  python chord_node.py $j &
  sleep $LAT
  i=$[$i+1]
  j=$[$j+1]
done
