#!/bin/bash

#PBS -l nodes=1:ppn=2
#PBS -o run_ex2.out
#PBS -e run_ex2.err

cd ${HOME}/lab2_omp/ex2

./variables

