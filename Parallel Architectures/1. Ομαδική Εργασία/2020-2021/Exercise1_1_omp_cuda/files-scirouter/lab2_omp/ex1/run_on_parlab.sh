#!/bin/bash

#PBS -l nodes=1:ppn=8
#PBS -o run_ex1.out
#PBS -e run_ex1.err

cd ${HOME}/lab2_omp/ex1

export OMP_NUM_THREADS=8
./helloworld

