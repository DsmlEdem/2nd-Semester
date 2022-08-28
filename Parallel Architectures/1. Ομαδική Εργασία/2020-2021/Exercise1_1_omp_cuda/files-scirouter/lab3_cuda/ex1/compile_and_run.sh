#PBS -o gpu.out
#PBS -e gpu.err
#PBS -l walltime=01:00:00

export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

## Change this to the directory of your executable!
cd /home/parml/parml02/lab3_cuda/ex1
nvcc -O3 hello_world.cu -o helloworld
./helloworld
