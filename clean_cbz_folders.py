'''Clean Comic book folders

'''

import os
import re




for curr_dir in os.listdir('.'):
    #print(f"Dir: {curr_dir}")

    if not os.path.isdir(curr_dir):
        continue

    curr_dir = curr_dir.strip()
    res = re.search(r'^(\[(ENG|JAP|RUS|RUS1|RUS2|SPA|CHI|[0-9\-\.]{4,9})\])+', curr_dir)

    if res is None:
        continue

    dst_name = curr_dir.replace(res.group(),'', 1)

    dst_name = f"{dst_name} {res.group()}".strip()

    print(f"Src: '{curr_dir}' -> Dst: '{dst_name}'")

    os.rename(curr_dir, dst_name)

    # break
