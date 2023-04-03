#!/usr/bin/env python3
'''
Create checksum file for a file(s).

'''
import argparse
import functools
import glob
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

def create_sum_file(checksum_filename: str, checksums: dict, filesize: int):
    '''Write the checksum file to disk.

    '''
    try:
        with open(checksum_filename, 'w', encoding='utf-8') as checksum_file:
            # Write the filesize
            checksum_file.write(f"SIZE : {filesize}\n")
            # Now write the hashes and the values
            for hash_name,hash_data in checksums.items():
                checksum_file.write(
                    f"{hash_name.upper()} : {hash_data['hash_calculated']}\n"
                )
    except Exception as exc:
        logging.error(
            f"Error writing checksum file '{checksum_filename}' - {exc}"
        )
        raise

def calculate_hashes(filename: str,
                    hashes_to_calculate: list[str],
                    read_block_size: int = 1 * 1024 * 1024,
                    ):
    '''Calculate the hashes for the file using the hashes supplied.
    
    '''

    # Setup the objects for managing the running hashes.
    hashes = {}
    for curr_algorithm in hashes_to_calculate:
        hashes[curr_algorithm] = {
            'hash_calculated': None,
            'hash_obj': hashlib.new(curr_algorithm),
        }

    # Simultaneously hash each block of the file against all the algorithms
    # requested, thus reducing the I/O required.
    # If you are really that interested in performance tuning the block size
    # to ensure a block fits in the CPU cache may be desirable.
    with open(filename, 'rb') as in_file:
        for block in iter(functools.partial(in_file.read, read_block_size), b''):
            for _,hash_data in hashes.items():
                hash_data['hash_obj'].update(block)

    # Save the final hashes to the object for that algorithm.
    for _,hash_data in hashes.items():
        hash_data['hash_calculated'] = hash_data['hash_obj'].hexdigest()

    return hashes

def check_checksum_file(filename: str, suffix: str) -> str:
    '''Generate and check for the existence of the output file.
    '''
    checksum_filename = f"{filename}.{suffix}"

    if os.path.exists(checksum_filename):
        msg = f"Checksum file '{checksum_filename}' already exists"
        # logger.error(msg)
        raise RuntimeError(msg)

    return checksum_filename

def parse_arguments():
    '''Parse arguments and return a config object with appropriate defaults.
    '''
    default_hashes = ['md5','sha1','sha256','sha512']
    default_checksum_suffix = 'sum'

    parser = argparse.ArgumentParser(
        prog='CreateHashes',
        description='Generate hashes for the specified file.',
    )
    parser.add_argument('filename', nargs='+')
    #TODO: add option to specify hashes.
    #TODO: add option to override checksum output filename.
    args = parser.parse_args()

    matched_files = []
    for file in args.filename:
        if glob.escape(file) != file:
            # There are glob pattern chars in the string
            matched_files.extend(glob.glob(file))
        else:
            matched_files.append(file)

    return {
        'hashes': default_hashes,
        'files': matched_files,
        'checksum_suffix': default_checksum_suffix,
    }

def main():
    '''Main function'''
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    run_data = parse_arguments()

    for curr_file in run_data['files']:
        try:
            logging.info(f"Processing: {curr_file}")
            checksum_filename = check_checksum_file(
                curr_file,
                run_data['checksum_suffix']
            )

            hashes = calculate_hashes(curr_file, run_data['hashes'])
            filesize = os.path.getsize(curr_file)
            create_sum_file(checksum_filename, hashes, filesize)
        except Exception as exc:
            logging.error(f"Error checksuming file '{curr_file}' - {exc}")

if __name__ == '__main__':
    main()
