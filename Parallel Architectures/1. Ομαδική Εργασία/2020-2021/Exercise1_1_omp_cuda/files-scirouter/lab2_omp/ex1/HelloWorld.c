/**************************************
Ex. 1: Hello World!

Fill in the requested code.
Compile to executable "helloworld".
Run with 8 threads.

**************************************/

#include <stdio.h>
#include <omp.h>

int main () {
	int NumOfThreads;
	int ThreadID;

	#pragma omp parallel
	/* TODO: Declare a parallel region here */
	{
		// test
		/*TODO: Get the number of threads and store it in NumOfThreads*/
		NumOfThreads=omp_get_num_threads();
		/*TODO: Find the ID of each thread and store it in ThreadID*/
		ThreadID = omp_get_thread_num();
		printf("Hello world from threadd %d out of %d!\n",ThreadID, NumOfThreads);		
	}	
	return 0;
}
