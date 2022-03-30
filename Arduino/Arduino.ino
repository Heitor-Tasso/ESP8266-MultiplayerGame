
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
String players[num_players] = {"-1", "-1", "-1", "-1", "-1"};
int index_np = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT); // Inicializa o LED_BUILTIN

  IPAddress staticIP(192, 168, 4, 2); // IP Static 192.168.4.2
  IPAddress gateway(192, 168, 4, 1);// gateway Static 192.168.4.1
  IPAddress subnet(255, 255, 255, 0);// subnet Static 255.255.255.0
  WiFi.mode(WIFI_AP_STA);// Modo ACESS POINT and 
  WiFi.softAP(ssid, password, 2, 0); // WiFi ESP8266
  WiFi.begin(user_wifi, user_pass); // WiFi Domestico
  WiFi.config(staticIP, gateway, subnet);
  server.begin();

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
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
  while (!players[index_np].equals(String("-1"))) {
    if (index_np == num_players-1) {
      // player can't be added
      print_client("ERRO:Quantidade máxima de players atingida!", client);
      client.stop();
      return 0;
    } else {
      index_np++;
    }
  }
  players[index_np] = player_name;
  Serial.println("NEW PLAYER: "+player_name);
  // to player know what him index
  print_client("index:"+String(index_np), client);
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
  if (index_player < index_np) {
    index_np = index_player;
  }
}

void get_connection(WiFiClient client) {
  // Wait until the client sends some data
  String req = client.readStringUntil('\n');
  String splited[3];
  split_string(req, ":", splited);
  print_array_str(splited, "splited", LEN(splited), false);
  
  if (!splited[0].equals("-1")) {
    int index_player = splited[0].toInt();
    Serial.print("Ouvindo o ");
    Serial.println(players[index_player]);
  }

  if (splited[1].equals(String("np"))) {
    // can't add this player
    if (!new_player(splited[2], client)){ return; }
    // successful added
    print_array_str(players, "players", LEN(players), false);
  }
  else if (splited[1].equals(String("exit"))) {
    remove_player(splited[0].toInt());
    print_array_str(players, "players", LEN(players), false);
  }
  else if (splited[1].equals(String("mov"))) {
    double coords_mov[3]; // x, y, angle [ JOYSTICK ]
    split_string_to_double(String(splited[2]), ",", coords_mov);
    print_array_double(coords_mov, "coords_mov", LEN(coords_mov));
  }
  else if (splited[1].equals(String("atk"))) {
    String atk = splited[2];
    print_str(atk, "atk");
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
