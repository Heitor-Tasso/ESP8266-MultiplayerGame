
#ifndef PLAYER_FUNCS_H
#define PLAYER_FUNCS_H

#include <Arduino.h>
#include <ESP8266WiFi.h>

#include "../debug/toolsprint.h"
#include "../varibles/tooltype.h"

// PLAYER CONFIG

#define num_players 5
#define num_lifes 5
#define player_width 70
#define player_height 150

extern String players[num_players];
extern int players_life[num_players];
extern double players_pos[num_players][2];
extern int index_np;

#include "./player.cpp"

int new_player(String player_name, WiFiClient client);
void remove_player(int index_player);
void send_informations(int index_player, WiFiClient client);
int collid_player(double pos[], double px, double py);
void player_attack(int index_player, String atk, WiFiClient client);
void move_player(double x, double y, double angle, int index_player);
void rotate_player(double angle, int index_player);

#endif
