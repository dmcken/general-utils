'''
check-hashes.py
'''
import functools
import hashlib
import logging
import os
import pprint
import sys

def check_hashes(filename: str, checksum_suffix: str = 'sum', read_block_size: int = 1024 * 1024):
    '''
    calculate_and_check_hashes
    '''

    hashes = {}

    try:
        sum_filename = '{0}.{1}'.format(filename, checksum_suffix)

        #TODO: Handle the checksum file not existing better.
        with open(sum_filename, 'r') as f_sum:
            for curr_line in f_sum:
                curr_line = curr_line.strip()
                if curr_line.strip() == '':
                    continue

                # Ignore lines begining with '#'
                if curr_line[0] == '#':
                    continue

                parts = curr_line.split(':')
                if len(parts) != 2:
                    logging.error(f"Invalid checksum specification found on line: '{curr_line}'")
                    continue

                curr_algorithm = parts[0].strip().lower()

                if curr_algorithm not in hashlib.algorithms_available:
                    logging.error(f"Sorry but hash algorithm '{curr_algorithm}' is not available")
                    continue

                hashes[curr_algorithm] = {
                    'hash_saved': parts[1].strip().lower(),
                    'hash_calculated': '',
                    'hash_obj': hashlib.new(curr_algorithm),
                }
    except KeyError:
        logging.error(f"Unable to determine checksum file for: {filename}")
        return False
    except FileNotFoundError:
        logging.error(f"Checksum file '{sum_filename}' was not found")
        return False

    with open(filename, 'rb') as f:
        for block in iter(functools.partial(f.read, read_block_size), b''):
            for k,v in hashes.items():
                v['hash_obj'].update(block)
    
    any_failed_matches = False
    for k,v in hashes.items():
        v['hash_calculated'] = v['hash_obj'].hexdigest()

        # Specifically compare the two hashes, everything should be lower cased
        v['match'] = v['hash_calculated'] == v['hash_saved']

        if v['match'] == False:
            logging.warning("Hash mis-match found, algo '{0}' calculated '{1}' should be '{2}'".\
                format(k, v['hash_calculated'], v['hash_saved']))
            any_failed_matches = True

    if any_failed_matches:
        return False
    else:
        return True
  
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    import glob

    #sw_updates = glob.glob('*.ova')
    sw_updates = glob.glob('*.qcow2')
    #sw_updates = glob.glob('*.tgz')
    #sw_updates = glob.glob('*.vhd')
    for curr_file in sw_updates:
        res = check_hashes(curr_file)
        print("{0} => {1}".format(curr_file, res))
