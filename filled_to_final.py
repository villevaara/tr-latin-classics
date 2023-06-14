import tarfile
import jsonlines
from glob import glob
from tqdm import tqdm


def get_single_tar_contents(tarpath, verbose=False):
    tar = tarfile.open(tarpath, "r:gz")
    all_contents = []
    for member in tar.getmembers():
        f = tar.extractfile(member)
        if f is not None:
            contents = f.read()
            all_contents.append({
                'file': member.name,
                'content': contents})
    tar.close()
    if verbose:
        print("  -- Extracted data in: " + tarpath)
    return all_contents


def get_single_tar_jsonlines(tarpath, verbose=False):
    tar = tarfile.open(tarpath, "r:gz")
    all_contents = []
    for member in tar.getmembers():
        f = tar.extractfile(member)
        if f is not None:
            with jsonlines.Reader(f) as reader:
                for i in reader:
                    all_contents.append(i)
    tar.close()
    if verbose:
        print("  -- Extracted data in: " + tarpath)
    return all_contents


def get_text_segment(textfile_id, start, end):
    tf = 'data/work/txt/' + textfile_id[:-4] + ".txt"
    with open(tf, 'r') as textfile:
        this_text = textfile.read()
        return this_text[start:end]


def set_item_indices(filled_item):
    for prefix in ['text1', 'text2']:
        add_amount = int(filled_item[(prefix + '_id')].split('.xml__')[-1].split('_')[0])
        filled_item[prefix + '_text_start'] = filled_item[prefix + '_text_start'] + add_amount
        filled_item[prefix + '_text_end'] = filled_item[prefix + '_text_end'] + add_amount
        filled_item[prefix + '_id'] = filled_item[prefix + '_id'].split('__')[0]
        filled_item[prefix + '_source'] = filled_item[prefix + '_id'].split('__')[0][:-4] + ".txt"


def write_final_output(outputdata, fname):
    with jsonlines.open(fname, mode='w') as writer:
        writer.write_all(outputdata)


filled_qpi100_files = glob("data/work/filled/*.tar.gz")
write_buffer = list()
writer_i = 0
write_now = False
counter = 0
numlines = 1000000


for archive in tqdm(filled_qpi100_files):
    new_data = get_single_tar_jsonlines(archive)
    for item in new_data:
        set_item_indices(item)
    write_buffer.extend(new_data)
    counter += 1
    # if enough data in buffer, write and empty it
    if len(write_buffer) >= numlines:
        write_now = True
    if counter == len(filled_qpi100_files) -1:
        write_now = True
    if write_now:
        outfname = 'data/final_out/latin_tr_' + str(writer_i) + '.jsonl'
        write_final_output(write_buffer[0:numlines], outfname)
        write_buffer = write_buffer[numlines:]
        writer_i += 1
        write_now = False
