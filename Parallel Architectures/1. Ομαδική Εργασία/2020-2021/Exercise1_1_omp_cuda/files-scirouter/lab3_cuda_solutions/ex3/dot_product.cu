#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define EPS 1e-4

char *program_name = NULL;

double csecond(void) {
  struct timespec tms;

  if (clock_gettime(CLOCK_REALTIME, &tms)) {
    return (0.0);
  }
  /// seconds, multiplied with 1 million
  int64_t micros = tms.tv_sec * 1000000;
  /// Add full microseconds
  micros += tms.tv_nsec / 1000;
  /// round up if necessary
  if (tms.tv_nsec % 1000 >= 500) {
    ++micros;
  }
  return ((double)micros / 1000000.0);
}

static void set_program_name(char *path) {
  if (!program_name)
    program_name = strdup(path);
  if (!program_name)
    fprintf(stderr, "strdup failed\n");
}

static void print_usage() {
  printf("Usage: %s <N>\n", program_name);
}

static void check(cudaError_t result, char const *const func, const char *const file, int const line) {
  if (result) {
    printf("CUDA error at %s: %d code = %d (%s) %s\n", file, line, static_cast<unsigned int>(result), cudaGetErrorName(result), func);
    exit(EXIT_FAILURE);
  }
}
#define checkCudaErrors(val) check((val), #val, __FILE__, __LINE__)

__device__ 
int get_global_id(){
  return blockDim.x*blockIdx.x + threadIdx.x;
}

static void dot_product_cpu(float *out, float *a, float *b, int n) {
  for (int i = 0; i < n; i++) {
    *out += a[i] * b[i];
  }
}

/* TODO: optimize the GPU implementation */
__global__ void dot_product_gpu(float *out, float *a, float *b, int n) {
  for (int i = 0; i < n; i++) {
    *out += a[i] * b[i];
  }
}

int main(int argc, char **argv) {
  set_program_name(argv[0]);
  if (argc < 2) {
    printf("Error in number of arguments!\n");
    print_usage();
    exit(1);
  }

  int N = atoi(argv[1]);
  float *a, *b, out = 0.;
  float *dev_a, *dev_b, *dev_out;
	
  // Allocate memory on the CPU memory
  a = (float*)malloc(N * sizeof(float));
  b = (float*)malloc(N * sizeof(float));
	
  // Allocate memory on the GPU memory
  checkCudaErrors(cudaMalloc((void**)&dev_a, N*sizeof(float)));
  checkCudaErrors(cudaMalloc((void**)&dev_b, N*sizeof(float)));
  checkCudaErrors(cudaMalloc((void**)&dev_out, sizeof(float)));
	
  // Initialize vectors
  for (int i = 0; i < N; i++) {
    a[i] = i;
    b[i] = i*2;
  }

  // Copy the vectors to the GPU
  checkCudaErrors(cudaMemcpy(dev_a, a, N*sizeof(float), cudaMemcpyHostToDevice));
  checkCudaErrors(cudaMemcpy(dev_b, b, N*sizeof(float), cudaMemcpyHostToDevice));
  checkCudaErrors(cudaMemcpy(dev_out, &out, sizeof(float), cudaMemcpyHostToDevice));

  double timer = csecond();

  /* TODO: optimize the grid and block dimensions */
  dim3 grid(1);
  dim3 block(1);  
  dot_product_gpu<<<grid, block>>>(dev_out, dev_a, dev_b, N);
  checkCudaErrors(cudaPeekAtLastError());
  checkCudaErrors(cudaDeviceSynchronize());

  timer = csecond() - timer;
  printf("GPU Product completed in %lf seconds!\n", timer);

  // Copy the result back from the GPU to the CPU
  checkCudaErrors(cudaMemcpy(&out, dev_out, sizeof(float), cudaMemcpyDeviceToHost));


  // Check result
  float out_test = 0;

  timer = csecond();
  dot_product_cpu(&out_test, a, b, N);
  timer = csecond() - timer;
  printf("CPU Product completed in %lf seconds!\n", timer);

  if (fabs((float)(out - out_test) / (float)out) > EPS) {
    printf("Result differs: %lf vs %lf\n", out, out_test);
    printf("Test FAILED!\n");
  } else {
    printf("Test PASSED!\n");
  }
    
  // Free memory on the GPU side
  cudaFree(dev_a);
  cudaFree(dev_b);
  cudaFree(dev_out);
	
  // Free memory on the CPU side
  free(a);
  free(b);
}
