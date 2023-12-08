cd $HOME/projects/comhis/data_input_text_reuse/code
source venv/bin/activate
python generate_json_multiprocess_lmdb.py --datadir "$HOME/projects/comhis/tr-latin-classics/data/blast_results" --outdir "$HOME/projects/comhis/tr-latin-classics/data/blast_results_filled" --threads 10 --db "$HOME/projects/comhis/tr-latin-classics/data/blast_work/db/original_data_DB"
