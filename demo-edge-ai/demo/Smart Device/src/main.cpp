// /**
//  * @file main.cpp
//  * @brief ESP32-S Hardware Demo Entry Point
//  * 
//  * Initializes the hardware demo and runs the main loop.
//  * Demonstrates TFT display capability and button input for hardware verification.
//  */

// // #include <Arduino.h>
// #include "demo.h"

// /**
//  * @brief Setup function - runs once at startup
//  */
// void setup() {
//   // Initialize serial for debugging
//   Serial.begin(115200);
//   delay(100);

//   Serial.println("\n\n================================");
//   Serial.println("AIoT Hardware Demo Starting...");
//   Serial.println("================================\n");

//   // Initialize the hardware demo
//   if (!demo_init()) {
//     Serial.println("ERROR: Demo initialization failed!");
//     while (1) {
//       delay(1000);
//     }
//   }

//   Serial.println("Demo initialized successfully!");
// }

// /**
//  * @brief Main loop function - runs repeatedly
//  */
// void loop() {
//   Serial.println("haha");
//   // Update demo (handles display rendering and button input)
//   if (demo_update()) {
//     // Demo running normally
//     Serial.flush();  // Ensure debug logs are sent
//     delay(50);  // 1 second between updates for stability
//   } else {
//     // Demo error - restart
//     Serial.println("ERROR: Demo update failed - restarting!");
//     Serial.flush();
//     demo_stop();
//     delay(50);
    
//     if (!demo_init()) {
//       Serial.println("ERROR: Demo restart failed!");
//       Serial.flush();
//       while (1) {
//         delay(50);
//       }
//     }
//   }
// }

#include <iostream>
#include "classifier.h"

#define FEATURE_COUNT 45
#define CLASS_COUNT 7




int main(){
  std::cout << "haha\n";

  const int16_t input_features[FEATURE_COUNT] = {
      0, 0, 1211, 745, 0, 0, 1797, 7, 1584, 1797, 3218, 2, 0,
        -306, 92, 8, 23, 7, -5, -11, -9, -3, -13, 0, -9, -6,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        21, 15, 18, 16, 18, 18, 14
  };

  const char *labels[CLASS_COUNT] = {
     "Angry",
      "Disgust",
      "Fear",
      "Happy",
      "Neutral",
      "Sad",
      "Surprise"
  };

  // Mẫu:
  // header generated with emlearn
    // #include "mymodel.h"

    // float probabilities[N_CLASSES];
    // mymodel_predict_proba(mymodel, features, features_length, probabilities, N_CLASSES)
  
  int32_t predicted_class = rf_predict(input_features, FEATURE_COUNT);
  float  probabilities[CLASS_COUNT];
  rf_predict_proba(input_features, FEATURE_COUNT, probabilities, CLASS_COUNT);

  std::cout << "Class index: " << predicted_class << '\n';
  std::cout << "Emotion label: " << labels[predicted_class] <<'\n';

  for  (int i = 0; i < CLASS_COUNT; i++)
  {
    std::cout << i << " " << labels[i] << " " << probabilities [i] << '\n';
  }

    
  return 0;
}