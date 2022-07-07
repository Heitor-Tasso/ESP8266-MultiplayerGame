 
#include <ESP8266WiFi.h>

#include "debug/toolsprint.h"
#include "varibles/tooltype.h"
#include "player/player.h"

// WIFI CONFIG

WiFiServer server(80);

// ------------------ esp8266 wifi ------------------
#define ssid "ESP8266 - Heitor" // esp8266 wifi
#define password "SENHA"

// ------------------- local wifi -------------------
#define user_wifi "BC Telecom anderson"
#define user_pass "m23m19v16v22h11h26"

unsigned int time_to_update=0;
bool need_to_update=false;
unsigned long int last_time_updated=0;

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
  pinMode(LED_BUILTIN, OUTPUT);

  IPAddress staticIP(192, 168, 4, 2); // IP Static 192.168.4.2
  IPAddress gateway(192, 168, 4, 1);// gateway Static 192.168.4.1
  IPAddress subnet(255, 255, 255, 0);// subnet Static 255.255.255.0
  WiFi.mode(WIFI_AP_STA);// Mode ACCESS POINT && STATION ACCESS
  WiFi.softAP(ssid, password, 2, 0); // Start ACCESS POINT
  WiFi.config(staticIP, gateway, subnet);
  server.begin();
  
  //start_local_wifi(); // Start STATION ACCESS

  Serial.println("");
  Serial.println(".......................");
  Serial.println("Server started!");
  print_str(WiFi.softAPIP().toString(), "getway");
  print_str(WiFi.localIP().toString(), "ip");
  Serial.println(".......................");
}

void update_clients() {
  WiFiClient client;
  for (unsigned int i=0; i<num_players; i++) {
    if (players_port[i]) {
      if (client.connect(players_host[i], players_port[i])) {
        send_informations(i, client);
        try_connect_player[i] = 0;
        client.stop();
      }
      else {
        if (try_connect_player[i] == 5) {
          remove_player(i);
        }
      }
    }
  }
}

void get_connection(WiFiClient client) {
  String data[5] = {"", "", "", "", ""};
  // Wait until the client sends some data and split it
  split_string(client.readStringUntil('\n'), ":", data);
  
  int index_player = data[0].toInt();
  String instruction = data[1];
  
  if (instruction == "mov") {
    // cordinates of joystick to move and rotate player
    float coords[3]; // [ x, y, angle ]
    split_string_to_float(data[2], ",", coords);
    
    move_player(coords[0], coords[1], index_player);
    // rotate_player(coords[2], index_player);
  }
  else if (instruction == "atk") {
    player_attack(index_player, data[2], client);
  }
  else if (instruction == "np") {
    if (!new_player(data, client)){ return; }
    
    // successful added
    print_array_str(players, "players", LEN(players), false);
  }
  else if (instruction == "exit") {
    remove_player(index_player);
    print_array_str(players, "players", LEN(players), false);
  }
  client.stop();
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);

  WiFiClient client = server.available();
  if (client) {
    get_connection(client);
    need_to_update = true;
  }
  
  digitalWrite(LED_BUILTIN, LOW);
  if (millis()-last_time_updated >= time_to_update && need_to_update) {
    last_time_updated = millis();
    update_clients();
    need_to_update = false;
  }
}
