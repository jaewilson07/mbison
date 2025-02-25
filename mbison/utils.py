# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/utils.ipynb.

# %% auto 0
__all__ = ['upsert_folder', 'download_zip', 'change_suffix']

# %% ../nbs/utils.ipynb 1
import os
import pathlib

import zipfile
import io

# %% ../nbs/utils.ipynb 3
def upsert_folder(folder_path: str, debug_prn: bool = False):
    folder_path = os.path.dirname(folder_path)

    if debug_prn:
        print(
            {
                "upsert_folder": os.path.abspath(folder_path),
                "is_exist": os.path.exists(folder_path),
            }
        )

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return True

# %% ../nbs/utils.ipynb 4
def download_zip(
        output_folder,
        zip_bytes_content: bytes = None,
                 zip_file_path : str = None,
                  ):
    """save bytes content to a zip file then convert html to markdown"""
    zip = None
    if zip_bytes_content:
        zip = zipfile.ZipFile(io.BytesIO(zip_bytes_content), "r")
    
    if zip_file_path:
        zip = zipfile.ZipFile(zip_file_path)
    
    if not zip:
        raise Exception("unabler to generate zip file pass zip_bytes_content or zip_file_path")
    
    zip.extractall(output_folder)

    file_ls = os.listdir(output_folder)
    return file_ls

# %% ../nbs/utils.ipynb 5
def change_suffix(filename, new_extension):
    is_exist = os.path.exists(filename)

    p = pathlib.PurePath(filename)
    p = p.with_suffix(new_extension)

    if is_exist:
        p = pathlib.Path(filename)
        p = p.rename(p.with_suffix(new_extension))

    return str(p)
