'''Rename directory from parent.

A very simple script to rename all folders in the CWD to the folder
name concatenated to the parent.

Useful in cases like this:
Series/
  vol1/
  vol2/

After running in the Series folder it will look like this:
Series/
  Series - vol1/
  Series - vol2/
'''

import os
import sys

try:
    base_path = sys.argv[1]
except IndexError:
    base_path = '.'

base_path = os.path.abspath(base_path)
dir_parts = base_path.split(os.sep)

parent_dir = dir_parts[-1]

for fname in os.listdir('.'):
    if not os.path.isdir(fname):
        continue

    new_dir_name = f"{parent_dir} - {fname}"

    if parent_dir == fname[:len(parent_dir)]:
        # 
        continue

    print(f"Old: {fname} -> New: {new_dir_name}")

    os.rename(fname, new_dir_name)
