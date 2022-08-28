#!/bin/bash

#PBS -l nodes=1:ppn=1
#PBS -o compile_ex1.out
#PBS -e compile_ex1.err

cd ${HOME}/lab2_omp/ex1
gcc -O3 -fopenmp HelloWorld.c -o helloworld
