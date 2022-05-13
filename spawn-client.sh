#!/bin/bash
#Spawns different clients
MAXCLIENTS=30

i=0
j=1
while [ $i -lt $MAXCLIENTS ]
do
  mkdir $j
  #Linking to 64MB file and generating different hash value for testing
  ln -s ../client_data/test128.txt $j/test64.txt
  python client.py $j
  i=$[$i+1]
  j=$[$j+1]
done
