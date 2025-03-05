DATASET_DIR_NAME="workspace_1kgenome"
LINUX_RESOURCE_DETECT="/qfs/projects/oddite/peng599/1kgenome_qfs/linux_resource_detect/remote_data_transfer.sh"
SIZE_40G=41943040

## Read storage CSV
local_dir_config="local_dir_config.csv"
if [ ! -s ${local_dir_config} ]; then
    # generate the storage config file
    if [ -s ${LINUX_RESOURCE_DETECT} ]; then
        echo
        echo "Running LINUX_RESOURCE_DETECT ..."
        echo
        bash ${LINUX_RESOURCE_DETECT}
        echo
        echo "Generated ${local_dir_config}"
        echo
    else
        echo "Error: not found ${local_dir_config} nor linux_resource_detect (${LINUX_RESOURCE_DETECT})"
        exit -1
    fi
fi

storage_options=$(csvsql --query "SELECT Actual_Path, Type FROM local_dir_config WHERE Avail_KB > ${SIZE_40G} GROUP BY Type" ${local_dir_config} | tail -n +2)
echo 
echo "storage_options:"
echo "${storage_options}"
echo 

## Iterate over all storage options

TT_TIME_START=$(date +%s.%N)

for option in ${storage_options}; do
    IFS="," read -ra tmp_opt <<< "${option}"
    root_path=${tmp_opt[0]}
    root_type=${tmp_opt[1]}

    # Prepare the data
    CURRENT_DIR="${root_path}/${DATASET_DIR_NAME}"
    echo
    echo "CURRENT_DIR: ${CURRENT_DIR}"
    echo
    if [ -d ${CURRENT_DIR} ]; then
        echo
        echo "Removing ${CURRENT_DIR} ..."
        echo
        start_time=$(date +%s.%N)
        # set -x
        # rm -rf "${CURRENT_DIR}"
        output=$(du "${CURRENT_DIR}" | tail -n 1)
        number=$(echo ${output} | grep -o -E '^[0-9]+([.][0-9]+)?')
        echo "output: ${output}"
        echo "number: ${number}"

        if [ ${number} -ge ${SIZE_40G} ]; then
            echo "Greater"
        else
            echo "Less"
        fi
        # set +x
        end_time=$(date +%s.%N)
        exe_time=$(echo "${end_time} - ${start_time}" | bc -l)
        echo
        echo "Removed ${CURRENT_DIR} (${exe_time} secs)"
        echo
    fi
done

TT_TIME_END=$(date +%s.%N)
TT_TIME_EXE=$(echo "${TT_TIME_END} - ${TT_TIME_START}" | bc -l)
echo
echo "TT_TIME_EXE(s): ${TT_TIME_EXE}"
echo

