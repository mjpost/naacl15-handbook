import re

def extract_keywords(title):
    """Extracts keywords from a title, and returns the title and a dictionary of keys and values"""
    dict = {}
    for key, value in re.findall('%(\w+) ([^%]+)', title):
        dict[key] = value

    if title.find('%') != -1:
        title = title[:title.find('%')]

    return title, dict
        

       
