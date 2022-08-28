#!/bin/bash

#PBS -l nodes=1:ppn=8
#PBS -o run_ex3.out
#PBS -e run_ex3.err

cd ${HOME}/lab2_omp/ex3

OMP_NUM_THREADS=1 ./vecadd
OMP_NUM_THREADS=2 ./vecadd
OMP_NUM_THREADS=4 ./vecadd
OMP_NUM_THREADS=8 ./vecadd

