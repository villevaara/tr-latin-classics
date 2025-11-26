# process each filled results file:
# 1. find bible reuses in each
# 2. mark out areas with bible reuse
# 2.1. create mapping table, write to disc (csv) of bible overlap indices
# 3. process each pair, check how many characters on ech side overlap with "bible" area
# 4. add "bible_overlap" percentage to each side of each pair.
# 5. add "avg_bible_overlap" value to reuse pair

from glob import glob
import jsonlines
from operator import itemgetter
from itertools import groupby
from tqdm import tqdm
import csv


def get_processed_metadata(thismeta):
    return {
        'doc_id': thismeta['doc_id'],
        'author': thismeta['titleStmt_author_#text'],
        'chronology': int(thismeta['chronology']),
        'title': thismeta['titleStmt_title'],
        'is_bible': thismeta['is_bible']
    }


def get_file_passages(output_jsonl):
    with open(output_jsonl, 'r') as f:
        all_contents = []
        if f is not None:
            with jsonlines.Reader(f) as reader:
                for i in reader:
                    all_contents.append(i)
    return all_contents


def test_biblical_pair(item):
    for prefix in ['text1', 'text2']:
        if item[prefix + '_id'].split('_')[0] == "Vulgata":
            return True
    return False


def get_biblical_data(item):
    retlist = list()
    for prefix in ['text1', 'text2']:
        retlist.append(
            {
                'id': item[prefix + '_id'],
                'interval': [item[prefix + '_text_start'], item[prefix + '_text_end']]
            })
    return retlist


def get_file_biblical_passages(output_jsonl):
    with open(output_jsonl, 'r') as f:
        all_contents = []
        if f is not None:
            with jsonlines.Reader(f) as reader:
                for i in reader:
                    all_contents.append(i)
    biblical_passages = list()
    for reuse_pair in all_contents:
        if test_biblical_pair(reuse_pair):
            biblical_passages.extend(get_biblical_data(reuse_pair))
    return biblical_passages


def merge_intervals(intervals):
    # Sort the array on the basis of start values of intervals.
    intervals.sort()
    stack = list()
    # insert first interval into stack
    stack.append(intervals[0])
    for i in intervals[1:]:
        # Check for overlapping interval,
        # if interval overlap
        if stack[-1][0] <= i[0] <= stack[-1][-1]:
            stack[-1][-1] = max(stack[-1][-1], i[-1])
        else:
            stack.append(i)
    return stack


def get_indices_overlap_length(x, y):
    return len(range(max(x[0], y[0]), min(x[-1], y[-1]) + 1))


def get_section_biblicality(item_id, interval, bible_overlaps):
    if item_id not in bible_overlaps.keys():
        return 0
    else:
        this_item_overlaps = bible_overlaps[item_id]
        overlaps = list()
        for item in this_item_overlaps:
            overlaps.append(get_indices_overlap_length(interval, item))
        overlap_length = sum(overlaps)
        overlap_percentage = int((overlap_length / len(range(interval[0], interval[1] + 1))) * 100)
        return overlap_percentage


def write_final_output(outputdata, fname):
    with jsonlines.open(fname, mode='w') as writer:
        writer.write_all(outputdata)


def get_biblical_data_file(file_path, bib_overlap_data, metadata_dict):
    reuse_pairs = get_file_passages(file_path)
    for item in tqdm(reuse_pairs):
        for prefix in ['text1', 'text2']:
            item[prefix + '_vulgata_overlap'] = get_section_biblicality(
                item_id=item[prefix + '_id'],
                interval=[item[prefix + '_text_start'], item[prefix + '_text_end']],
                bible_overlaps=bib_overlap_data)
            #
            this_meta = metadata_dict[item[prefix + '_id']][0]
            for k, v in this_meta.items():
                if k != 'doc_id':
                    item[prefix + '_' + k] = v
        #
        item['avg_vulgata_overlap'] = int((
            item['text1_vulgata_overlap'] + item['text2_vulgata_overlap']) / 2)
    return reuse_pairs


def read_csv_to_dict(file_path):
    result_list = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result_list.append(row)
    return result_list


def list_to_dict_by_key(list_to_group, key_field):
    results_dict = {}
    for entry in list_to_group:
        if entry[key_field] in results_dict.keys():
            results_dict[entry[key_field]].append(entry)
        else:
            results_dict[entry[key_field]] = [entry]
    return results_dict



files_jsonl = glob('data/final_out/*.jsonl')

# Get a list of all overlaps with bible.
all_biblical = list()
for file in tqdm(files_jsonl):
    all_biblical.extend(get_file_biblical_passages(file))

# sort above list by text id
bible_sorted = sorted(all_biblical, key=itemgetter('id'))

# Get intervals overlapping with bible, grouped by text id.
merged_bib_by_id = dict()
for key, value in groupby(bible_sorted, key=itemgetter('id')):
    merged_bib_by_id[key] = merge_intervals([i['interval'] for i in value])

metadata = read_csv_to_dict('data/final/metadata.csv')
metadata_processed = [get_processed_metadata(i) for i in metadata]
metadata_processed = list_to_dict_by_key(metadata_processed, 'doc_id')


# set biblicality percentage, add metadata to each item.
i = 1
for file_path in files_jsonl:
    new_data = get_biblical_data_file(file_path, merged_bib_by_id, metadata_processed)
    write_final_output(new_data, "data/final_out_with_vulgata/" + file_path.split('/')[-1])
    print("Done: " + str(i) + "/" + str(len(files_jsonl)) + " " + file_path.split('/')[-1])
    i += 1


import ndjson


def read_ndjson(ndjson_file):
    with open(ndjson_file, 'r') as jsonfile:
        data = ndjson.load(jsonfile)
    return data


for index in range(0, 23):
    print(index)
    d = read_ndjson('data/final_out_with_vulgata/latin_tr_' + str(index) + '.jsonl')
    for i in d:
        if "." in i['text1_id']:
            print(i['text1_id'])
        if "." in i['text2_id']:
            print(i['text2_id'])

