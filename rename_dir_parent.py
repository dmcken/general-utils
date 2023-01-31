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
