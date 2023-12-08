#!/bin/bash

cd $HOME/projects/comhis/blast_ecco/code/work
source venv/bin/activate
export PATH="$HOME/projects/common/text-reuse-blast-custom/ncbi-blast-2.13.0+-src_modified/c++/ReleaseMT/bin:$PATH"

START=$1
END=$2

for (( c=$START; c<=$END; c++ ))
do
  echo "Running iter $c (${START}-${END})"
  python blast_batches.py --output_folder="$HOME/projects/comhis/tr-latin-classics/data/blast_work" --batch_folder="$HOME/projects/comhis/tr-latin-classics/data/blast_results" --threads=4 --text_count=15967 --qpi=100 --iter=$c --e_value=0.000000001
done
