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
DATASET_DIR_NAME="workspace.${SLURM_JOBID}.${SLURM_JOB_NAME}"
DATALIFE_LIB_PATH="/qfs/projects/oddite/peng599/FlowForecaster/datalife/build/flow-monitor/src/libmonitor.so"


echo
echo "PREV_PWD: ${PREV_PWD}"
echo

echo
echo "DATALIFE_OUTPUT_PATH: ${DATALIFE_OUTPUT_PATH}"
echo

if [ ! -d "${DATALIFE_OUTPUT_PATH}" ]; then
    mkdir -p "${DATALIFE_OUTPUT_PATH}"
fi
rm -rf "${DATALIFE_OUTPUT_PATH}/*"

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

# set -x

#########
# Tasks
#########

function START_INDIVIDUALS() {
    # set -x

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
                set -x
                LD_PRELOAD=$DATALIFE_LIB_PATH \
                srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals.py $CURRENT_DIR/ALL.chr${ii}.250000.vcf $ii $((1+j*200)) $((201+j*200)) 6000 &
                set +x
                counter=$(($counter + 1))
                # echo "counter: $counter"
            fi
	    done
    done
    # sleep 3

}

function START_INDIVIDUALS_MERGE() {

    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        let ii=i+1
        # 10 merge tasks in total
        set -x
        LD_PRELOAD=$DATALIFE_LIB_PATH \
        srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals_merge.py $ii $CURRENT_DIR/chr${ii}n-1-201.tar.gz $CURRENT_DIR/chr${ii}n-201-401.tar.gz $CURRENT_DIR/chr${ii}n-401-601.tar.gz $CURRENT_DIR/chr${ii}n-601-801.tar.gz $CURRENT_DIR/chr${ii}n-801-1001.tar.gz $CURRENT_DIR/chr${ii}n-1001-1201.tar.gz $CURRENT_DIR/chr${ii}n-1201-1401.tar.gz $CURRENT_DIR/chr${ii}n-1401-1601.tar.gz $CURRENT_DIR/chr${ii}n-1601-1801.tar.gz $CURRENT_DIR/chr${ii}n-1801-2001.tar.gz $CURRENT_DIR/chr${ii}n-2001-2201.tar.gz $CURRENT_DIR/chr${ii}n-2201-2401.tar.gz $CURRENT_DIR/chr${ii}n-2401-2601.tar.gz $CURRENT_DIR/chr${ii}n-2601-2801.tar.gz $CURRENT_DIR/chr${ii}n-2801-3001.tar.gz $CURRENT_DIR/chr${ii}n-3001-3201.tar.gz $CURRENT_DIR/chr${ii}n-3201-3401.tar.gz $CURRENT_DIR/chr${ii}n-3401-3601.tar.gz $CURRENT_DIR/chr${ii}n-3601-3801.tar.gz $CURRENT_DIR/chr${ii}n-3801-4001.tar.gz $CURRENT_DIR/chr${ii}n-4001-4201.tar.gz $CURRENT_DIR/chr${ii}n-4201-4401.tar.gz $CURRENT_DIR/chr${ii}n-4401-4601.tar.gz $CURRENT_DIR/chr${ii}n-4601-4801.tar.gz $CURRENT_DIR/chr${ii}n-4801-5001.tar.gz $CURRENT_DIR/chr${ii}n-5001-5201.tar.gz $CURRENT_DIR/chr${ii}n-5201-5401.tar.gz $CURRENT_DIR/chr${ii}n-5401-5601.tar.gz $CURRENT_DIR/chr${ii}n-5601-5801.tar.gz $CURRENT_DIR/chr${ii}n-5801-6001.tar.gz &
        set +x
    done

}

function START_SIFTING() {

    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        # 10 sifting tasks in total
        let ii=i+1
        set -x
        LD_PRELOAD=$DATALIFE_LIB_PATH \
        srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/sifting.py $CURRENT_DIR/ALL.chr${ii}.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf $ii &
        set +x
    done

}

