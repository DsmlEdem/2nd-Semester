#include <stdlib.h>
#include <stdio.h>
#include <string.h>

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

static void check(cudaError_t result, char const *const func, const char *const file, int const line) {
  if (result) {
    printf("CUDA error at %s: %d code = %d (%s) %s\n", file, line, static_cast<unsigned int>(result), cudaGetErrorName(result), func);
    exit(EXIT_FAILURE);
  }
}
#define checkCudaErrors(val) check((val), #val, __FILE__, __LINE__)

static void set_program_name(char *path) {
  if (!program_name)
    program_name = strdup(path);
  if (!program_name)
    fprintf(stderr, "strdup failed\n");
}

static void print_usage() {
  printf("Usage: %s <N>\n", program_name);
}

__global__ void vector_add(float *out, float *a, float *b, int n) {
  for (int i = 0; i < n; i++) {
    out[i] = a[i] + b[i];
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
  float *a, *b, *out; 

  // Allocate memory for vectors
  a   = (float*)malloc(sizeof(float) * N);
  b   = (float*)malloc(sizeof(float) * N);
  out = (float*)malloc(sizeof(float) * N);

  // Initialize vectors
  for (int i = 0; i < N; i++) {
    a[i] = 1.0f; b[i] = 2.0f;
  }

  double timer = csecond();

  dim3 block(1);
  dim3 grid(1);
  vector_add<<<grid, block>>>(out, a, b, N);
  checkCudaErrors(cudaPeekAtLastError());
  checkCudaErrors(cudaDeviceSynchronize());

  timer = csecond() - timer;
  printf("Addition completed in %lf seconds!\n", timer);
  
  // Cleanup
  free(a);
  free(b);
  free(out);

  return 0;
}
