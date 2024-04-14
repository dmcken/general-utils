'''
Duplicate file finder:

Algorithm:
# Fetch the folders that we want to process (and if we want to process them recursively or not).
# Sweep all the files in those folders (recursively as appropriate)

'''
import functools
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

READ_BLOCK_SIZE = 1 * 1024 * 1024

class FileEntry:
    '''
    File entry to process
    '''
    __slots__ = (
        'archive_path',
        'file_path',
        'hash_value',
        'size',
    )

    def __init__(self, file_path: str, size: int, archive_path: str = '',
                 hash_value: str = '') -> None:
        '''
        '''
        self.file_path = file_path
        self.size = size
        self.archive_path = archive_path
        self.hash_value = hash_value

    def __repr__(self) -> str:
        return f'FileEntry({self.file_path},{self.size},' \
            f'{self.archive_path},{self.hash_value})'

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
    '''Fetch directory contents returning a list of FileEntry objects.
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

def clean_sizes(file_sizes: dict[int, list[FileEntry]]) -> dict[int, list[FileEntry]]:
    '''Clean out the file sizes.
    '''
    sizes_to_delete = []
    for f_size,files in file_sizes.items():
        if len(files) <= 1:
            sizes_to_delete.append(f_size)

    for curr_size in sizes_to_delete:
        del file_sizes[curr_size]

    return file_sizes

def calculate_hashes(files_to_check: list[FileEntry], hashes_to_calculate: list[str],
                    read_block_size: int = 1024 * 1024) -> list[FileEntry]:
    '''Calculate hashes for all the files listed.

    Args:
        files_to_check: file entries to calculate hashes for.
        hashes_to_calculate: hash algorithms to generate the hash with.
        read_block_size: Block size to read file in for hashing.
    '''
    for curr_file in files_to_check:
        hashes = {}
        for curr_algorithm in hashes_to_calculate:
            hashes[curr_algorithm] = {
                'hash_calculated': '',
                'hash_obj': hashlib.new(curr_algorithm),
            }


        with open(curr_file.file_path, 'rb') as f_obj:
            for block in iter(functools.partial(f_obj.read, read_block_size), b''):
                for _,hash_data in hashes.items():
                    hash_data['hash_obj'].update(block)

        curr_file.hash_value = ''
        hash_values = []
        for curr_algorithm in hashes_to_calculate:
            hashes[curr_algorithm]['hash_calculated'] = \
                hash_values.append(f"{curr_algorithm}#"
                f"{hashes[curr_algorithm]['hash_obj'].hexdigest()}")
        curr_file.hash_value = "|".join(hash_values)


    return files_to_check

if __name__ == '__main__':
    logging.BASIC_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
    logging.basicConfig(level = logging.DEBUG, format=logging.BASIC_FORMAT)

    logging.debug("Start")
