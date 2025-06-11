export DATALIFE_OUTPUT_PATH="/people/peng599/Projects/Datamesh/qfs/1kgenome_qfs/pg7_1kgenome_bluesky_datalife_debug/datalife_stats"
export DATALIFE_FILE_PATTERNS="\
*.vcf \
"


# LD_PRELOAD=/qfs/projects/oddite/peng599/FlowForecaster/datalife/build/flow-monitor/src/libmonitor.so \
python py01.grep.py

# LD_PRELOAD=/qfs/projects/oddite/peng599/FlowForecaster/datalife/build/flow-monitor/src/libmonitor.so \
# bash sh01.grep.sh

siftfile='SIFT.chr1.vcf'
wc -l ${siftfile}
# rm -rf ${siftfile}