#!/bin/bash
#submit using: bsub < /home/gharm/DeepCell/DeepCellHelper/SubmitDeepCellJob.sh
#BSUB -J GPU_job1
#BSUB -o GPU_job1.%J.out
#BSUB -e GPU_job1.%J.error
#BSUB -M 500000 # Reqesting 10GB RAM
#BSUB -R "span[hosts=1] rusage [mem=500000]"
#BSUB -q gpu #input gpu if using gpu

module load CUDA/11.4.1

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:sftp:/home/gharm/DeepCell/cuda/lib64

source /home/gharm/DeepCell/DeepCellEnv/bin/activate

python /home/gharm/DeepCell/DeepCellHelper/RunDeepCell.py
