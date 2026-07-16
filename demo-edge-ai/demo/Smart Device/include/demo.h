// /**
//  * @file demo.h
//  * @brief Hardware capability demo interface
//  * 
//  * Main entry point for the hardware demo application.
//  * Provides high-level initialization and control functions.
//  */

// #ifndef DEMO_H
// #define DEMO_H

// /**
//  * @brief Initialize the hardware demo
//  * 
//  * Sets up display, buttons, and state machine.
//  * Call this once at startup from main.cpp.
//  * 
//  * @return true if initialization successful, false if any component failed
//  */
// bool demo_init();

// /**
//  * @brief Run one iteration of the demo loop
//  * 
//  * Updates button states, checks for navigation input, renders current screen.
//  * Call this in your main loop repeatedly.
//  * 
//  * @return true if demo is running normally, false if an error occurred
//  */
// bool demo_update();

// /**
//  * @brief Check if demo is running
//  * 
//  * @return true if demo initialized and running
//  */
// bool demo_is_running();

// /**
//  * @brief Stop the demo and clean up resources
//  */
// void demo_stop();

// #endif // DEMO_H