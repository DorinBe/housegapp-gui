def row_generate(start=0):
    while True:
        yield start
        start += 1

def find_tag(tag_name:str, tag_tuple:tuple):
    for tag in tag_tuple:
        if tag_name in tag:
            return tag.split(":")[1]
    # raise Exception(f"Tag {tag_name} not found") # for debugging only