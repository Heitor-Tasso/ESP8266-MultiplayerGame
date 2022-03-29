
#include "print.h"

void print_client(String msg, WiFiClient client) {
  client.print(msg+"\n");
  client.flush();
}

void print_str(String msg, char name_var[]) {
  Serial.print(name_var);
  Serial.println(" = '" + msg + "'");
}

void print_double(double value, char name_var[]) {
  Serial.print(name_var);
  Serial.print(" = ");
  Serial.println(value);
}

void print_array_str(String strs[], char name_var[], int size_array, bool ident) {
  int idx;
  int count = 0;
  
  Serial.print(name_var);
  Serial.print(" = [");
  for (idx=0; idx < size_array; idx++) {
    count++;
    if ((count == 5 || idx == 0) && ident) {
      count = 0;
      Serial.println("");
      Serial.print("    '");
    }
    Serial.print(strs[idx]);
    if (idx == size_array-1) {
      if (ident) {
        Serial.println("'");
      } else { Serial.print("'"); }
    } else {
      Serial.print(", '");
    }
  }
  Serial.println("]");
}

void print_array_double(double nums[], char name_var[], int size_array) {
  int idx;
  int count = 0;
  
  Serial.print(name_var);
  Serial.print(" = [");
  for (idx=0; idx < size_array; idx++) {
    count++;
    if (count == 5 || idx == 0) {
      count = 0;
      Serial.println("");
      Serial.print("    ");
    }
    Serial.print(nums[idx]);
    if (idx == size_array-1) {
      Serial.println("");
    } else {
      Serial.print(", ");
    }
  }
  Serial.println("]");
}
