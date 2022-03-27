#include <ESP8266WiFi.h>

#define ssid "ESP8266 - Heitor"
#define password "12345678"

#define user_wifi "BC Telecom anderson"
#define user_pass "m23m19v16v22h11h26"

WiFiServer server(80);

void print2(char msg[], String value) {
  Serial.print(msg);
  Serial.println(value);
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT); // Inicializa o LED_BUILTIN
  
  IPAddress staticIP(192, 168, 4, 2); // IP Static 192.168.4.2
  IPAddress gateway(192, 168, 4, 1);// gateway Static 192.168.4.1
  IPAddress subnet(255, 255, 255, 0);// subnet Static 255.255.255.0

  WiFi.mode(WIFI_AP_STA);// Modo Acess Point and 
  WiFi.softAP(ssid, password, 2, 0);
  WiFi.begin(user_wifi, user_pass);
  WiFi.config(staticIP, gateway, subnet);
  server.begin();

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nServer started!");
  print2("getway padrão: ", WiFi.softAPIP().toString());
  print2("local ip: ", WiFi.localIP().toString());
}

void get_connection(WiFiClient client) {
  // Wait until the client sends some data
  Serial.println("Esperando resposta.");
  String req = client.readStringUntil('\n');
  print2("Resposta: ", req);
  //req = req.substring(req.indexOf("/") + 1, req.indexOf("HTTP") - 1);

  client.print("EPS8266 recebeu sua informação.\n");
  client.flush();
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
