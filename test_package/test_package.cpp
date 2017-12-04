#include <stdio.h>

#include "FLAC/all.h"

int main() {
  FLAC__format_sample_rate_is_subset(44100);
  printf("Test OK\n");
  return 0;
}
