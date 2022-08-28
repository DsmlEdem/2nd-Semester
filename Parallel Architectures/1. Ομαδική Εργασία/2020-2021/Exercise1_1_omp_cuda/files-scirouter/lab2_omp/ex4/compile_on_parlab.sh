#!/bin/bash

#PBS -l nodes=1:ppn=1
#PBS -o compile_ex4.out
#PBS -e compile_ex4.err

cd ${HOME}/lab2_omp/ex4
gcc -O3 -fopenmp DotProduct.c -o dotproduct
