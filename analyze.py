import time
load = time.time()
import os, csv, cv2, shutil
from util.extract import roi, front_rear, is_vehicle
from util.ocr import processs_OCR
from util.post_process import major_vote, check_order
from datetime import datetime
finish = time.time()

print(f"Model loaded in {finish - load: .4f} seconds")

# make the directory if not yet created
os.makedirs('ref_img', exist_ok=True)
os.makedirs('temp_img', exist_ok=True)

def analyzer(img_path):
    image = cv2.imread(img_path)
    plates = roi(image, 0)
    data = []
    for plate in plates: 
        result = processs_OCR(image, plate)
        result['file_path'] = img_path
        data.append(result)
    return data

def server_datetime():
    return str(datetime.now().year) + '_' + str(datetime.now().month) + '_' + str(datetime.now().day) + '_' \
            + str(datetime.now().hour) + '_' + str(datetime.now().minute) + '_' + str(datetime.now().second) + '_' + str(datetime.now().microsecond)

def get_last_row_from_csv(file_path):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = [row for row in csv_reader]
        if rows:
            return rows[-1]
        return None

def save_data(filename, data):
    file_exist = os.path.isfile(filename)
    with open(filename, 'a', newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exist:
            writer.writerow(['date', 'time', 'status (0:exit, 1:entrance)', 'plate_size', 'plate', 'conf', 'ref'])
        last = get_last_row_from_csv(filename)
        if not last: # if there is no data in the csv file yet
            writer.writerow(data)
            print('Record data...')
            return True
        elif [last[0], last[2], last[4]] != [str(data[0]), str(data[2]), str(data[4])]: # check on date, status, and plate before add to dataset
            writer.writerow(data)
            print('Record data...')
            return True
        else:
            print('Data already exist...')
            return False

def detected(frame): # check if the vehicle appears in the frame
    if is_vehicle(frame):
        data = roi(frame, 0)
        for d in data:
            width, height = d[2] - d[0], d[3] - d[1]
            if height >= 50: # detect untill the height of the plate is greater than 50
                return True
    return False

def vehicle_xyxy(frame):
    return is_vehicle(frame, True)

def readRemove(path):
    try:
        with open(path, 'r') as file:
            data = file.read()
        os.remove(path)    
        return [i for i in data.split('\n') if i]
    except:
        return []


def process_data(temfile):
    """
        param: temfile
                txt directory file
    """
    start = time.time()
    imgs = readRemove(temfile)
    if len(imgs) > 0: # work if the folder is not empty
        results = []
        for img in imgs:       
            # analyze the image
            data = analyzer(img)
                    
            for d in data:
                if d['serial_value'] == '' or d['conf'] < 0.35:
                    pass
                else:
                    results.append(d)
        if results:
            numbers = [i['serial_value'] for i in results]
            common = major_vote(numbers)
            matched = []
            for r in results:
                if r['serial_value'] == common:
                    matched.append(r)

            # find the max confidence
            if matched:
                max_conf = max([i['conf'] for i in matched])
                # checking if object car front or rear
                match_imgs = [i['file_path'] for i in matched]
                status = major_vote([front_rear(i) for i in match_imgs])

                order = check_order([i['plate_size'] for i in matched], 0.5) # set threshold to 50%
                # get the result
                for i in range(len(matched)):
                    if matched[i]['conf'] == max_conf: # get the data with high confident score
                        # save data to csv [date, time, status, plate, conf, ref]
                        filename = os.path.split(matched[i]['file_path'])[-1]
                        print(filename)
                        datetime_element = filename.split('_')
                        date = "-".join(datetime_element[:3])
                        det_time = ":".join(datetime_element[3:-1])
                        plate = matched[i]['plate_name'] + ' ' + matched[i]['serial_value']
                        ref = matched[i]['file_path']

                        # add data to csv file
                        saved = save_data('record.csv', [date, det_time, status, order, plate, max_conf, ref])
                        # save image as a reference
                        if saved:
                            shutil.copyfile(ref, f'ref_img/{filename}')
                        break # if the data is redundant

        # clear the temporary image from temp_img folder
        end = time.time()
        [os.remove(i) for i in imgs]
        print('-----------------------------')
        print(f'{len(imgs)} images - {end - start: .2f} seconds')
        print('-----------------------------')

if __name__ == '__main__':
    process_data('tem_img.txt')
    