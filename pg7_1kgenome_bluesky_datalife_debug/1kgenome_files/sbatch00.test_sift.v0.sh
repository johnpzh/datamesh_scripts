#!/bin/bash
#SBATCH --job-name="sift_debug"
#SBATCH --partition=slurm
######SBATCH --exclude=dc[119,077]
#SBATCH --account=datamesh
#SBATCH -N 1
#SBATCH --time=04:44:44
#SBATCH --output=R.%x.%j.out
#SBATCH --error=R.%x.%j.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhen.peng@pnnl.gov
#SBATCH --exclusive

#### sinfo -p <partition>
#### sinfo -N -r -l
#### srun -A CENATE -N 1 -t 20:20:20 --pty -u /bin/bash

#First make sure the module commands are available.
source /etc/profile.d/modules.sh

#Set up your environment you wish to run in with module commands.
echo
echo "loaded modules"
echo
module purge
# module load rocm/5.6.0
#module load cuda/12.3
# Modules needed by Orca
module load gcc/11.2.0 binutils/2.35 cmake/3.29.0
#module load openmpi/4.1.4
#module load mkl
module list &> _modules.lis_
cat _modules.lis_
/bin/rm -f _modules.lis_

#Python version
echo
echo "python version"
echo
command -v python
python --version
PYTHON_PATH=$(command -v python)


#Next unlimit system resources, and set any other environment variables you need.
ulimit -s unlimited
echo
echo limits
echo
ulimit -a

#Is extremely useful to record the modules you have loaded, your limit settings,
#your current environment variables and the dynamically load libraries that your executable
#is linked against in your job output file.
# echo
# echo "loaded modules"
# echo
# module list &> _modules.lis_
# cat _modules.lis_
# /bin/rm -f _modules.lis_
# echo
# echo limits
# echo
# ulimit -a
echo
echo "Environment Variables"
echo
printenv
# echo
# echo "ldd output"
# echo
# ldd your_executable

#Now you can put in your parallel launch command.
#For each different parallel executable you launch we recommend
#adding a corresponding ldd command to verify that the environment
#that is loaded corresponds to the environment the executable was built in.

# set -euo pipefail
set -u

#####################
# Path settings
#####################
SCRIPT_DIR="/qfs/projects/oddite/peng599/1kgenome_qfs/datalife/tutorials/evaluation_scripts/performance/1000genome_plot/1000genome_perf_number/1kgenome_bin"
NFS_ORIGIN_1KGENOME_DIR="/qfs/projects/oddite/peng599/1kgenome_qfs/1kgenome_sbatch_deception"
BEEGFS_ORIGIN_1KGENOME_DIR="/rcfs/projects/datamesh/peng599/1kgnome_rcfs/1kgenome_sbatch_deception"
LINUX_RESOURCE_DETECT="/qfs/projects/oddite/peng599/1kgenome_qfs/linux_resource_detect/remote_data_transfer.sh"
PREPARE_DATA_SH="/qfs/projects/oddite/peng599/1kgenome_qfs/utils/util01.prepare_data.v2.sh"
REMOVE_LOCAL_DATA_SH="/qfs/projects/oddite/peng599/1kgenome_qfs/utils/util02.remove_local_data.v0.sh"
# SIZE_37G_IN_BYTES=$(du -sb ${ORIGIN_1KGENOME_DIR} | grep -o -E '^[0-9]+([.][0-9]+)?')
# SIZE_37G_IN_KB=$(du -s ${ORIGIN_1KGENOME_DIR} | grep -o -E '^[0-9]+([.][0-9]+)?')
SIZE_37G_IN_BYTES=38089130668
SIZE_37G_IN_KB=37346388
PREV_PWD=$(readlink -f .)
DATASET_DIR_NAME="workspace.${SLURM_JOBID}.${SLURM_JOB_NAME}"
DATALIFE_LIB_PATH="/qfs/projects/oddite/peng599/FlowForecaster/datalife/build/flow-monitor/src/libmonitor.so"

export DATALIFE_OUTPUT_PATH="${PREV_PWD}/datalife_stats.${SLURM_JOB_NAME}.${SLURM_JOBID}"
export DATALIFE_FILE_PATTERNS="\
*.fits, *.vcf, *.lht, *.fna, *.*.bt2, \
*.fastq, *.fasta.amb, *.fasta.sa, *.fasta.bwt, *.fasta.pac, \
*.fasta.ann, *.fasta, *.stf, *.out, *.dot, \
*.gz, *.tar.gz, *.dcd, *.pt, *.h5, \
*.nc, SAS, EAS, GBR, AMR, \
AFR, EUR, ALL, *.datalifetest \
"

echo
echo "PREV_PWD: ${PREV_PWD}"
echo

