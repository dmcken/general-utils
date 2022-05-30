





import argparse
import pathlib



def parse_args():
    '''
    '''
    parser = argparse.ArgumentParser(description='Bulk converter')
    parser.add_argument(
        '--path',
        type=pathlib.Path,
        help='Path to process',
        default='.'
    )
    parser.add_argument('-r', '--recursive', action='store_true')
    parser.set_defaults(recursive=False)

    prog_args = parser.parse_args()

    return prog_args





