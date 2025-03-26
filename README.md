# Datamesh Scripts

## Set up Submodules
Run
```bash
$ git clone https://github.com/johnpzh/datamesh_scripts.git 
$ cd datamesh_scripts
$ git submodule update --init
$ export REPO_ROOT=$(pwd)
```
This will set up submodules [datalife](https://github.com/pnnl/datalife) and [linux_resource_detect](https://github.com/candiceT233/linux_resource_detect).

## Install Dependent Python Library
```bash
$ pip install numpy csvkit networkx matplotlib pandas sortedcontainers
```

## Run 1000Genome Workflow Using SLURM
1. Prepare 1000Genome data at `/NFS/1kgenome_sbatch_deception` and `/BEEGFS/1kgenome_sbatch_deception`.

2. Change the paths in `${REPO_ROOT}/pg1_1kgenome/sbatch/deception_pfs_1kgenome_parallel_6000_1.v1.iterate_storage.sbatch`
```bash
SCRIPT_DIR="${REPO_ROOT}/datalife/tutorials/evaluation_scripts/performance/1000genome_plot/1000genome_perf_number/1kgenome_bin"
NFS_ORIGIN_1KGENOME_DIR="/NFS/1kgenome_sbatch_deception"
BEEGFS_ORIGIN_1KGENOME_DIR="/BEEGFS/1kgenome_sbatch_deception"
LINUX_RESOURCE_DETECT="${REPO_ROOT}/linux_resource_detect/remote_data_transfer.sh"
PREPARE_DATA_SH="${REPO_ROOT}/utils/util01.prepare_data.v2.sh"
```

3. Submit the SLURM script. Under the repo root, run
```bash
$ cd pg1_1kgenome_deception
$ sbatch sbatch/deception_02Nodes_allStorages_1kgenome_parallel_6000.v1.storage_path.sbatch
```

4. Check the results in `.out`, `.err`, and `.csv`.