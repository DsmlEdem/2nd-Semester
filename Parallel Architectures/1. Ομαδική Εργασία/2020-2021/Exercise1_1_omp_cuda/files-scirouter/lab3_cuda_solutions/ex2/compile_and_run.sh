#PBS -o gpu.out
#PBS -j oe
##PBS -e gpu.err
#PBS -l walltime=06:00:00

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

## Change this to the directory of your executable!
##PROJECTDIR="/home/users/panastas/teaching_stuff/par-ML/lab3_cuda_solutions/"
##cd "${PROJECTDIR}/ex2
cd /home/parml/parml02/lab3_cuda_solutions/ex2
gcc -O3 vector_add.c -std=gnu99 -o vecadd_cpu
nvcc -O3 vector_add.cu -o vecadd_gpu
nvcc -O3 vector_add_working.cu -o vecadd_gpu_working
nvcc -O3 vector_add_solved.cu -o vecadd_gpu_solved
echo "--------------"
time ./vecadd_cpu 5000000
echo "--------------"
time ./vecadd_gpu 5000000
echo "--------------"
time ./vecadd_gpu_working 5000000
echo "--------------"
time ./vecadd_gpu_solved 5000000
