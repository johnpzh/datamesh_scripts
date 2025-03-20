jid2=$(sbatch sbatch/bluesky_02Nodes_allStorages_1kgenome_parallel_6000.v1.storage_path.sbatch | grep -o -E '[0-9]+$')

jid5=$(sbatch --dependency=afterok:$jid2 sbatch/bluesky_05Nodes_allStorages_1kgenome_parallel_6000.v1.storage_path.sbatch | grep -o -E '[0-9]+$')

jid10=$(sbatch --dependency=afterok:$jid5 sbatch/bluesky_10Nodes_allStorages_1kgenome_parallel_6000.v1.storage_path.sbatch | grep -o -E '[0-9]+$')

jid20=$(sbatch --dependency=afterok:$jid10 sbatch/bluesky_20Nodes_allStorages_1kgenome_parallel_6000.v1.storage_path.sbatch | grep -o -E '[0-9]+$')

# jid30=$(sbatch --dependency=afterok:$jid20 sbatch/bluesky_30Nodes_allStorages_1kgenome_parallel_6000.v1.storage_path.sbatch | grep -o -E '[0-9]+$')

echo "Submitted jobs $jid2 $jid5 $jid10 $jid20"