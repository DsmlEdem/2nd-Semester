#include <stdio.h>

__device__ 
int get_global_id(){
  return blockDim.x*blockIdx.x + threadIdx.x;
}

__global__ void cuda_hello()
{
  int tid = get_global_id();
  printf("Hello World from thread %d!\n", tid);
}

#define BLOCK_DIM 1
#define GRID_DIM 64

int main() {

  dim3 block(BLOCK_DIM);
  dim3 grid(GRID_DIM);
  cuda_hello<<<grid, block>>>(); 
  cudaDeviceSynchronize();
    
  return 0;
}
