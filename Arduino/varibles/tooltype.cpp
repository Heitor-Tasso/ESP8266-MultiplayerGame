
#include "../varibles/tooltype.h"

void split_string(String str, String split_c, String strs[]) {
  /* to split string using any character and add in a new ``String`` array
   
   Args:
     str (String): string that will be splited
     split_c (String): character that will be used to split **str**
     strs (String[]): array to add all Strings that was splited
   Return:
     None
  */
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
  /* to split string using any character and add in a new ``double`` array
   
   Args:
     str (String): string that will be splited
     split_c (String): character that will be used to split **str**
     strs (String[]): array to add all double varibles that was splited
   Return:
     None
  */
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

void split_string_to_float(String str, String split_c, float nums[]) {
  /* to split string using any character and add in a new ``double`` array
   
   Args:
     str (String): string that will be splited
     split_c (String): character that will be used to split **str**
     strs (String[]): array to add all double varibles that was splited
   Return:
     None
  */
  int StringCount = 0;
  while (str.length() > 0) {
    int index = str.indexOf(split_c);
    if (index == -1) { // No space found 
      nums[StringCount++] = str.toFloat();
      break;
    }
    else {
      nums[StringCount++] = str.substring(0, index).toFloat();
      str = str.substring(index+1);
    }
  }
}
