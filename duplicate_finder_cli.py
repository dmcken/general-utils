'''Duplicate finder CLI interface.
'''


import argparse
import logging
import os
import pathlib
import pprint

import duplicate_finder

logger = logging.getLogger(__name__)

def parse_args():
    '''Parse arguments passed to script.

    TODO: Flag the recursive on a per-path basis.
    '''
    parser = argparse.ArgumentParser(description='Bulk converter')
    parser.add_argument(
        '-p', '--path',
        help='Directory(s) to check for duplicates',
        default=[],
        action='append',
    )
    parser.add_argument(
        '-r', '--recursive',
        help='Check sub directories.',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '-d', '--delete',
        help='Actually delete the files.',
        action='store_true',
        default=False,
    )  
    prog_args = parser.parse_args()

    # Default to current directory if not specified.
    if prog_args.path == []:
        prog_args.path = ['.']

    # Convert the strings to path objects.
    # Also make sure they exist and are directories
    final_paths = []
    for curr_path in prog_args.path:
        p_obj = pathlib.Path(curr_path)
        if not p_obj.exists():
            raise RuntimeError(f"Path '{curr_path}' doesn't exist")
        if not p_obj.is_dir():
            raise RuntimeError(f"Path '{curr_path}' is not a directory")

        # Standardize all paths to their absolute version
        final_paths.append(p_obj.resolve())

    prog_args.path = final_paths

    return prog_args

def calculate_duplicates(args):
    '''Calculate duplicates.
    '''
    logger.info("Starting size scan")
    sizes = {}
    for curr_path in args.path:
        search_dir = duplicate_finder.SearchDirEntry(
            str(curr_path),
            recursive=args.recursive,
        )

        contents = duplicate_finder.fetch_directory_contents(search_dir)

        for curr_file in contents:
            if curr_file.size not in sizes:
                sizes[curr_file.size] = []
            sizes[curr_file.size].append(curr_file)

    # Clear out any sizes that only have 1 entry
    sizes = duplicate_finder.clean_sizes(sizes)

    logger.info(f"Starting hashing '{len(sizes)}' groups")

    # Now we start calculating the hashes
    duplicates = {}
    for curr_size,file_data in sizes.items():
        sizes[curr_size] = duplicate_finder.calculate_hashes(
            file_data,
            ['md5','sha512'],
        )

        candidate_duplicates = {}
        for curr_file in sizes[curr_size]:
            key_value = f"{curr_size}${curr_file.hash_value}"
            if key_value not in candidate_duplicates:
                candidate_duplicates[key_value] = []
            candidate_duplicates[key_value].append(curr_file)

        for dup_group,dup_files in candidate_duplicates.items():
            if len(dup_files) > 1:
                duplicates[dup_group] = dup_files

    return duplicates

def main():
    '''Main CLI function.
    '''
    args = parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(message)s',
        level=logging.INFO,
    )

    logger.info(f"Running duplicate finder with the following parameters: {args}")

    duplicates = calculate_duplicates(args)

    deleted_count = 0
    deleted_size = 0
    for _, curr_dup_files in duplicates.items():
        print(f"Group {len(curr_dup_files)} x {curr_dup_files[0].size:,}")
        for curr_dup_file in curr_dup_files:
            print(f"-> {curr_dup_file.file_path}")

        for to_del in curr_dup_files[:-1]:
            print(f"Delete: {to_del.file_path}")
            deleted_count += 1
            deleted_size += to_del.size
            if args.delete:
                os.remove(to_del.file_path)

    print(f"Files deleted {deleted_count} -> {deleted_size:,}")


if __name__ == '__main__':
    main()
 