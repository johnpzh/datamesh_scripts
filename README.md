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
$ pip install numpy csvkit
```

## Run 1000Genome Workflow using SLURM
1. Prepare 1000Genome data at `${REPO_ROOT}/1kgenome_sbatch_deception`.

2. Change the paths in `${REPO_ROOT}/pg1_1kgenome/sbatch/deception_pfs_1kgenome_parallel_6000_1.v1.iterate_storage.sbatch`
```bash
SCRIPT_DIR="${REPO_ROOT}/datalife/tutorials/evaluation_scripts/performance/1000genome_plot/1000genome_perf_number/1kgenome_bin"
ORIGIN_1KGENOME_DIR="${REPO_ROOT}/1kgenome_sbatch_deception"
LINUX_RESOURCE_DETECT="${REPO_ROOT}/linux_resource_detect/remote_data_transfer.sh"
PREPARE_DATA_SH="${REPO_ROOT}/pg1_1kgenome/sbatch/util00.prepare_data.sh"
```

3. Submit the SLURM script. Under the repo root, run
```bash
$ cd pg1_1kgenome
$ sbatch sbatch/deception_pfs_1kgenome_parallel_6000_1.v1.iterate_storage.sbatch
```

4. Check the results in `.out`, `.err`, and `.csv`.