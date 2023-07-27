import re

# removing spaces and other special characters
def remove_space_special_chars(string):
    result = re.sub(r'[^a-zA-Z0-9]', '', string)
    return result