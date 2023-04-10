# tr-latin-classics

Data preparation for BLAST run of set of TEI XML texts in latin from classical authors.

*create_datadirs.sh* - create the directories for data used below.

*datawrangler.py* - Read extracted data in `data/raw` and save output in `data/final` as *.gz* files ready for BLAST.

*metadata_extractor.py* - Read metadata fields from extracted XML files in `data/raw` and flatten it it to single csv in `data/final`.

## Usage

The scripts have been tested with Python 3.10.6.

1. Run *create_datadirs.sh* to create the empty data directories.
2. Download the required data package from CSC IDA (`Corpus2_PL_new.7z`, found at `COMHIS/originals/corpus-corporum`), extract it to `data/raw`.
3. Install packages in `requirements.txt` with pip.
4. Run *datawrangler.py* to create the data for BLAST.
5. Run *metadata_extractor.py* to create the metadata csv.
6. Proceed with BLAST.
