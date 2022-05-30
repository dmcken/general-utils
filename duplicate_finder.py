'''
Duplicate file finder:

Algorithm:
# Fetch the folders that we want to process (and if we want to process them recursively or not).
# Sweep all the files in those folders (recursively as appropriate)

'''
import collections
import functools
import hashlib
import logging
import os
import pprint
import typing

logger = logging.getLogger(__name__)

READ_BLOCK_SIZE = 1 * 1024 * 1024

class FileEntry:
    '''
    File entry to process
    '''
    __slots__ = ('file_path','archive_path','size')

    def __init__(self, file_path: str, size: int, archive_path: str = '') -> None:
        '''
        '''
        self.file_path = file_path
        self.size = size
        self.archive_path = archive_path

    def __repr__(self) -> str:
        return f'FileEntry({self.file_path},{self.size},{self.archive_path})'

class SearchDirEntry:
    '''
    Directory entry we want to search for duplicates
    '''
    __slots__ = ('dir_path', 'recursive', 'search_archives')

    def __init__(self, dir_name, recursive=False, search_archives=False):
        self.dir_path = dir_name
        self.recursive = recursive
        self.search_archives = search_archives

    def __repr__(self):
        return f'SearchEntry({self.dir_path},{self.recursive},{self.search_archives})'

def fetch_directory_contents(to_search: SearchDirEntry) -> list[FileEntry]:
    '''
    Fetch directory contents returning a list of FileEntry objects
    '''

    res = []

    for root, _, filenames in os.walk(to_search.dir_path):
        for filename in filenames:
            full_filename = os.path.join(root, filename)
            file_size = os.stat(full_filename).st_size

            #TODO: Check if this is an archive and recurse into it.

            res.append(FileEntry(
                full_filename,
                file_size,
            ))

        # Do we want the sub-directories?
        if not to_search.recursive:
            break

    return res

def find_duplicates(directories: list[SearchDirEntry]) -> list[list[FileEntry]]:
    '''
    Find duplicate files in the folders specified

    '''
    logger.debug("Scanning directories")
    files_by_size = collections.defaultdict(list)
    for curr_directory_entry in directories:
        curr_files = fetch_directory_contents(curr_directory_entry)
        for curr_file in curr_files:
            files_by_size[curr_file.size].append(curr_file)

    # Filter out all those where there is only 1 file of that size
    #TODO: Identify which method works better filter vs dictionary comprehension
    potential_duplicates = dict(filter(lambda elem: len(elem[1]) > 1, files_by_size.items()))
    #potential_duplicates = { key:value for (key,value) in files_by_size.items() if len(value) > 1}

    duplicates_found = []
    logger.debug(f"Number of potential duplicates: {len(potential_duplicates)}")

    hashes_to_check = ['md5','sha1']

    for _,files in potential_duplicates.items():

        group_hashes = collections.defaultdict(list)

        # Calculate all of the hashes desired
        for curr_file in files:
            hashes = {}
            for curr_hash in hashes_to_check:
                hashes[curr_hash] = hashlib.new(curr_hash)

            with open(curr_file.file_path, 'rb') as f:
                for block in iter(functools.partial(f.read, READ_BLOCK_SIZE), b''):
                    for _,hash_obj in hashes.items():
                        hash_obj.update(block)

            hash_strings = []
            for curr_hash in hashes_to_check:
                hash_strings.append(hashes[curr_hash].hexdigest())
            full_signature = '_'.join(hash_strings)

            group_hashes[full_signature].append(curr_file)

        dup_groups = { key:value for (key,value) in group_hashes.items() if len(value) > 1}

        #logger.debug(f"Duplicates: {dup_groups}")
        for _,dup_group in dup_groups.items():
            duplicates_found.append(dup_group)

    return duplicates_found

if __name__ == '__main__':
    logging.BASIC_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
    logging.basicConfig(level = logging.DEBUG, format=logging.BASIC_FORMAT)

    logging.debug("Start")

    dirs = [
        SearchDirEntry(r'F:\eBooks-Incoming\Mathematics', True),
    ]

    duplicates = find_duplicates(dirs)

    for curr_dup in duplicates:
        logging.debug(f"Group of {len(curr_dup)} files of size: {curr_dup[0].size:,}")
        for curr_file in curr_dup:
            logging.debug(f"  File: {curr_file.file_path}")

