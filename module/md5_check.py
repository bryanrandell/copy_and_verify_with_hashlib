import hashlib
import shutil
import os

def create_md5_values(folder_path_src, folder_path_dest, hasher_selected="md5"):
    dict_md5_src = {}
    dict_md5_dest = {}
    extention_selected_tuple = (".jpg", ".png", ".gif", ".bmp", ".jpeg", '.dng', '.mov', '.pdf')
    for root, dir, files in os.walk(folder_path_src):
        for file in files:
            if file.endswith(extention_selected_tuple):
                src_file_path = os.path.join(root, file)
                dict_md5_src[file] = hash_file(src_file_path, hasher_selected)
                print("{} -> {}".format(file, dict_md5_src[file]))

    for root, dir, files in os.walk(folder_path_dest):
        for file in files:
            if file.endswith(extention_selected_tuple):
                dst_file_path = os.path.join(root, file)
                dict_md5_dest[file] = hash_file(dst_file_path, hasher_selected)
                print("{} -> {}".format(file, dict_md5_dest[file]))

    return dict_md5_src, dict_md5_dest

def compare_two_dict_md5(dict_md5_src, dict_md5_dest):
    dict_md5_compare = {}
    for file_name in dict_md5_src.keys():
        if file_name in dict_md5_dest.keys():
            if dict_md5_src[file_name] == dict_md5_dest[file_name]:
                dict_md5_compare[file_name] = "Same"
            else:
                dict_md5_compare[file_name] = "Different"
        else:
            dict_md5_compare[file_name] = "Not Found"
    return dict_md5_compare


def copy_files_from_selected_folder(src, dest):
    if os.path.isdir(src):
        try:
            shutil.copytree(src, dest)
            return "Copy Successful"
        except shutil.Error as e:
            return e


def hash_file(file_path, hasher_selected):
    BLOCKSIZE = 65536
    hasher_selected_dict = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256, "sha512": hashlib.sha512}
    hasher = hasher_selected_dict[hasher_selected]()
    with open(file_path, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()