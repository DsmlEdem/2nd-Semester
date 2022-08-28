#!/bin/bash

#PBS -l nodes=1:ppn=1
#PBS -o compile_ex2.out
#PBS -e compile_ex2.err

cd ${HOME}/lab2_omp/ex2

gcc -O3 -fopenmp Variables.c -o variables
