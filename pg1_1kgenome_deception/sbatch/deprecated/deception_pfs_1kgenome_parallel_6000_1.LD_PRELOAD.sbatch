#!/bin/bash
#SBATCH --job-name="deception_2nodes_pfs_6000_1"
#SBATCH --partition=slurm
#SBATCH --exclude=dc[119,077]
#SBATCH -N 2
#SBATCH --time=03:30:00
#SBATCH --output=R_%x.out
#SBATCH --error=R_%x.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=meng.tang@pnnl.gov
#SBATCH --exclusive

DATALIFE_LIB_PATH=/qfs/people/tang584/install/datalife/lib/libmonitor.so
CWD=$(pwd)
rm -rf *.datalife.json *blk_trace.json

NODE_NAMES=`echo $SLURM_JOB_NODELIST|scontrol show hostnames`
SHARE="PFS" # PFS NFS

if [ "$SHARE" == "NFS" ]
then
    echo "Running on NFS"
    SCRIPT_DIR=/qfs/projects/oddite/tang584/1000genome-workflow/bin
    CURRENT_DIR=/qfs/people/tang584/scripts/1kgenome_sbatch_deception #NFS
    # CURRENT_DIR=/qfs/projects/oddite/lenny/hermes_scripts/1kgenome_sbatch_deception #NFS
