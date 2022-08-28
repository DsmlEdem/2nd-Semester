#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <omp.h>

#define N 100000000

int test ( double * y_serial, double * y_parallel ) {
	int i;

	for ( i = 0 ; i < N ; i++ )
		if ( y_serial[i] != y_parallel[i])
			return 1;
	return 0;
}


int main () {
	double * x1, * x2, *y_serial, * y_parallel;
	double time;
	struct timeval ts,tf;
	int i;

	/* Allocate space for vectors */
	x1 = (double *)malloc ( N * sizeof(double) );
	x2 = (double *)malloc ( N * sizeof(double) );
	y_serial = (double *)malloc ( N * sizeof(double) );
	y_parallel = (double *)malloc ( N * sizeof(double) );


	/* Initialize values of x1 and x2 */
	for ( i = 0 ; i < N ; i++ ) {
		x1[i] = i*0.32;
		x2[i] = i*0.25;
	}

	/* Serial code for vector addition - result in y_serial */
	for ( i = 0 ; i < N ; i++ )
		y_serial[i] = x1[i] + x2[i];


	gettimeofday(&ts, NULL); //Start time measurement

	/* Parallel code for vector addition - result in y_parallel */

	/* TODO: Parallelize this loop */
	/* TODO: Declare a parallel region */
	/* TODO: Parallelize the vector addition operation */
	#pragma omp parallel
	{
	#pragma omp for
	for ( i = 0 ; i < N ; i++ )
		y_parallel[i] = x1[i] + x2[i];
	}

	gettimeofday(&tf, NULL); //Stop time measurement


	/* Check and print results */
	if ( test( y_serial, y_parallel)==0 )
		printf ("Test PASSED! Time: %.5lf ms\n", (tf.tv_sec-ts.tv_sec)*1000+(tf.tv_usec-ts.tv_usec)*0.001);
	else
		printf("Test FAILED...\n");
	return 0;
}
