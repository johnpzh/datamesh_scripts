import subprocess
import os


siftfile = 'SIFT.chr1.vcf'

with open(siftfile, 'w') as f:
    f.write("hello, world.\nIs this correct?\n")

with open(siftfile, 'r') as f:
    content = f.readlines()
    print(f"len(content): {len(content)}")

print("Done.")
