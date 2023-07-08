import os
import math
import zipfile
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
        if directory_path.endswith('.zip'):
            return
        
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

def is_nested_archive(archive_path: str) -> bool:
    with zipfile.ZipFile(archive_path, 'r') as archive:
        return any(file.filename.endswith('.zip') for file in archive.filelist)

def _extract_zip(archive_path: str):
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(archive_path.removesuffix(".zip"))

    except FileNotFoundError:
        pass

def extract_nested_zip(archive_path: str, save_path: str):
    if not is_nested_archive(archive_path):
        unzip_archive(archive_path, save_path)
        remove_file(archive_path)
        return

    with zipfile.ZipFile(archive_path, 'r') as archive:
        for file in archive.filelist:
            if not file.filename.endswith('.zip'):
                continue

            with archive.open(file.filename) as zf, open(f"{save_path}/{file.filename}", 'wb') as out:
                shutil.copyfileobj(zf, out)
            
            extract_nested_zip(f"{save_path}/{file.filename}", save_path)
            _extract_zip(f"{save_path}/{file.filename}")
            remove_file(f"{save_path}/{file.filename}")
