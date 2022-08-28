#!/bin/sh

export OMP_NUM_OF_THREADS=1
echo 'Number of threads =' $OMP_NUM_OF_THREADS
./openmp
export OMP_NUM_OF_THREADS=2
echo 'Number of threads =' $OMP_NUM_OF_THREADS
./openmp
export OMP_NUM_OF_THREADS=4
echo 'Number of threads =' $OMP_NUM_OF_THREADS
./openmp
export OMP_NUM_OF_THREADS=8
echo 'Number of threads =' $OMP_NUM_OF_THREADS
./openmp
export OMP_NUM_OF_THREADS=12
echo 'Number of threads =' $OMP_NUM_OF_THREADS
./openmp