function START_MUTATION_OVERLAP() {

    FNAMES=("SAS EAS GBR AMR AFR EUR ALL")
    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        for j in $FNAMES
        do
            let ii=i+1
            set -x
            LD_PRELOAD=$DATALIFE_LIB_PATH \
            srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/mutation_overlap.py -c $ii -pop $j &
            set +x
        done
    done

}

function START_FREQUENCY() {

    FNAMES=("SAS EAS GBR AMR AFR EUR ALL")
    for i in $(seq 0 9)
    do
        node_idx=$(($i % $NUM_NODES))
        running_node=${list[$node_idx]}
        for j in $FNAMES
        do
            let ii=i+1
            set -x
            LD_PRELOAD=$DATALIFE_LIB_PATH \
            srun -w $running_node -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/frequency.py -c $ii -pop $j &
            set +x
        done
    done

}


############
# Utilities
############



function GET_STORAGE_OPTIONS() {
    filename="local_dir_config_${SLURM_JOBID}_${SLURM_JOB_NAME}"
    local_dir_config="dir_config_${SLURM_JOBID}_${SLURM_JOB_NAME}.csv"
    full_path="${PREV_PWD}/${filename}.csv"
    
    # Remove it, because different clusters might have different storage options.
    rm -f "${full_path}"
    if [ ! -s ${full_path} ]; then
        # generate the storage config file
        if [ -s ${LINUX_RESOURCE_DETECT} ]; then
            echo
            echo "Running LINUX_RESOURCE_DETECT ..."
            echo
            set -x
            bash ${LINUX_RESOURCE_DETECT} -o "${local_dir_config}"
            set +x
            echo
            echo "Generated ${full_path}"
            echo
        else
            echo "Error: not found ${full_path} nor linux_resource_detect (${LINUX_RESOURCE_DETECT})"
            exit -1
        fi
    fi

    # Skip `people/$USER` to avoid the interference and the size limit in home directory.
    set -x
    STORAGE_OPTIONS=$(csvsql --query "\
SELECT Actual_Path, Type \
FROM ${filename} \
WHERE Avail_KB > ${SIZE_37G_IN_KB} \
  AND Actual_Path NOT LIKE '%people/${USER}%' \
GROUP BY Type" \
${full_path} | tail -n +2)
    set +x

    rm -f "${full_path}"
}


function CLEANUP() {

    start_time=$(date +%s.%N)

    # rm -rf chr*-freq* 
    # rm -rf chr*.tar.gz
    # find . -depth -type d -name "output_no_sift" -exec rm -rf {} \;
    # find . -depth -type d -name "plots_no_sift" -exec rm -rf {} \;

    # CURRENT_DIR contains either copied local data or created symlinks.
    # cd "${PREV_PWD}"
    # set -x
    # rm -rf "${CURRENT_DIR}"
    # set +x

    cd "${PREV_PWD}"
    if [ "${root_type}" = "beegfs" ] || [ "${root_type}" = "nfs" ]; then
        # Shared storage only need delete once
        set -x
        rm -rf "${CURRENT_DIR}"
        set +x
    else
        # Local storage needs to be done by each nodes
        for node in ${list[@]}; do
            set -x
            srun -w ${node} -n1 -N1 --exclusive bash "${REMOVE_LOCAL_DATA_SH}" &
            set +x
        done
    fi
    wait

    end_time=$(date +%s.%N)
    exe_time=$(echo "${end_time} - ${start_time}" | bc -l)
    echo
    echo "Removed results. (${exe_time} secs)"
    echo
}


# set -x 

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

CURRENT_DIR="${root_path}/${DATASET_DIR_NAME}"

if [ ${root_type} = "nfs" ]; then
    ORIGIN_1KGENOME_DIR="${NFS_ORIGIN_1KGENOME_DIR}"
elif [ ${root_type} = "beegfs" ]; then
    ORIGIN_1KGENOME_DIR="${BEEGFS_ORIGIN_1KGENOME_DIR}"
