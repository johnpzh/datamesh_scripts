#!/bin/bash
#SBATCH --job-name="ws_2-nodes_datalife_1kgenome"
#SBATCH --partition=slurm
######SBATCH --exclude=dc[119,077]
#SBATCH --account=datamesh
#SBATCH -N 2
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
export PYTHON_PATH=$(command -v python)


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


########################
# Environment variables
########################

export PREV_PWD=$(readlink -f .)
# export DATALIFE_OUTPUT_PATH="${PREV_PWD}/datalife_stats.${SLURM_JOB_NAME}.${SLURM_JOBID}"
export DATALIFE_OUTPUT_PATH="${PREV_PWD}/datalife_stats"
export DATALIFE_FILE_PATTERNS="\
*.fits, *.vcf, *.lht, *.fna, *.*.bt2, \
*.fastq, *.fasta.amb, *.fasta.sa, *.fasta.bwt, *.fasta.pac, \
*.fasta.ann, *.fasta, *.stf, *.out, *.dot, \
*.gz, *.tar.gz, *.dcd, *.pt, *.h5, \
*.nc, SAS, EAS, GBR, AMR, \
AFR, EUR, ALL, *.chr*.txt, *.datalifetest \
"

TT_TIME_START=$(date +%s.%N)

#####################
# Launch the monitor
#####################
set -x
python py00.event_monitor.py "${DATALIFE_OUTPUT_PATH}" >> "R.${SLURM_JOB_NAME}.${SLURM_JOBID}.events.log" &
set +x

######################
# Launch the workflow
######################
set -x
bash sbatch/sh03.datalife.bluesky_nfs_1kgenome_6000.v0.workspace.sh
set +x

######################
# Put off the exit
######################
sleep 11

TT_TIME_END=$(date +%s.%N)
TT_TIME_EXE=$(echo "${TT_TIME_END} - ${TT_TIME_START}" | bc -l)
echo
echo "TT_TIME_EXE(s): ${TT_TIME_EXE}"
echo

collect_file="${PREV_PWD}/R.${SLURM_JOB_NAME}.${SLURM_JOBID}.all_times.csv"
echo "TT_TIME_EXE(s): ${TT_TIME_EXE}" > ${collect_file}