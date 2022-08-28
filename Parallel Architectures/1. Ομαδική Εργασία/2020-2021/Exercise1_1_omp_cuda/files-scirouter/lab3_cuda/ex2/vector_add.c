#include <stdlib.h>
#include <stdio.h>
#include <string.h>

char *program_name = NULL;

static void vector_add(float *out, float *a, float *b, int n) {
  for (int i = 0; i < n; i++) {
    out[i] = a[i] + b[i];
  }
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

  vector_add(out, a, b, N);
  printf("Addition completed!\n");
  
  // Cleanup
  free(a);
  free(b);
  free(out);

  return 0;
}
