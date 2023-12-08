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


files_jsonl = glob('data/final_out/*.jsonl')

all_biblical = list()
for file in tqdm(files_jsonl):
    all_biblical.extend(get_file_biblical_passages(file))


# Sort students data by grade key.
bible_sorted = sorted(all_biblical, key=itemgetter('id'))

# Get intervals overlapping with bible by id.
merged_bib_by_id = dict()
for key, value in groupby(bible_sorted, key=itemgetter('id')):
    merged_bib_by_id[key] = merge_intervals([i['interval'] for i in value])

# set biblicality percentage

def write_final_output(outputdata, fname):
    with jsonlines.open(fname, mode='w') as writer:
        writer.write_all(outputdata)


def get_biblical_data_file(file_path, bib_overlap_data):
    reuse_pairs = get_file_passages(file_path)
    for item in tqdm(reuse_pairs):
        for prefix in ['text1', 'text2']:
            item[prefix + '_vulgata_overlap'] = get_section_biblicality(
                item_id=item[prefix + '_id'],
                interval=[item[prefix + '_text_start'], item[prefix + '_text_end']],
                bible_overlaps=bib_overlap_data
            )
            item[prefix + '_id'] = item[prefix + '_id'].strip('.xml')
        item['avg_vulgata_overlap'] = int((
            item['text1_vulgata_overlap'] + item['text2_vulgata_overlap']) / 2)
    return reuse_pairs


i = 1
for file_path in files_jsonl:
    new_data = get_biblical_data_file(file_path, merged_bib_by_id)
    write_final_output(new_data, "data/final_out_with_vulgata/" + file_path.split('/')[-1])
    print("Done: " + str(i) + "/" + str(len(files_jsonl)))
    i += 1
