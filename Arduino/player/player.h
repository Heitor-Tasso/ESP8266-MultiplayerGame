
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
extern float players_pos[num_players][2];
extern String players_host[num_players];
extern int players_port[num_players];
extern int try_connect_player[num_players];
extern int index_np;

#include "./player.cpp"

int new_player(String data[], WiFiClient client);
void remove_player(int index_player);
void send_informations(int index_player, WiFiClient client);
int collid_player(float pos[], float px, float py);
void player_attack(int index_player, String atk, WiFiClient client);
void move_player(float x, float y, int index_player);
void rotate_player(float angle, int index_player);

#endif
