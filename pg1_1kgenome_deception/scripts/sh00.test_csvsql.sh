linux_resource_detect="/qfs/projects/oddite/peng599/1kgenome_qfs/linux_resource_detect/remote_data_transfer.sh"

## Read storage CSV
local_dir_config="local_dir_config.csv"
if [ ! -s ${local_dir_config} ]; then
    # generate the storage config file
    if [ -s ${linux_resource_detect} ]; then
        bash ${linux_resource_detect}
        echo
        echo "Generated ${local_dir_config}"
        echo
    else
        echo "Error: not found ${local_dir_config} nor linux_resource_detect (${linux_resource_detect})"
        exit -1
    fi
fi

SIZE_37G_IN_KB=1000
set -x
storage_options=$(csvsql --query "\
                    SELECT Actual_Path, Type \
                    FROM local_dir_config \
                    WHERE Avail_KB > ${SIZE_37G_IN_KB} \
                        AND Actual_Path NOT LIKE '%people/${USER}%'
                    GROUP BY Type" \
                    ${local_dir_config})
set +x


storage_roots=$(echo "${storage_options}" | tail -n +2)
for root_path in ${storage_roots}; do
    echo "root_path: ${root_path}"
done

# echo
# echo "Again"
# echo
# table_rows=$(csvsql --query "SELECT Actual_Path, Type FROM local_dir_config WHERE Avail_KB > 0 GROUP BY Type" ${local_dir_config})
# pool=$(echo "${table_rows}" | tail -n +2)
# for storage_option in ${pool}; do
#     echo "storage_option: ${storage_option}"
# done

# echo
# echo "Finally"
# echo
# storage_options=$(csvsql --query "SELECT Actual_Path, Type FROM local_dir_config WHERE Avail_KB > 0 GROUP BY Type" ${local_dir_config} | tail -n +2)
# # options=$(echo "${table_rows}" | tail -n +2)
# for option in ${storage_options}; do
#     echo "storage_option: ${option}"
#     IFS="," read -ra tmp_opt <<< "${option}"
#     storage_path=${tmp_opt[0]}
#     storage_type=${tmp_opt[1]}
#     echo "storage_path: ${storage_path} storage_type: ${storage_type}"
# done
