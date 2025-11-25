// runtime.c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

void print_int(int32_t x) {
    printf("%d", x);
}

void print_char(int8_t c) {
    putchar((unsigned char)c);
}

void print_bool(_Bool b) {
    printf(b ? "true" : "false");
}

void print_float(float f) {
    printf("%f", f);
}
