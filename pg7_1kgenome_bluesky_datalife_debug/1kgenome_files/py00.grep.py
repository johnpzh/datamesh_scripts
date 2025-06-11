import subprocess
import os

# inputfile = "/qfs/projects/oddite/peng599/1kgenome_qfs/1kgenome_sbatch_deception/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf"
inputfile = "/people/peng599/Projects/Datamesh/qfs/1kgenome_qfs/pg7_1kgenome_bluesky_datalife_debug/1kgenome_files/data.log"

siftfile = 'SIFT.chr1.vcf'

# with open(siftfile, 'w') as f:
#     subprocess.run(['grep -n "deleterious\|tolerated" {}'.format(inputfile)], shell=True, stdout=f, check=True)
# #     # results = os.popen(f'grep -n "deleterious\|tolerated" {inputfile}').read()
# #     # print(f"len(results): {len(results)}")
# #     # f.write(results)

# results = subprocess.run(['grep -n "deleterious\|tolerated" {}'.format(inputfile)], 
#                          capture_output = True, text = True, shell=True, check=True)
# with open(siftfile, 'w') as f:
#     f.write(results.stdout)

# results = subprocess.run(['grep -n "deleterious\|tolerated" {}'.format(inputfile)], 
#                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
# results = subprocess.run(
#     ['grep', '-n', '"deleterious\|tolerated"', inputfile], 
#     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


# results = subprocess.run(
#     ['grep', '-n', 'deleterious\|tolerated', inputfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

with open(siftfile, 'w') as f:
    # f.write(results.stdout.decode(encoding="utf-8"))
    f.write("hello, world.\nIs this correct?")


with open(siftfile, 'r') as f:
    content = f.readlines()
    print(f"len(content): {len(content)}")

# results = os.popen(f'grep -n "deleterious\|tolerated" {inputfile}').read()
# print(f"len(results): {len(results)}")
# with open(siftfile, 'w') as f:
#     f.write(results)


print("Done.")
