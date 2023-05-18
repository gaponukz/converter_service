import os
import math
import shutil
import logging
import patoolib

def devide_list(array: list, number: int) -> list[list]:
    div_number = math.ceil(len(array) / number)
    result: list[list] = []
    start_index = 0

    for index in range(1, div_number+1):
        result.append(array[start_index:index*number])

        start_index = index * number
    
    return result

def remove_folder(folder_path: str):
    try:
        shutil.rmtree(folder_path)

    except Exception as error:
        logging.warning(f"Can not remove folder {folder_path} due to error: {error}")

def remove_file(file_path: str):
    try:
        os.remove(file_path)

    except Exception as error:
        logging.warning(f"Can not remove {file_path} due to error: {error}")

def make_zip_archive(directory_path: str, remove: bool=False):
    try:
        shutil.make_archive(directory_path, 'zip', directory_path)

    except Exception as error:
        logging.warning(f"Can not create zip {directory_path} due to error: {error}")
    
    if remove:
        remove_folder(directory_path)

def unzip_archive(archive, outdir):
    try:
        patoolib.extract_archive(archive, 0, outdir)

    except Exception as error:
        logging.error(f"Can not extract {archive} due to {error}")
        raise error
