#!/bin/bash
LATENCY=3
MAXNODES=50
k=0
iteration=500

i=0
#Port number - j
j=50000
while [ $i -lt $MAXNODES ]
do
  python3 node.py $j &
  sleep $MTBF
  i=$[$i+1]
  j=$[$j+1]
done

sleep 3
#Keep nodes join/leave by spawining a new node and killing a existing one
while [ $k -lt $iteration ]
do
  python3 node.py $j &
  sleep $LATENCY
  kill -9 `pgrep python3 | head -1`
  sleep $LATENCY
  k=$[$k+1]
  j=$[$j+1]
done
