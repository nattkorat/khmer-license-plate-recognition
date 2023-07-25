# need a dircetory of dataset
# put the chunsize ex. 10 will create 10 folders and move data into that subfolder
# for the ramianding files file add to sub folder randomly
import os
import random
import shutil
import argparse


def group_files(source_folder, target_folder, num_subfolders: int):

    # Get the list of files in the source folder
    files = os.listdir(source_folder)

    num_files_per_group = len(files) // num_subfolders
    print(num_files_per_group)

    remain = len(files) % num_subfolders

    # list of remaining files
    remained_file = files[-remain:]

    # Split the files into groups
    file_groups = [files[i:i+num_files_per_group] for i in range(0, len(files), num_files_per_group)]

    # add the remainer to random sub folder
    for i in remained_file:
        rand_group = random.randint(0, num_subfolders - 1)

        # append remain to sub folder
        file_groups[rand_group].append(i)

    # Create target subfolders
    for i in range(num_subfolders):
        os.makedirs(os.path.join(target_folder, f"task_{i}"), exist_ok=True)
  
    # Move files to subfolders
    if remain > 0:
        for i, group in enumerate(file_groups[:-1]):
            subfolder = os.path.join(target_folder, f"task_{i}")
            for file in group:
                source_path = os.path.join(source_folder, file)
                target_path = os.path.join(subfolder, file)
                shutil.move(source_path, target_path)
                print(source_path, target_path)

    else:
        for i, group in enumerate(file_groups[:-1]):
            subfolder = os.path.join(target_folder, f"task_{i}")
            for file in group:
                source_path = os.path.join(source_folder, file)
                target_path = os.path.join(subfolder, file)
                shutil.move(source_path, target_path)
                print(source_path, target_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # add argument 
    parser.add_argument('--source_folder', type=str, required=True, help='Directory to the base folder')
    parser.add_argument('--target_folder', type=str, required=True, help='Directory to the target folder')
    parser.add_argument('--num_folder', type=int, required=True, help='Amount of sub folder to seperate')

    # parse the argument
    arg = parser.parse_args()


    group_files(arg.source_folder, arg.target_folder, arg.num_folder)