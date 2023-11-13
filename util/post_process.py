from collections import Counter
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
    if char == '6':
        return 'g'
    if char == '5':
        return 's'
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
    if char == 'g':
        return '6'
    if char == 's':
        return '5'
    
    return char


def char_map(txt, label = ''):
    string = list(remove_space_special_chars(txt.lower()))
    # print(string)
    length = len(string)

    if label in ['Police', 'State', 'RCAF']:
        for i in range(length):
            string[i] = char_to_num(string[i])
            # print(string[i])
        string.insert(1, '-')
        
    elif label == 'Cambodia':
        string = list(txt)
        for i in range(len(string)):
            if string[i] in ['_', ',', '*']:
                string[i] = '.'
            if string[i] == ' ':
                string[i] = ''
    else:
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

        if length == 7:
            string.insert(3, '-')
        
        if length == 6:
            string.insert(2, '-')
    string = ''.join(string).upper()
    return string

def major_vote(data: list):
    if data:
        vote_count = Counter(data)
        winner = vote_count.most_common(1)[0][0]
        return winner
    return None

def check_order(data: list, threshold=0.7):
    if len(data) > 1:
        increasing = sum(data[i] < data[i+1] for i in range(len(data) - 1))
        decreasing = sum(data[i] > data[i+1] for i in range(len(data) - 1))

        total = len(data) - 1

        inc_percent = increasing / total
        dec_percent = decreasing / total

        if inc_percent > threshold:
            return "Increase"
        elif dec_percent > threshold:
            return "Decrease"
        else:
            return "Neigther"
    else:
        return "Neigther"

if __name__ == '__main__':
    print(char_map('2I6.661', 'Cambodia'))