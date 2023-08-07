import re

# removing spaces and other special characters
def remove_space_special_chars(string):
    result = re.sub(r'[^a-zA-Z0-9]', '', string)
    return result


# replace character (B - 8) (0 - O) (I - 1) (A - 4)
# first character must be number the most number is
def num_to_char(char):
    if char == '1':
        return 'i'
    if char == '0':
        return 'o'
    if char == '4':
        return 'a'
    if char == '8':
        return 'b'
    return char

def char_to_num(char):
    if char == 'i':
        return '1'
    if char == 'o':
        return '0'
    if char == 'a':
        return '4'
    if char == 'b':
        return '8'
    return char


def char_map(string):
    string = list(remove_space_special_chars(string.lower()))
    length = len(string)

    if length > 0:
        first = string[0]
        # replace char with num
        if not first.isdigit():
            string[0] = char_to_num(first)

        if length >= 2:
            second = string[1] # the second character must be str
            if second.isdigit():
                string[1] = num_to_char(second)
                
        if length >= 3:
            third = string[2] # has two case if len > 6 is letter else number
            if length > 6:
                string[2] = num_to_char(third)
            else:
                string[2] = char_to_num(third)

        
        # for other must be number
        for i in range(3, length):
            string[i] = char_to_num(string[i])

    # convert back to str
    string = ''.join(string).upper()

    return string

if __name__ == '__main__':
    print(char_map('I6.661'))