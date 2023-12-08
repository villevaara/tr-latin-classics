import re


def get_clean_id(old_id):
    new_id = re.sub(r'[\(\)\.,]', '', old_id)
    new_id = new_id.replace(' ', '_')
    new_id = re.sub(r'_+', '_',new_id)
    new_id = new_id.strip('_')
    return new_id
