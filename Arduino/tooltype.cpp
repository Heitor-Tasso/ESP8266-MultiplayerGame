
#include "tooltype.h"

void split_string(String str, String split_c, String strs[]) {
  int StringCount = 0;
  while (str.length() > 0) {
    int index = str.indexOf(split_c);
    if (index == -1) { // No space found 
      strs[StringCount++] = String(str);
      break;
    }
    else {
      strs[StringCount++] = str.substring(0, index);
      str = str.substring(index+1);
    }
  }
}

void split_string_to_double(String str, String split_c, double nums[]) {
  int StringCount = 0;
  while (str.length() > 0) {
    int index = str.indexOf(split_c);
    if (index == -1) { // No space found 
      nums[StringCount++] = str.toDouble();
      break;
    }
    else {
      nums[StringCount++] = str.substring(0, index).toDouble();
      str = str.substring(index+1);
    }
  }
}
