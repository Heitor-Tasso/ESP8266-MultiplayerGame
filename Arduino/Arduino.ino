
#include <ESP8266WiFi.h>
#include "print.h"
#include "tooltype.h"

#define ssid "ESP8266 - Heitor"
#define password "12345678"

#define user_wifi "BC Telecom anderson"
#define user_pass "m23m19v16v22h11h26"

WiFiServer server(80);

String players[5] = {"-1", "-1", "-1", "-1", "-1"};
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
  while (!players[index_np].equals(String("-1"))) {
    if (index_np == 4) {
      print_client("ERRO:Quantidade máxima de players atingida!", client);
      client.stop();
      return 0;
    } else {
      index_np++;
    }
  }
  players[index_np] = player_name;
  print_client("index:"+String(index_np), client);
  Serial.print("Novo Player -> ");
  Serial.println(player_name);
  return 1;
}

void remove_player(int index_player) {
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
    if (!new_player(splited[2], client)){
      return;
    }
    print_array_str(players, "players", LEN(players), false);
  }
  else if (splited[1].equals(String("exit"))) {
    remove_player(splited[0].toInt());
    print_array_str(players, "players", LEN(players), false);
  }
  else if (splited[1].equals(String("mov"))) {
    double coords_mov[2];
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
