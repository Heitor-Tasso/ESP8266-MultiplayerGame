
#ifndef TOOLTYPE_FUNCS_H
#define TOOLTYPE_FUNCS_H
#include <Arduino.h>

#define LEN(array) ((sizeof(array))/(sizeof(array[0])))

void split_string(String str, String split_c, String strs[]);
void split_string_to_double(String str, String split_c, double nums[]);

#endif
