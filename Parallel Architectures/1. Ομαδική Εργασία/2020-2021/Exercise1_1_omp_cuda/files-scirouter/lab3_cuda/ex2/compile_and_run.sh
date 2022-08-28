#PBS -o gpu.out
#PBS -j oe
##PBS -e gpu.err
#PBS -l walltime=06:00:00


export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

## Change this to the directory of your executable!
cd /home/parml/parml02/lab3_cuda/ex2
gcc -O3 vector_add.c -std=gnu99 -o vecadd_cpu
nvcc -O3 vector_add.cu -o vecadd_gpu

echo "--------------"
time ./vecadd_cpu 5000000
echo "--------------"
time ./vecadd_gpu 5000000

