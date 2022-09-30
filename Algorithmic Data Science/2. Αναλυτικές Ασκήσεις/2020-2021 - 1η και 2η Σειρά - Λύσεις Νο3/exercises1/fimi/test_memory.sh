#!/bin/bash

# This script was created for testing the memory need of different FIM implementation on
# different databases with different parameteres (support threshold in our case).
# The script needs one parameter, that is the name of the file the test result are written to.
# For example: ./test_running_time_input test_results.txt
# author: Ferenc Bodon
# email: bodon@cs.bme.hu
# date: 04/03/2004

result_file=$1
# email_address=your_name@domain

datadir=datasets/
program_vector="fimi01/apriori"

database[1]=kosarak.dat
minsupp_vector[1]="0.9 0.8 0.7 0.6"

database[2]=accidents.dat
minsupp_vector[2]="0.9 0.8 0.7 0.6"

database[3]=pumsb.dat
minsupp_vector[3]="0.9 0.8 0.7 0.6"

echo PEAK MEMORY \(HEAD + STACK\) USAGES >>$result_file
for((index=1;$index<4;index++));
do
	echo ${database[$index]} database>>$result_file;
	for minsupp in ${minsupp_vector[$index]};
	do
		echo >>$result_file;
		echo minsupp: $minsupp>>$result_file;
		for program in $program_vector;
		do
			memusage $program ${datadir}${database[$index]} output.txt $minsupp 2>&1|head -2|tail -1|awk '{print ($9 + $12)/1048576}'>>$result_file;
		done;
		
	done;
	echo -------------------------- >>$result_file;
done

# mail -s "Simulation has finished!" $email_address<$result_file