elif [ -d ${BEEGFS_ORIGIN_1KGENOME_DIR} ]; then
    ORIGIN_1KGENOME_DIR="${BEEGFS_ORIGIN_1KGENOME_DIR}"
elif [ -d ${NFS_ORIGIN_1KGENOME_DIR} ]; then
    ORIGIN_1KGENOME_DIR="${NFS_ORIGIN_1KGENOME_DIR}"
else
    echo "Error: both ${NFS_ORIGIN_1KGENOME_DIR} and ${BEEGFS_ORIGIN_1KGENOME_DIR} do not exist. Exit."
    exit -1
fi

export CURRENT_DIR
export root_type
export SIZE_37G_IN_BYTES
export ORIGIN_1KGENOME_DIR
start_time=$SECONDS
if [ "${root_type}" = "beegfs" ] || [ "${root_type}" = "nfs" ]; then
    # Shared storage only need copy once
    set -x
    bash "${PREPARE_DATA_SH}"
    set +x
else
    # Local storage needs to be done by each nodes
    for node in ${list[@]}; do
        set -x
        srun -w ${node} -n1 -N1 --exclusive bash "${PREPARE_DATA_SH}" &
        set +x
    done
fi
wait
duration=$(($SECONDS - $start_time))
echo "prepare_data : $(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed ($duration secs)."
prepare_data_time_list+=(${duration})

col_header+=",${root_type}(${root_path})"


workflow_start_time=$SECONDS

#
# Run the workflow
#
# cd "${CURRENT_DIR}"
WORKSPACE_PWD="${PREV_PWD}/output_workspace"
cd "${WORKSPACE_PWD}"

echo
echo "WORKSPACE_PWD: $(pwd)"
echo


## Stage 1 : Individuals
echo
echo "#########################"
echo "# Task : individuals.py #"
echo "#########################"
echo

set -x
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals.py $CURRENT_DIR/ALL.chr1.250000.vcf 1 1 201 6000 &
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals.py $CURRENT_DIR/ALL.chr1.250000.vcf 1 201 401 6000 &
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals.py $CURRENT_DIR/ALL.chr1.250000.vcf 1 401 601 6000 &
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals.py $CURRENT_DIR/ALL.chr1.250000.vcf 1 601 801 6000 &
set +x
wait

## Stage 2 : Individuals merge + Sifting

echo
echo "###############################"
echo "# Task : individuals_merge.py #"
echo "###############################"
echo

set -x
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/individuals_merge.py 1 \
        "${WORKSPACE_PWD}"/chr1n-1-201.tar.gz \
        "${WORKSPACE_PWD}"/chr1n-201-401.tar.gz \
        "${WORKSPACE_PWD}"/chr1n-401-601.tar.gz \
        "${WORKSPACE_PWD}"/chr1n-601-801.tar.gz &
set +x
wait

echo
echo "#####################"
echo "# Task : sifting.py #"
echo "#####################"
echo

set -x
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/sifting.py $CURRENT_DIR/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf 1 &
set +x
wait

## Stage 3 : Mutation overlap + Frequency

echo
echo "##############################"
echo "# Task : mutation_overlap.py #"
echo "##############################"
echo

set -x
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/mutation_overlap.py -c 1 -pop EAS &
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/mutation_overlap.py -c 1 -pop AMR &
set +x
wait

echo
echo "#######################"
echo "# Task : frequency.py #"
echo "#######################"
echo

set -x
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/frequency.py -c 1 -pop EAS &
LD_PRELOAD=$DATALIFE_LIB_PATH \
    srun -w "${list[0]}" -n1 -N1 --exclusive $PYTHON_PATH $SCRIPT_DIR/frequency.py -c 1 -pop AMR &
set +x
wait


# LOCAL_CLEANUP
echo
echo "Cleaning up"
echo 
CLEANUP

# Change back PWD
cd "${PREV_PWD}"

# done # Iterate over all storage options

hostname;date;
sacct -j $SLURM_JOB_ID -o jobid,submit,start,end,state

###########################
# Save performance numbers
###########################