else
    echo "Running on PFS" # but this behaves like NFS
    PFS_DIR=/rcfs/projects/chess #/files0/oddite
    SCRIPT_DIR=$PFS_DIR/$USER/1000genome-workflow/bin
    CURRENT_DIR=$PFS_DIR/$USER/1kgenome_sbatch_deception #PFS
    mkdir -p $SCRIPT_DIR $CURRENT_DIR
    # Candice: commented out to avoid copying in trials
    # if ! [ -s "$SCRIPT_DIR" ]; then cp -r /qfs/projects/oddite/tang584/1000genome-workflow/bin/* $SCRIPT_DIR/; fi
    # if ! [ -s "$CURRENT_DIR" ]; then cp -r /qfs/people/tang584/scripts/1kgenome_sbatch_deception/* $CURRENT_DIR/; fi
    if ! [ -s "$SCRIPT_DIR" ]; then echo "No files in $SCRIPT_DIR"; realpath $SCRIPT_DIR/*; fi
    if ! [ -s "$CURRENT_DIR" ]; then echo "No files in $CURRENT_DIR"; realpath $CURRENT_DIR/*; fi
    # clear intermediate and freq output
    rm -rf $CURRENT_DIR/chr*-freq* $CURRENT_DIR/tmp* $CURRENT_DIR/merged_chr* $CURRENT_DIR/chr*.tar.gz
fi

# /files0/oddite/$USER/1kgenome_sbatch #SSD Burst Buffer

CHROMOSOMES=10
NUM_NODES=$SLURM_JOB_NUM_NODES

ITERATION=$(( $CHROMOSOMES / $NUM_NODES -1 ))

# if ITERATION is 0, set to 1
if [ "$ITERATION" -lt "0" ]
then
    echo "ITERATION is 0, set to 1"
    ITERATION=1
fi


PROBLEM_SIZE=300 # the maximum number of tasks within a stage !!!need to modify as needed!!!
# the `SBATCH -N -n` needs to modify as well !!!

# NUM_TASKS_PER_NODE=$((($SLURM_NTASKS/$SLURM_JOB_NUM_NODES))
NUM_TASKS_PER_NODE=$(((PROBLEM_SIZE+NUM_TASKS_PER_NODE)/NUM_NODES)) # (fixed) This is the max number of cores per node
#NUM_NODES=$(((PROBLEM_SIZE+NUM_TASKS_PER_NODE-1)/NUM_TASKS_PER_NODE))
echo "PROBLEM SIZE: $PROBLEM_SIZE SLURM_NTASKS_PER_NODE: $SLURM_NTASKS_PER_NODE NUM_NODES: $NUM_NODES"

# module purge
# module load python/3.7.0 gcc/11.2.0

# module purge
# module load python/miniconda3.7 gcc/9.1.0
# PYTHON_PATH=/share/apps/python/miniconda3.7/bin/python

NODE_NAMES=`echo $SLURM_JOB_NODELIST|scontrol show hostnames`
list=()
while read -ra tmp; do
    list+=("${tmp[@]}")
done <<< "$NODE_NAMES"

host_list=$(echo "$NODE_NAMES" | tr '\n' ',')
echo "host_list: $host_list"
# readarray -t host_list <<< "$NODE_NAMES"

# set -x



START_INDIVIDUALS() {
    set -x

    counter=0
    t_count=1

    for i in $(seq 0 9)
    do
        for j in $(seq 0 29)
	do
	    # echo "$i $j"
            if [ "$counter" -lt "$PROBLEM_SIZE" ]
            then
                node_idx=$(($i % $NUM_NODES))
                running_node=${list[$node_idx]}
                # echo "running node: $running_node t$i"
                let ii=i+1
                # No need to change. This is the smallest input allowed.
                echo "srun -w $running_node -n1 -N1 --exclusive $SCRIPT_DIR/individuals.py $CURRENT_DIR/ALL.chr${ii}.250000.vcf $ii $((1+j*200)) $((201+j*200)) 6000"
                
                LD_PRELOAD=$DATALIFE_LIB_PATH \
                srun -w $running_node -n1 -N1 --exclusive $SCRIPT_DIR/individuals.py $CURRENT_DIR/ALL.chr${ii}.250000.vcf $ii $((1+j*200)) $((201+j*200)) 6000 &
                counter=$(($counter + 1))
                # echo "counter: $counter"
            fi
	done
    done
    # sleep 3

}

START_INDIVIDUALS_MERGE() {

    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        let ii=i+1
        # 10 merge tasks in total
        LD_PRELOAD=$DATALIFE_LIB_PATH \
        srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals_merge.py $ii $CURRENT_DIR/chr${ii}n-1-201.tar.gz $CURRENT_DIR/chr${ii}n-201-401.tar.gz $CURRENT_DIR/chr${ii}n-401-601.tar.gz $CURRENT_DIR/chr${ii}n-601-801.tar.gz $CURRENT_DIR/chr${ii}n-801-1001.tar.gz $CURRENT_DIR/chr${ii}n-1001-1201.tar.gz $CURRENT_DIR/chr${ii}n-1201-1401.tar.gz $CURRENT_DIR/chr${ii}n-1401-1601.tar.gz $CURRENT_DIR/chr${ii}n-1601-1801.tar.gz $CURRENT_DIR/chr${ii}n-1801-2001.tar.gz $CURRENT_DIR/chr${ii}n-2001-2201.tar.gz $CURRENT_DIR/chr${ii}n-2201-2401.tar.gz $CURRENT_DIR/chr${ii}n-2401-2601.tar.gz $CURRENT_DIR/chr${ii}n-2601-2801.tar.gz $CURRENT_DIR/chr${ii}n-2801-3001.tar.gz $CURRENT_DIR/chr${ii}n-3001-3201.tar.gz $CURRENT_DIR/chr${ii}n-3201-3401.tar.gz $CURRENT_DIR/chr${ii}n-3401-3601.tar.gz $CURRENT_DIR/chr${ii}n-3601-3801.tar.gz $CURRENT_DIR/chr${ii}n-3801-4001.tar.gz $CURRENT_DIR/chr${ii}n-4001-4201.tar.gz $CURRENT_DIR/chr${ii}n-4201-4401.tar.gz $CURRENT_DIR/chr${ii}n-4401-4601.tar.gz $CURRENT_DIR/chr${ii}n-4601-4801.tar.gz $CURRENT_DIR/chr${ii}n-4801-5001.tar.gz $CURRENT_DIR/chr${ii}n-5001-5201.tar.gz $CURRENT_DIR/chr${ii}n-5201-5401.tar.gz $CURRENT_DIR/chr${ii}n-5401-5601.tar.gz $CURRENT_DIR/chr${ii}n-5601-5801.tar.gz $CURRENT_DIR/chr${ii}n-5801-6001.tar.gz &
    done

}

START_SIFTING() {

    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        # 10 sifting tasks in total
        let ii=i+1
        LD_PRELOAD=$DATALIFE_LIB_PATH \
        srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/sifting.py $CURRENT_DIR/ALL.chr${ii}.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf $ii &
    done

}

START_MUTATION_OVERLAP() {

    FNAMES=("SAS EAS GBR AMR AFR EUR ALL")
    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        for j in $FNAMES
        do
            let ii=i+1
            LD_PRELOAD=$DATALIFE_LIB_PATH \
            srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/mutation_overlap.py -c $ii -pop $j &
        done
    done

}

START_FREQUENCY() {

    FNAMES=("SAS EAS GBR AMR AFR EUR ALL")
    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        for j in $FNAMES
        do
            let ii=i+1
            LD_PRELOAD=$DATALIFE_LIB_PATH \
            srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/frequency.py -c $ii -pop $j &
        done
    done

}

set -x 

hostname;date;

echo "Making directory at $CURRENT_DIR ..."
srun -n$NUM_NODES -w $host_list --exclusive mkdir -p $CURRENT_DIR



total_start_time=$SECONDS

cd $CURRENT_DIR


start_time=$SECONDS
STAGE_IN_INDIVIDUALS
wait
duration=$(($SECONDS - $start_time))
echo "data stage-in for individuals : $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ($duration secs)."


# Stage 1 : Individuals
echo "individuals CHROMOSOME from $START_CHROMOSOME to $END_CHROMOSOME"
start_time=$SECONDS
START_INDIVIDUALS
wait
duration=$(($SECONDS - $start_time))
echo "individuals : $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ($duration secs)."

# Stage 2 : Individuals merge + Sifting
start_time=$SECONDS
echo "individuals_merge from $START_CHROMOSOME to $END_CHROMOSOME"
START_INDIVIDUALS_MERGE
wait
duration=$(($SECONDS - $start_time))
echo "individuals_merge+sifting : $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ($duration secs)."
echo "Sifting from $START_CHROMOSOME to $END_CHROMOSOME"
start_time=$SECONDS
START_SIFTING
wait
duration=$(($SECONDS - $start_time))
echo "sifting : $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ($duration secs)."



# Stage 3 : Mutation overlap + Frequency
start_time=$SECONDS
echo "mutation_overlap from $START_CHROMOSOME to $END_CHROMOSOME"
START_MUTATION_OVERLAP
wait
duration=$(($SECONDS - $start_time))
echo "mutation_overlap : $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ($duration secs)."
start_time=$SECONDS
echo "frequency from $START_CHROMOSOME to $END_CHROMOSOME"
START_FREQUENCY
wait
duration=$(($SECONDS - $start_time))
echo "frequency : $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ($duration secs)."



total_duration=$(($SECONDS - $total_start_time))
echo "All done : $(($total_duration / 60)) minutes and $(($total_duration % 60)) seconds elapsed ($total_duration secs)."

set -x
# check output
echo "Checking all output ----------------"
srun -n$NUM_NODES -w $host_list --exclusive du -h $CURRENT_DIR

LOCAL_CLEANUP

# Candice: do not remove the current dir which contains all initial input for the test run
# # remove current dir
# rm -fr $CURRENT_DIR/*

hostname;date;
sacct -j $SLURM_JOB_ID -o jobid,submit,start,end,state


# Create and move results to the test log folder
TEST_LOG_FOLDER=$CWD/"6000_2n_pfs_datalife_1"
mkdir -p $TEST_LOG_FOLDER
rm -rf $TEST_LOG_FOLDER/*

mv $CURRENT_DIR/*datalife.json $TEST_LOG_FOLDER
mv $CURRENT_DIR/*blk_trace.json $TEST_LOG_FOLDER

mv $CWD/R_*$SLURM_JOB_NAME*.err $TEST_LOG_FOLDER
mv $CWD/R_*$SLURM_JOB_NAME*.out $TEST_LOG_FOLDER
