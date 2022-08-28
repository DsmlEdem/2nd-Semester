#!/bin/bash

#PBS -l nodes=1:ppn=8
#PBS -o run_ex4.out
#PBS -e run_ex4.err

cd ${HOME}/lab2_omp/ex4

OMP_NUM_THREADS=1 ./dotproduct
OMP_NUM_THREADS=2 ./dotproduct
OMP_NUM_THREADS=4 ./dotproduct
OMP_NUM_THREADS=8 ./dotproduct

