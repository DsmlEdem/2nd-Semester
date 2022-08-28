#PBS -o gpu.out
#PBS -j oe
##PBS -e gpu.err
#PBS -l walltime=06:00:00

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

## Change this to the directory of your executable!
cd /home/parml/parml02/lab3_cuda/ex3
nvcc -O3 dot_product.cu -o dot
echo "--------------"
time ./dot 500000
