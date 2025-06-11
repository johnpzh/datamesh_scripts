siftfile='SIFT.chr1.vcf'

grep -n "deleterious\|tolerated" /qfs/projects/oddite/peng599/1kgenome_qfs/1kgenome_sbatch_deception/ALL.chr1.phase3_shapeit2_mvncall_integrated_v5.20130502.sites.annotation.vcf &> ${siftfile}

