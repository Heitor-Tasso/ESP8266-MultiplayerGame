
#ifndef PRINT_FUNCS_H
#define PRINT_FUNCS_H
#include <Arduino.h>
#include <ESP8266WiFi.h>

void print_client(String msg, WiFiClient client);
void print_str(String msg, char name_var[]);
void print_array_str(String strs[], char name_var[], int size_array);
void print_double(double value, char name_var[]);
void print_array_double(double nums[], char name_var[], int size_array);

#endif
