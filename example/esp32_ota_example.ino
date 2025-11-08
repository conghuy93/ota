/*
 * ESP32 OTA Update từ GitHub Raw Files
 * 
 * Cách sử dụng:
 * 1. Thay RAW_URL_VER và RAW_URL_FW bằng link repo của bạn
 * 2. Nạp code này vào ESP32 lần đầu (qua USB)
 * 3. Từ lần sau, ESP32 sẽ tự động OTA update
 * 
 * Workflow:
 * - Build firmware mới → Export compiled binary
 * - Upload firmware.bin lên GitHub
 * - Tăng version trong version.json
 * - ESP32 tự động detect và update
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Update.h>
#include <ArduinoJson.h>

// ============================================
// CẤU HÌNH WIFI
// ============================================
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// ============================================
// CẤU HÌNH GITHUB RAW URLs
// ============================================
// Thay USERNAME và REPO_NAME bằng repo của bạn
String RAW_URL_VER = "https://raw.githubusercontent.com/conghuy93/ota/main/ota/version.json";
String RAW_URL_FW  = "https://raw.githubusercontent.com/conghuy93/ota/main/ota/firmware/firmware.bin";

// ============================================
// CẤU HÌNH OTA
// ============================================
int CURRENT_VERSION = 1;  // Version hiện tại của firmware này
int CHECK_INTERVAL = 3600000;  // Kiểm tra mỗi 1 giờ (milliseconds)
bool AUTO_UPDATE = true;  // Tự động update khi có version mới

// ============================================
// BIẾN TOÀN CỤC
// ============================================
unsigned long lastCheck = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n========================================");
  Serial.println("ESP32 OTA Update System");
  Serial.println("========================================");
  Serial.printf("Current Version: %d\n", CURRENT_VERSION);
  Serial.printf("Check Interval: %d minutes\n", CHECK_INTERVAL / 60000);
  Serial.println("========================================\n");
  
  // Kết nối WiFi
  connectWiFi();
  
  // Kiểm tra update ngay khi khởi động
  checkAndUpdate();
  
  // Setup các chức năng khác của bạn ở đây
  setupYourApp();
}

void loop() {
  // Kiểm tra update định kỳ
  if (millis() - lastCheck > CHECK_INTERVAL) {
    lastCheck = millis();
    if (AUTO_UPDATE) {
      checkAndUpdate();
    }
  }
  
  // Code chính của ứng dụng của bạn
  loopYourApp();
  
  delay(1000);
}

// ============================================
// HÀM KẾT NỐI WIFI
// ============================================
void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ WiFi connection failed!");
  }
}

// ============================================
// HÀM KIỂM TRA VÀ CẬP NHẬT
// ============================================
void checkAndUpdate() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Skipping update check.");
    return;
  }
  
  Serial.println("\n[OTA] Checking for updates...");
  
  // Lấy version từ GitHub
  int onlineVersion = getOnlineVersion();
  
  if (onlineVersion == -1) {
    Serial.println("[OTA] ✗ Failed to get online version");
    return;
  }
  
  Serial.printf("[OTA] Current: %d, Online: %d\n", CURRENT_VERSION, onlineVersion);
  
  if (onlineVersion > CURRENT_VERSION) {
    Serial.println("[OTA] ✓ Update available!");
    Serial.println("[OTA] Downloading firmware...");
    
    if (downloadAndUpdateFirmware()) {
      Serial.println("[OTA] ✓ Update successful! Rebooting...");
      delay(2000);
      ESP.restart();
    } else {
      Serial.println("[OTA] ✗ Update failed!");
    }
  } else {
    Serial.println("[OTA] ✓ Already up to date");
  }
}

// ============================================
// HÀM LẤY VERSION TỪ GITHUB
// ============================================
int getOnlineVersion() {
  HTTPClient http;
  http.begin(RAW_URL_VER);
  http.setTimeout(10000);
  
  int httpCode = http.GET();
  
  if (httpCode != HTTP_CODE_OK) {
    Serial.printf("[OTA] HTTP error: %d\n", httpCode);
    http.end();
    return -1;
  }
  
  String payload = http.getString();
  http.end();
  
  // Parse JSON
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, payload);
  
  if (error) {
    Serial.printf("[OTA] JSON parse error: %s\n", error.c_str());
    return -1;
  }
  
  int version = doc["version"];
  return version;
}

// ============================================
// HÀM TẢI VÀ CẬP NHẬT FIRMWARE
// ============================================
bool downloadAndUpdateFirmware() {
  HTTPClient http;
  http.begin(RAW_URL_FW);
  http.setTimeout(30000);
  
  int httpCode = http.GET();
  
  if (httpCode != HTTP_CODE_OK) {
    Serial.printf("[OTA] HTTP error: %d\n", httpCode);
    http.end();
    return false;
  }
  
  int contentLength = http.getSize();
  Serial.printf("[OTA] Firmware size: %d bytes\n", contentLength);
  
  if (contentLength <= 0) {
    Serial.println("[OTA] Invalid content length");
    http.end();
    return false;
  }
  
  // Bắt đầu OTA update
  if (!Update.begin(contentLength)) {
    Serial.println("[OTA] Not enough space for update");
    http.end();
    return false;
  }
  
  // Tải và write firmware
  WiFiClient* stream = http.getStreamPtr();
  size_t written = Update.writeStream(*stream);
  
  if (written != contentLength) {
    Serial.printf("[OTA] Written: %d / %d\n", written, contentLength);
    Update.abort();
    http.end();
    return false;
  }
  
  if (!Update.end()) {
    Serial.println("[OTA] Update failed");
    Update.abort();
    http.end();
    return false;
  }
  
  if (!Update.isFinished()) {
    Serial.println("[OTA] Update not finished");
    Update.abort();
    http.end();
    return false;
  }
  
  http.end();
  Serial.println("[OTA] ✓ Firmware downloaded and verified");
  return true;
}

// ============================================
// HÀM CỦA ỨNG DỤNG CỦA BẠN
// ============================================
void setupYourApp() {
  // Setup code của bạn ở đây
  Serial.println("Setting up your application...");
  // Ví dụ:
  // pinMode(LED_BUILTIN, OUTPUT);
}

void loopYourApp() {
  // Main loop code của bạn ở đây
  // Ví dụ:
  // digitalWrite(LED_BUILTIN, HIGH);
  // delay(1000);
  // digitalWrite(LED_BUILTIN, LOW);
  // delay(1000);
}

