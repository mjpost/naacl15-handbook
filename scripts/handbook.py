import re
from csv import DictReader

def extract_keywords(title):
    """Extracts keywords from a title, and returns the title and a dictionary of keys and values"""
    dict = {}
    for key, value in re.findall('%(\w+) ([^%]+)', title):
        dict[key] = value

    if title.find('%') != -1:
        title = title[:title.find('%')]

    return title, dict
        
def load_location_file(file):
    """Loads a location file (TODO: specify format)"""
    locations = {}
    if file is not None:
        for row in DictReader(open(file)):
            locations[row['event']] = '\\\\%sLoc' % (row['event'])

    return locations
