#PBS -o gpu.out
#PBS -j oe
##PBS -e gpu.err
#PBS -l walltime=06:00:00

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

## Change this to the directory of your executable!
cd /home/parml/parml02/lab3_cuda_solutions/ex3
nvcc -O3 dot_product.cu -o dot
nvcc -O3 dot_product_solved.cu -o dot_solved
nvcc -O3 dot_product_shared.cu -o dot_shared
nvcc -O3 dot_product_shared_optimized.cu -o dot_shared_optimized
echo "--------------"
time ./dot 1000000
echo "--------------"
time ./dot_solved 1000000
echo "--------------"
time ./dot_shared 1000000
echo "--------------"
time ./dot_shared_optimized 1000000
