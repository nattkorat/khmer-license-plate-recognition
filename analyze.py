from time import time
start = time()
import os, csv, cv2, shutil
from util.extract import roi, front_rear, is_vehicle
from util.ocr import processs_OCR
from util.post_process import major_vote, check_order
end = time()

print(f"Model loaded in {end - start: .4f} seconds")

def analyzer(img_path):
    image = cv2.imread(img_path)
    plates = roi(image, 0)
    data = []
    for plate in plates:
        data.append(processs_OCR(image, plate))
    return data

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
            if width >= 100 or height >= 100: # detect untill the size of the plate is greater than or equal to 100
                return True
    else:
        return False


def process_data(tem_dir):
    imgs = os.listdir(tem_dir)

    if len(imgs) >= 6: # check if the images in the folder is greater than or equal to 6
        results = []
        images = [os.path.join(tem_dir, i) for i in imgs]
        for img in images:       
            # analyze the image
            status = front_rear(img) # checking if object car front or rear
            data = analyzer(img)
                    
            for d in data:
                if d['plate_name'] == '' or d['serial_value'] == '':
                    pass
                else:
                    results.append(d)

        numbers = [i['serial_value'] for i in results]
        common = major_vote(numbers)
        matched = []
        for r in results:
            if r['serial_value'] == common:
                matched.append(r)

        # find the max confidence
        if matched:
            order = check_order([i['plate_size'] for i in matched])
            max_conf = max([i['conf'] for i in matched])
            # get the result
            for i in range(len(matched)):
                if matched[i]['conf'] == max_conf: # get the data with hight confident score
                    # save data to csv [date, time, status, plate, conf, ref]
                    filename = imgs[i]
                    datetime_element = filename.split('_')
                    date = "-".join(datetime_element[:3])
                    time = ":".join(datetime_element[3:-1])
                    plate = matched[i]['plate_name'] + ' ' + matched[i]['serial_value']
                    ref = images[i]

                    # add data to csv file
                    saved = save_data('record.csv', [date, time, status, order, plate, max_conf, ref])
                    # save image as a reference
                    if saved:
                        shutil.copyfile(ref, f'ref_img/{filename}')
                    break # if the data is redundant

            # clear the temporary image from temp_img folder
            [os.remove(i) for i in images]

if __name__ == '__main__':
    start = time()
    process_data('temp_img')
    end = time()
    print(f"The execution time of the recognition {len(os.listdir('temp_img'))} images is: {end - start: .4f} seconds")