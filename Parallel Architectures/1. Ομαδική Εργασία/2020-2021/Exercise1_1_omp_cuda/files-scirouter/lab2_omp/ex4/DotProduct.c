#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <omp.h>

#define N 100000000


int main () {
	double * x1, * x2, y_serial=0, y_parallel=0;
	double time; 
	struct timeval ts,tf;
	int i;

	/* Allocate space for vectors */
	x1 = (double *)malloc ( N * sizeof(double) );
	x2 = (double *)malloc ( N * sizeof(double) );

	
	/* Initialize values of x1 and x2 */
	for ( i = 0 ; i < N ; i++ ) {
		x1[i] = i*0.000032;
		x2[i] = i*0.000025;
	}

	/* Serial code for dot product - result in xR_serial */
	for ( i = 0 ; i < N ; i++ ) 
		y_serial+=x1[i]*x2[i];


	gettimeofday(&ts, NULL); //Start time measurement

	/* Parallel code for vector addition - result in xR_parallel */

	/* TODO: Parallelize this loop */
	/* TODO: Declare a parallel region */
	/* TODO: Parallelize the vector addition operation */
	#pragma omp parallel for reduction(+:y_parallel)
	for ( i = 0 ; i < N ; i++ )
		y_parallel+=x1[i]*x2[i];


	gettimeofday(&tf, NULL); //Stop time measurement


	/* Check and print results */
	if ( (y_serial - y_parallel)<0.00001 )
		printf ("Test PASSED! Time: %.5lf ms\n", (tf.tv_sec-ts.tv_sec)*1000+(tf.tv_usec-ts.tv_usec)*0.001);
	else
		printf("Test FAILED %lf %lf...\n", y_serial, y_parallel);
	return 0;
}
