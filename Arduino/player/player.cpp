
#include "../player/player.h"

// PLAYER CONFIG

String players[num_players] = {"-1", "-1", "-1", "-1", "-1"};
int players_life[num_players] = {0, 0, 0, 0, 0};
float players_pos[num_players][2] = {{0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}};
String players_host[num_players] = {"", "", "", "", ""};
int players_port[num_players] = {0, 0, 0, 0, 0};
int try_connect_player[num_players] = {0, 0, 0, 0, 0};
int index_np = 0;

#define distance_mov 10

int new_player(String data[], WiFiClient client) {
  /* add a new player and comunicate to start the game for him
   
   Args:
     data (Array String): in it has: 2-player_name, 3-player_host, 4-player_port
     client (WiFiClient): connection to communicate with player
   Return:
     false if no player added or true if added
  */
  while (!players[index_np].equals("-1")) {
    if (index_np == num_players-1) {
      // player can't be added
      print_client("erro:Quantidade máxima de players atingida!", client);
      client.stop();
      return 0;
    } else {
      index_np++;
    }
  }
  players[index_np] = data[2];
  players_life[index_np] = num_lifes;
  players_host[index_np] = data[3];
  players_port[index_np] = data[4].toInt();
  Serial.println(String("NEW PLAYER: ")+data[2]);
  Serial.println(String("HOST: ")+data[3]);
  Serial.println(String("PORT: ")+data[4]);
  // to player know what him index
  print_client(String("start:")+String(index_np)+String(":")+String(num_lifes), client);
  return 1;
}

void remove_player(int index_player) {
  /* remove player and comunicate to stop game for him
   
   Args:
     index_player (int): index of player to remove him of **players**
   Return:
     None
  */
  Serial.println(players[index_player]+String(" acabou de sair."));
  players[index_player] = "-1";
  players_life[index_player] = 0;
  players_port[index_player] = 0;
  players_host[index_player] = "";
  players_pos[index_player][0] = 0;
  players_pos[index_player][1] = 0;
  if (index_player < index_np) {
    index_np = index_player;
  }
}

void send_informations(int index_player, WiFiClient client) {
  String life_msg = String("life:")+String(players_life[index_player])+String(":");

  String pos_msg = String("pos:");
  for (int i=0; i < num_players; i++) {
    pos_msg += String(players_pos[i][0])+String(",")+String(players_pos[i][1])+String(":");
  }

  print_client(life_msg+pos_msg, client);

  if (players_life[index_player] == 0) {
    players_life[index_player] = num_lifes;
    Serial.print(players[index_player]);
    Serial.println(" morreu!!");
  }
}

int collid_player(float pos[], float px, float py) {
  if (px+player_width < pos[0] || px > (pos[0]+player_width)) {
    return 0;
  }
  else if (py+player_height < pos[1] || py > (pos[1]+player_height)) {
    return 0;
  }
  return 1;
}

void player_attack(int index_player, String atk, WiFiClient client) {
  String player = players[index_player];
  float px = players_pos[index_player][0];
  float py = players_pos[index_player][1];
  Serial.println(String("tipo do ataque: ")+atk);
  
  for (int i=0; i<num_players; i++) {
    if (index_player != i && !players[i].equals("-1")) {
      if (collid_player(players_pos[i], px, py) && players_life[i] > 0) {
        Serial.print(player+String(" colidiu com o ")+players[i]+String(", "));
        players_life[i] --;
        Serial.println(String(players_life[i])+String(" é a nova vida dele"));
      }
    }
  }
}

void move_player(float x, float y, int index_player) {
  Serial.print(players[index_player] + String(" "));
  if (x > 0.4) {
    Serial.print("movendo para direita");
    players_pos[index_player][0] += distance_mov;
  }
  else if (x < -0.4) {
    Serial.print("movendo para esquerda");
    players_pos[index_player][0] -= distance_mov;
  }

  if (y > 0.4) {
    Serial.print("movendo para cima");
    players_pos[index_player][1] += distance_mov;
  }
  else if (y < -0.4) {
    Serial.print("movendo para baixo");
    players_pos[index_player][1] -= distance_mov;
  }
  Serial.print(" na posição [");
  Serial.print(players_pos[index_player][0]);
  Serial.print(", ");
  Serial.print(players_pos[index_player][1]);
  Serial.println("]");
}

void rotate_player(float angle, int index_player) {
  Serial.print(players[index_player] + String(" no angulo "));
  Serial.print(angle);
  Serial.print(", ");
  if (angle == 0) {
    Serial.println("movendo para direita angle");
  }
  else if (angle == 180) {
    Serial.println("movendo para esquerda angle");
  }
  else if (angle == 90) {
    Serial.println("movendo para cima angle");
  }
  else if (angle == 270) {
    Serial.println("movendo para baixo angle");
  }
  else if (angle == 45) {
    Serial.println("movendo para direita e cima angle");
  }
  else if (angle == 315) {
    Serial.println("movendo para direita e baixo angle");
  }
  else if (angle == 135) {
    Serial.println("movendo para esquerda e cima angle");
  }
  else if (angle == 225) {
    Serial.println("movendo para esquerda e baixo angle");
  }
}
