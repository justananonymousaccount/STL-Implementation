#!/bin/bash

# Check for exactly two arguments: domain and max iteration number
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <domain> <max_iteration>"
    exit 1
fi

# Assign arguments
domain=$1
max_iter=$2

# Copy base model to iteration 0 directory
echo "Initializing model for domain '${domain}' at iteration 0..."
mkdir -p ./models/${domain}/ours/
cp -r ./models/llava-v1.5-7b ./models/${domain}/ours/llava-v1.5-7b-lora-oursit0

# Run the pipeline for iterations 1 through max_iter
for i in $(seq 1 $max_iter)
do
    ./ours-part1.sh $i $domain
    ./ours-neg.sh $i $domain
    ./ours-part2.sh $i $domain
done
