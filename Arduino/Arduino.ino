
#include <ESP8266WiFi.h>
#include "print.h"
#include "tooltype.h"
#include "player.h"

// WIFI CONFIG

WiFiServer server(80);

// ------------------ esp8266 wifi ------------------
#define ssid "ESP8266 - Heitor" // esp8266 wifi
#define password "12345678"
// ------------------- local wifi -------------------
#define user_wifi "BC Telecom anderson"
#define user_pass "m23m19v16v22h11h26"

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

  IPAddress staticIP(192, 168, 4, 2); // IP Static 192.168.4.2
  IPAddress gateway(192, 168, 4, 1);// gateway Static 192.168.4.1
  IPAddress subnet(255, 255, 255, 0);// subnet Static 255.255.255.0
  WiFi.mode(WIFI_AP_STA);// Mode ACCESS POINT && STATION ACCESS
  WiFi.softAP(ssid, password, 2, 0); // Start ACCESS POINT
  WiFi.config(staticIP, gateway, subnet);
  server.begin();
  
  //start_local_wifi(); // Start STATION ACCESS
  Serial.println("");
  Serial.println("Server started!");
  print_str(WiFi.softAPIP().toString(), "getway");
  print_str(WiFi.localIP().toString(), "ip");
}

void get_connection(WiFiClient client) {
  // Wait until the client sends some data
  String req = client.readStringUntil('\n');
  String splited[3];
  split_string(req, ":", splited);
  // print_array_str(splited, "splited", LEN(splited), false);
  int index_player = splited[0].toInt();
  
  if (splited[1].equals("recv")) {
    send_life(index_player, client);
  }
  else if (splited[1].equals("mov")) {
    double coords_move[3]; // [ x, y, angle_joystick ]
    split_string_to_double(splited[2], ",", coords_move);
    double x = coords_move[0];
    double y = coords_move[1];
    double angle = coords_move[2];
    // print_array_double(coords_move, "coords_mov", LEN(coords_move));
    move_player(x, y, angle, index_player);
    rotate_player(angle, index_player);
  }
  else if (splited[1].equals("atk")) {
    player_attack(index_player, splited[2], client);
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
