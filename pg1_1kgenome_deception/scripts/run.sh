LIB_PATH=/qfs/projects/oddite/leeh736/git/datalife/flow-monitor/build940/src/libmonitor.so
LIB_PATH=/qfs/projects/oddite/leeh736/git/datalife/flow-monitor/build_no_header/src/libmonitor.so
parallel=false
for i in {1..10}
do
    task_num=$(($i % 5))
    mkdir task$i
    cd task$i
    if [ $task_num -eq 1 ]
    then
        i_start=1
        i_end=20
        if [ $parallel == 'true' ]
        then
            cd ..
            mkdir task${i}.1
            cd task${i}.1
            touch .task_name.individuals
            ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/ALL.chr1.20.vcf /scratch/leeh736/.
            ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/one_chr/data/20130502/columns.txt /scratch/leeh736/.
            LD_PRELOAD=$LIB_PATH /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/individuals.py ALL.chr1.20.vcf 1 1 10 20 &>> run.log
            i_start=10
            i_end=20
            i_num_tasks=2
            cd ..
            cd task$i
        fi
        touch .task_name.individuals
        ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/ALL.chr1.20.vcf .
        ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/one_chr/data/20130502/columns.txt .
        LD_PRELOAD=$LIB_PATH /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/individuals.py ALL.chr1.20.vcf 1 $i_start $i_end 20 &>> run.log
        # multi-tasks from 2nd round 
        parallel=true
        i_prev_task_name=task$i
    elif [ $task_num -eq 2 ]
    then
        touch .task_name.individuals_merge
        target_file=/qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/$i_prev_task_name/chr1n-1-20.tar.gz
        if [ -f "$target_file" ]
        then
            ln -s $target_file .
            n_files_to_merge=false
        else
            echo "$target_file" does not exist
            ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/${i_prev_task_name}.1/chr1n-1-10.tar.gz
            ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/${i_prev_task_name}/chr1n-10-20.tar.gz
            n_files_to_merge=true
        fi
        ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/one_chr/data/20130502/columns.txt .
        ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/ALL.chr1.20.vcf .
        if [ $n_files_to_merge == "false" ]; then
            LD_PRELOAD=$LIB_PATH /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/individuals_merge.py 1 chr1n-1-20.tar.gz &> /dev/null
        else
            LD_PRELOAD=$LIB_PATH /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/individuals_merge.py 1 chr1n-1-10.tar.gz chr1n-10-20.tar.gz &> /dev/null
        fi
        m_prev_task_name=task$i
    elif [ $task_num -eq 3 ]
    then    
        touch .task_name.sifting
        ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/one_chr/data/20130502/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf .
        LD_PRELOAD=$LIB_PATH /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/sifting.py ALL.chr1.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf 1 &> /dev/null
        /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/sifting.py ALL.chr1.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf 1 &> /dev/null
        s_prev_task_name=task$i
    elif [ $task_num -eq 4 ]
    then
        touch .task_name.mutation_overlap
        ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/$s_prev_task_name/sifted.SIFT.chr1.txt .
        ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/one_chr/data/20130502/columns.txt .
        ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/data/populations/SAS .
        ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/$m_prev_task_name/chr1n.tar.gz .
        LD_PRELOAD=$LIB_PATH /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/mutation_overlap.py -c 1 -pop SAS &> /dev/null
    elif [ $task_num -eq 0 ]
    then
        touch .task_name.frequency
        ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/$s_prev_task_name/sifted.SIFT.chr1.txt .
        ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/one_chr/data/20130502/columns.txt .
        ln -s /qfs/projects/oddite/leeh736/git/1000genome-workflow/data/populations/SAS .
        ln -s /qfs/projects/oddite/leeh736/online_analyzer/1k_genomes/$m_prev_task_name/chr1n.tar.gz .
        LD_PRELOAD=$LIB_PATH /qfs/projects/oddite/leeh736/git/1000genome-workflow//bin/frequency.py -c 1 -pop SAS &> /dev/null
    fi
    cd ..
done
