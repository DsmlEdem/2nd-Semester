#include <stdio.h>

__device__
int get_global_id() {
	return blockDim.x*blockIdx.x + threadIdx.x;
}
  
__global__ void cuda_hello()
{
  /* TODO: find global thread id */
  int tid = get_global_id();
  printf("Hello World from thread %d!\n", tid);
}

#define BLOCK_DIM 1
#define GRID_DIM 64

int main() {
  /* TODO: define thread block and grid dimensions */
  dim3 block(BLOCK_DIM);
  dim3 grid(GRID_DIM);
  cuda_hello<<<grid, block>>>(); 

  # this call is for cpu to wait gpu excecution
  cudaDeviceSynchronize();
    
  return 0;
}
