#!/bin/bash

#PBS -l nodes=1:ppn=1
#PBS -o compile_ex3.out
#PBS -e compile_ex3.err

cd ${HOME}/lab2_omp/ex3

gcc -O3 -fopenmp VecAdd.c -o vecadd
