
#include <ESP8266WiFi.h>
#include "print.h"
#include "tooltype.h"

// esp8266 wifi config
#define ssid "ESP8266 - Heitor"
#define password "12345678"

// local wifi config
#define user_wifi "BC Telecom anderson"
#define user_pass "m23m19v16v22h11h26"

WiFiServer server(80);

#define num_players 5
#define num_lifes 5
#define player_width 70
#define player_height 150

String players[num_players] = {"-1", "-1", "-1", "-1", "-1"};
int players_life[num_players] = {0, 0, 0, 0, 0};
double players_pos[num_players][2] = {0, 0, 0, 0, 0};
int index_np = 0;

void start_local_wifi() {
  WiFi.begin(user_wifi, user_pass); // WiFi Domestico
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT); // Inicializa o LED_BUILTIN

  IPAddress staticIP(192, 168, 4, 2); // IP Static 192.168.4.2
  IPAddress gateway(192, 168, 4, 1);// gateway Static 192.168.4.1
  IPAddress subnet(255, 255, 255, 0);// subnet Static 255.255.255.0
  WiFi.mode(WIFI_AP_STA);// Modo ACESS POINT and 
  WiFi.softAP(ssid, password, 2, 0); // WiFi ESP8266
  WiFi.config(staticIP, gateway, subnet);
  server.begin();
  //start_local_wifi();
  Serial.println("");
  Serial.println("Server started!");
  print_str(WiFi.softAPIP().toString(), "getway");
  print_str(WiFi.localIP().toString(), "ip");
}

int new_player(String player_name, WiFiClient client) {
  /* add a new player and comunicate to start the game for him
   
   Args:
     player_name (String): name of player to add in **players**
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
  players[index_np] = player_name;
  players_life[index_np] = num_lifes;
  Serial.println(String("NEW PLAYER: ")+player_name);
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
  players[index_player] = "-1";
  players_life[index_player] = 0;
  if (index_player < index_np) {
    index_np = index_player;
  }
}

int collid_player(double pos[], double px, double py) {
  if (px < pos[0]+player_width && px >= pos[0] && py < pos[1]+player_height && py >= pos[1]) {
    return 1;
  }
  return 0;
}

void do_attack(int index_player, String atk, WiFiClient client) {
  String player = players[index_player];
  double px = players_pos[index_player][0];
  double py = players_pos[index_player][1];
  Serial.println(String("tipo do ataque: ")+atk);
  
  for (int i=0; i<num_players; i++) {
    if (index_player != i && !players[i].equals("-1")) {
      if (collid_player(players_pos[i], px, py) && players_life[i] > 0) {
        Serial.println(player+String(" colidiu com o ")+players[i]);
        players_life[i] --;
        Serial.println(String(players_life[i])+String(" é a nova vida do ")+players[i]);
      }
    }
  }
}

void get_connection(WiFiClient client) {
  // Wait until the client sends some data
  String req = client.readStringUntil('\n');
  String splited[3];
  split_string(req, ":", splited);
  // print_array_str(splited, "splited", LEN(splited), false);
  int index_player = splited[0].toInt();
  
  //if (!splited[0].equals("-1")) {
    //Serial.print("Ouvindo o ");
    //Serial.println(players[index_player]);
  //}
  
  if (splited[1].equals("recv")) {
    if (players_life[index_player] == 0) {
      print_client(String("over:zerolife:")+String(players_life[index_player]), client);
      players_life[index_player] = num_lifes;
    }
    else {
      print_client(String("life:")+String(players_life[index_player]), client); 
    }
  }
  else if (splited[1].equals("mov")) {
    double coords_move[3]; // [ x, y, angle_joystick ]
    split_string_to_double(splited[2], ",", coords_move);
    // print_array_double(coords_move, "coords_mov", LEN(coords_move));
    if (coords_move[0] > 0.4) {
      if (coords_move[1] > -0.4 && coords_move[1] < 0.4) {
        Serial.println("movendo para direita");
        players_pos[index_player][0] += 5;
      }
      else if (coords_move[1] > 0.4) {
        Serial.println("movendo para direita e cima");
      }
      else if (coords_move[1] < -0.4) {
        Serial.println("movendo para direita e baixo");
      }
    }
    else if (coords_move[0] < -0.4) {
      if (coords_move[1] > -0.4 && coords_move[1] < 0.4) {
        Serial.println("movendo para esquerda");
        players_pos[index_player][0] -= 5;
      }
      else if (coords_move[1] > 0.4) {
        Serial.println("movendo para esquerda e cima");
      }
      else if (coords_move[1] < -0.4) {
        Serial.println("movendo para esquerda e baixo");
      }
    }
    else if (coords_move[1] > 0.4) {
      if (coords_move[0] > -0.4 && coords_move[0] < 0.4) {
        Serial.println("movendo para cima");
        players_pos[index_player][1] += 5;
      }
    }
    else if (coords_move[1] < -0.4) {
      if (coords_move[0] > -0.4 && coords_move[0] < 0.4) {
        Serial.println("movendo para baixo");
        players_pos[index_player][1] -= 5;
      }
    }

    if (coords_move[2] == 0) {
      Serial.println("movendo para direita angle");
    }
    else if (coords_move[2] == 180) {
      Serial.println("movendo para esquerda angle");
    }
    else if (coords_move[2] == 90) {
      Serial.println("movendo para cima angle");
    }
    else if (coords_move[2] == 270) {
      Serial.println("movendo para baixo angle");
    }
    else if (coords_move[2] == 45) {
      Serial.println("movendo para direita e cima angle");
    }
    else if (coords_move[2] == 315) {
      Serial.println("movendo para direita e baixo angle");
    }
    else if (coords_move[2] == 135) {
      Serial.println("movendo para esquerda e cima angle");
    }
    else if (coords_move[2] == 225) {
      Serial.println("movendo para esquerda e baixo angle");
    }
  }
  else if (splited[1].equals("atk")) {
    do_attack(index_player, splited[2], client);
  }
  else if (splited[1].equals("np")) {
    // can't add this player
    if (!new_player(splited[2], client)){ return; }
    // successful added
    print_array_str(players, "players", LEN(players), false);
  }
  else if (splited[1].equals("exit")) {
    remove_player(splited[0].toInt());
    print_array_str(players, "players", LEN(players), false);
  }
  client.stop();
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);

  WiFiClient client = server.available();
  if (client) {
    get_connection(client);
  }
  digitalWrite(LED_BUILTIN, LOW);
}