echo
echo "DATALIFE_OUTPUT_PATH: ${DATALIFE_OUTPUT_PATH}"
echo

rm -rf "${DATALIFE_OUTPUT_PATH}"
mkdir -p "${DATALIFE_OUTPUT_PATH}"

##############
# Preparation
##############

CHROMOSOMES=10
NUM_NODES=$SLURM_JOB_NUM_NODES

ITERATION=$(( $CHROMOSOMES / $NUM_NODES -1 ))

# if ITERATION is 0, set to 1
if [ "$ITERATION" -lt "0" ]
then
    echo "ITERATION is 0, set to 1"
    ITERATION=1
fi


# PROBLEM_SIZE=4 # the maximum number of tasks within a stage !!!need to modify as needed!!!
PROBLEM_SIZE=300 # the maximum number of tasks within a stage !!!need to modify as needed!!!
# the `SBATCH -N -n` needs to modify as well !!!

# NUM_TASKS_PER_NODE=$((($SLURM_NTASKS/$SLURM_JOB_NUM_NODES))
# NUM_TASKS_PER_NODE=$(((PROBLEM_SIZE+NUM_TASKS_PER_NODE)/NUM_NODES)) # (fixed) This is the max number of cores per node
#NUM_NODES=$(((PROBLEM_SIZE+NUM_TASKS_PER_NODE-1)/NUM_TASKS_PER_NODE))
# echo "PROBLEM SIZE: $PROBLEM_SIZE SLURM_NTASKS_PER_NODE: $SLURM_NTASKS_PER_NODE NUM_NODES: $NUM_NODES"
echo "PROBLEM_SIZE: $PROBLEM_SIZE NUM_NODES: $NUM_NODES"

NODE_NAMES=`echo $SLURM_JOB_NODELIST | scontrol show hostnames`
list=()
while read -ra tmp; do
    list+=("${tmp[@]}")
done <<< "$NODE_NAMES"

host_list=$(echo "$NODE_NAMES" | tr '\n' ',')
echo "host_list: $host_list"
# readarray -t host_list <<< "$NODE_NAMES"


################
# Main workflow
################

hostname;date;

# echo "Making directory at $CURRENT_DIR ..."
# srun -n$NUM_NODES -w $host_list --exclusive mkdir -p $CURRENT_DIR

prepare_data_time_list=()
individuals_time_list=()
merge_sifting_time_list=()
mutation_overlap_time_list=()
frequency_time_list=()
workflow_time_list=()
total_time_list=()
col_header="Tasks"

# ## Get Storage options
# GET_STORAGE_OPTIONS
# echo 
# echo "STORAGE_OPTIONS:"
# echo "${STORAGE_OPTIONS}"
# echo 

## Iterate over all storage options

TT_TIME_START=$(date +%s.%N)

# for option in ${STORAGE_OPTIONS}; do
#     IFS="," read -ra tmp_opt <<< "${option}"
#     root_path=${tmp_opt[0]}
#     root_type=${tmp_opt[1]}

    # # DEBUG
    # if [ ! ${root_type} = "nfs" ]; then
    #     continue
    # fi
    # # End DEBUG

# Storage Options

root_path="/qfs/projects/oddite/peng599"
root_type="nfs"

total_time_start=$SECONDS

# Prepare the data

CURRENT_DIR="/people/peng599/Projects/Datamesh/qfs/1kgenome_qfs/pg7_1kgenome_bluesky_datalife_debug/1kgenome_files"

#
# Run the workflow
#
cd "${CURRENT_DIR}"


echo
echo "#####################"
echo "# Task : sifting.py #"
echo "#####################"
echo

set -x
LD_PRELOAD=$DATALIFE_LIB_PATH \
    $PYTHON_PATH "/people/peng599/Projects/Datamesh/qfs/1kgenome_qfs/pg7_1kgenome_bluesky_datalife_debug/1kgenome_files/sifting.py" "/qfs/projects/oddite/peng599/1kgenome_qfs/1kgenome_sbatch_deception/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf" 1 &
set +x
wait


# Change back PWD
cd "${PREV_PWD}"

# done # Iterate over all storage options

hostname;date;
sacct -j $SLURM_JOB_ID -o jobid,submit,start,end,state


TT_TIME_END=$(date +%s.%N)
TT_TIME_EXE=$(echo "${TT_TIME_END} - ${TT_TIME_START}" | bc -l)
echo
echo "TT_TIME_EXE(s): ${TT_TIME_EXE}"
echo

collect_file="${PREV_PWD}/R.${SLURM_JOB_NAME}.${SLURM_JOBID}.all_times.csv"
echo "TT_TIME_EXE(s): ${TT_TIME_EXE}" > ${collect_file}