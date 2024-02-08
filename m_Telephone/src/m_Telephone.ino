/*==========================================================================================================*/
/*		2CP - TeamEscape - Engineering
 *		by Abdullah Saei & Robert Schloezer
 *
 *		v1.0
 *		- Watchdog timer
 *		- Servo Motor working
 *		- 07.11.2019
 *    - No 1 sec release
 */
/*==========================================================================================================*/

const String title = String("Telephone v1.5");

/*==INCLUDE=================================================================================================*/
#include <Wire.h> /* TWI / I2C                                                          */
// Watchdog timer
#include <avr/wdt.h>
// I2C Port Expander
#include "PCF8574.h"
// LCD
#include "LiquidCrystal_I2C.h"
// Keypad
#include <Keypad.h>     /* Standardbibliothek                                                 */
#include <Keypad_I2C.h> /*                                                                    */
#include <Password.h>   /* http://www.arduino.cc/playground/uploads/Code/Password.zip
                                         Muss modifiziert werden:
                                         Password.h -> char guess[ MAX_PASSWORD_LENGTH ];
                                         und byte currentIndex; muessen PUBLIC sein                         */

// AUDIO
#include "AltSoftSerial.h"
//#include "NeoSWSerial.h"
#include "DFRobotDFPlayerMini.h"
// Servo
#include <Servo_I2C.h>  //
//#include <Servo.h> //pins connected to Attiny PIN D

/*==DEFINE==================================================================================================*/
// LED
// PIN
enum PWM_PIN {
    PWM_1_PIN = 3,  // Predefined by STB design
    PWM_2_PIN = 5,  // Predefined by STB design
    PWM_3_PIN = 6,  // Predefined by STB design
    PWM_4_PIN = 9,  // Predefined by STB design
    PWM_5_PIN = 12  // Servo
};

// SETTINGS
#define LED_STRIP WS2812B                                                              // Type of LED Strip, predefined by STB design
#define MAX_DIMENSION ((kMatrixWidth > kMatrixHeight) ? kMatrixWidth : kMatrixHeight)  // if w > h -> MAX_DIMENSION=kMatrixWidth, else MAX_DIMENSION=kMatrixHeight
#define NUM_LEDS (kMatrixWidth * kMatrixHeight)

// I2C ADRESSES
#define RELAY_I2C_ADD 0x3F  // Relay Expander
//#define OLED_I2C_ADD         0x3C         // Predefined by hardware
#define LCD_I2C_ADD 0x27     // 0x16         // Predefined by hardware
#define KEYPAD_I2C_ADD 0x38  // Telephone Keypad
#define INPUT_I2C_ADD 0x39   // coin detector and Phone speaker
#define SERVO_I2C_ADD 0x16   // 0x13         // From Attiny code

// RELAY
// PIN
enum REL_PIN {
    DOOR_LOCK_PIN,
    REL_2_PIN,
    REL_3_PIN,      // 2
    REL_4_PIN,      // 3
    REL_5_PIN,      // 4
    REL_6_PIN,      // 5
    BUZZER_12V_PIN,      // 0 Door Opener
    BUZZER_5V_PIN,     // 1 Buzzer
};

// AMOUNT
#define REL_AMOUNT 8
#define REL_MAX 8

// INIT
enum REL_INIT {
    DOOR_LOCK_INIT = 0,  // DESCRIPTION OF THE RELAY WIRING
    REL_2_INIT = 1,      // COM-12V_IN, NO-12V_OUT, NC-/
    REL_3_INIT = 1,      // DESCRIPTION OF THE RELAY WIRING
    REL_4_INIT = 1,      // DESCRIPTION OF THE RELAY WIRING
    REL_5_INIT = 1,      // DESCRIPTION OF THE RELAY WIRING
    REL_6_INIT = 1,      // DESCRIPTION OF THE RELAY WIRING
    // REL_7_INIT = 1,      // DESCRIPTION OF THE RELAY WIRING
    BUZZER_INIT = 1,     // COM-12V_IN, NO-12V_OUT_DOOR, NC-12V_OUT_ALARM
};

// INPUT
enum INPUT_PIN {
    PHONE_PICKUP_PIN,   //  0 Phone pickup button
    COIN_DETECTOR_PIN,  //  1 Coin Detector
    INPUT_3_PIN,        //  2
    INPUT_4_PIN,        //  3
    INPUT_5_PIN,        //  4
    INPUT_6_PIN,        //  5
    INPUT_7_PIN,        //  6
    INPUT_8_PIN
};
// AMOUNT
#define INPUT_AMOUNT 2

/*==CONSTANT VARIABLES======================================================================================*/
const enum REL_PIN relayPinArray[] = {DOOR_LOCK_PIN, REL_2_PIN, REL_3_PIN, REL_4_PIN, REL_5_PIN, REL_6_PIN, BUZZER_5V_PIN, BUZZER_12V_PIN};
const byte relayInitArray[] = {DOOR_LOCK_INIT, REL_2_INIT, REL_3_INIT, REL_4_INIT, REL_5_INIT, REL_6_INIT, BUZZER_INIT, BUZZER_INIT};
const enum INPUT_PIN inputPinArray[] = {PHONE_PICKUP_PIN, COIN_DETECTOR_PIN, INPUT_3_PIN, INPUT_4_PIN, INPUT_5_PIN, INPUT_6_PIN, INPUT_7_PIN};

/*==KEYPAD I2C==============================================================================================*/
const byte KEYPAD_ROWS = 4;
const byte KEYPAD_COLS = 3;
/* For Lab test */
// const byte KeypadRowPins[KEYPAD_ROWS] = {1, 6, 5, 3}; 	// Measure
// const byte KeypadColPins[KEYPAD_COLS] = {2, 0, 4};    	// Control wires (alternating HIGH)

/* For Telephone */
byte KeypadRowPins[KEYPAD_ROWS] = {3, 4, 5, 6};  // Measure
byte KeypadColPins[KEYPAD_COLS] = {0, 1, 2};     // Control wires (alternating HIGH)

char KeypadKeys[KEYPAD_ROWS][KEYPAD_COLS] = {
    {'1', '2', '3'},
    {'4', '5', '6'},
    {'7', '8', '9'},
    {'*', '0', '#'}};

bool KeypadTyping = false;
bool KeypadCodeCorrect = false;
bool KeypadCodeWrong = false;

const int KeypadWaitAfterCodeInput = 500;  // time for showing the entered code until it's checked

/*==Servo===================================================================================================*/
byte servo_correctstate = 1;  // zero is execluded
byte servo_defaultstate = 90;
byte servo_wrongstate = 179;

unsigned long coin_timerDelay = 0;
unsigned long coin_TimeOutCoinBack = 60000;

/*==VARIABLES===============================================================================================*/
bool CoinIn = false;  // coin inserted?
bool FirstCall = false;
bool EndGame = false;
/*==LCD=====================================================================================================*/
byte countMiddle = 6;
bool noTaxi = true;
bool UpdateLCD = true;

unsigned long UpdateLCDAfterDelayTimer = 0;
const unsigned long UpdateLCDAfterDelay = 5000; /* Refreshing the LCD periodically */

/*==CONSTRUCTOR=============================================================================================*/
// PCF8574
Expander_PCF8574 relay;
Expander_PCF8574 inputs;
// Keypad
Keypad_I2C MyKeypad(makeKeymap(KeypadKeys), KeypadRowPins, KeypadColPins, KEYPAD_ROWS, KEYPAD_COLS, KEYPAD_I2C_ADD, PCF8574);
// Password
char* taxi_number = (char*)"86753489";
Password pass_tele_num = Password(makeKeymap(taxi_number));
// LCD
LiquidCrystal_I2C lcd(LCD_I2C_ADD, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);
// Servo
Servo_I2C myservo;

unsigned long lastKeypadAction = millis();
unsigned long keypadTimeout = 5000;

// AUDIO
// NeoSWSerial altSerial( 8, 9 );
AltSoftSerial altSerial;
DFRobotDFPlayerMini myDFPlayer;
int tastenTon = 150;

/*============================================================================================================
//===SETUP====================================================================================================
//==========================================================================================================*/
void setup() {
    wdt_disable();
    Serial.begin(115200);
    Serial.println();
    Serial.println("==============Sweet Revange 12.08.2019=============");
    Serial.println();
    Serial.println("===================SETUP=====================");
    Serial.println();

    i2c_scanner();
    
    if (lcd_Init()) {
        Serial.println("LCD:     ok");
    }
    if (servo_Init()) {
        Serial.println("Servo:   ok");
    }
    if (relay_Init()) {
        Serial.println("Relay:   ok");
    }
    Serial.print(F("Inputs..."));
    if (input_Init()) {
        Serial.println("ok");
    }
    if (keypad_Init()) {
        Serial.println("Keypad: ok");
    }
    if (DFP_Init()) {
        Serial.println("DFP:   ok");
    }

    delay(100);
    i2c_scanner();
    delay(100);

    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);
    Serial.println();
    Serial.println("===================START=====================");
    Serial.println();
}

/*============================================================================================================
//===LOOP=====================================================================================================
//==========================================================================================================*/
void loop() {
    wdt_reset();
    while (inputs.digitalRead(PHONE_PICKUP_PIN)) {
        phone_start();
        while (1) {
            wdt_reset();
            Keypad_Update();
            if (millis() - lastKeypadAction > keypadTimeout) {
                checkPassword();
            }
            LCD_Update();
            if (!noTaxi && coinCheck() && !EndGame) {
                wdt_reset();
                relay.digitalWrite(DOOR_LOCK_PIN, !DOOR_LOCK_INIT);
                Serial.println("Everything correct, open door");
                relay.digitalWrite(BUZZER_5V_PIN, !BUZZER_INIT);
                relay.digitalWrite(BUZZER_12V_PIN, !BUZZER_INIT);
                delay(300);
                relay.digitalWrite(BUZZER_5V_PIN, BUZZER_INIT);
                relay.digitalWrite(BUZZER_12V_PIN, BUZZER_INIT);
                delay(150);
                relay.digitalWrite(BUZZER_5V_PIN, !BUZZER_INIT);
                relay.digitalWrite(BUZZER_12V_PIN, !BUZZER_INIT);
                delay(1000);
                relay.digitalWrite(BUZZER_5V_PIN, BUZZER_INIT);
                relay.digitalWrite(BUZZER_12V_PIN, BUZZER_INIT);
                EndGame = true;
            }
            if (!inputs.digitalRead(PHONE_PICKUP_PIN)) {
                break;
            }
        }
        phone_quit();
    }
}

/*============================================================================================================
//===FUNCTIONS================================================================================================
//==========================================================================================================*/

/*===Phone=================================================================================================*/
void phone_start() {
    FirstCall = true;
    Serial.println("Phone picked up");
    coin_timerDelay = millis();
    lcd.backlight();
    myDFPlayer.playMp3Folder(15);
}

void phone_quit() {
    Serial.println("Phone left down");
    myDFPlayer.pause();
    LCD_off();
    passwordReset();
    wdt_reset();
    // servo_coinBack();
}

void phone_correct() {
    noTaxi = false;
    FirstCall = false;
    LCD_correct();
    passwordReset();
    wdt_reset();
    playCorrectPasswort();
    wdt_reset();
    LCD_TaxiArrived();
    servo_coinBlock();
}

void phone_wrong() {
    LCD_wrong();
    playWrongPassword();
    software_Reset();
}
void phone_wrong_causeReset() {
    FirstCall = false;
    LCD_wrong();
    passwordReset();
    wdt_reset();
    playWrongPassword();
    // wdt_reset();
    servo_coinBack();
}

void phone_coinTimeOut() {
    LCD_TimeOut();
    DFP_soundAufgelegt();
    passwordReset();
    wdt_reset();
    servo_coinBack();
}

/*===Servo=================================================================================================*/

void servo_coinBlock() {
    myservo.write(servo_correctstate);
    delay(1000);
    myservo.write(servo_defaultstate);
    delay(20);
}

void servo_coinBack() {
    Serial.print("1");
    myservo.write(servo_wrongstate);
    Serial.print("2");
    delay(1000);
    Serial.print("3");
    myservo.write(servo_defaultstate);
    Serial.print("4");
    delay(20);
    Serial.print("5");
}

/*===AUDIO=================================================================================================*/

void DFP_soundAufgelegt() {
    myDFPlayer.playMp3Folder(13);
    delay(500);
    myDFPlayer.playMp3Folder(13);
    delay(500);
    myDFPlayer.playMp3Folder(13);
    delay(500);
    myDFPlayer.playMp3Folder(13);
    delay(500);
    myDFPlayer.playMp3Folder(13);
    delay(500);
}

void playButtonPressed(char eKey) {
    switch (eKey) {
        case '1':
            myDFPlayer.playMp3Folder(1);
            break;
        case '2':
            myDFPlayer.playMp3Folder(2);
            break;
        case '3':
            myDFPlayer.playMp3Folder(3);
            break;
        case '4':
            myDFPlayer.playMp3Folder(4);
            break;
        case '5':
            myDFPlayer.playMp3Folder(5);
            break;
        case '6':
            myDFPlayer.playMp3Folder(6);
            break;
        case '7':
            myDFPlayer.playMp3Folder(7);
            break;
        case '8':
            myDFPlayer.playMp3Folder(8);
            break;
        case '9':
            myDFPlayer.playMp3Folder(9);
            break;
        case '0':
            myDFPlayer.playMp3Folder(10);
            break;
    }
    delay(tastenTon);
}

void playCorrectPasswort() {
    Serial.println("Sound: BEGIN");
    myDFPlayer.playMp3Folder(11);
    delay(5000);
    wdt_reset();
    delay(5000);
    wdt_reset();
    delay(5000);
    wdt_reset();
    delay(5000);
    wdt_reset();
    delay(1200);  // 21200
    DFP_soundAufgelegt();
}

void playWrongPassword() {
    Serial.println("Falsches Passwort eingegeben");
    myDFPlayer.pause();
    delay(50);
    myDFPlayer.playMp3Folder(12);
    wdt_reset();
    delay(3300);
    myDFPlayer.playMp3Folder(13);
}

void DFP_printDetail(uint8_t type, int value) {
    switch (type) {
        case TimeOut:
            Serial.println(F("Time Out!"));
            break;
        case WrongStack:
            Serial.println(F("Stack Wrong!"));
            break;
        case DFPlayerCardInserted:
            Serial.println(F("Card Inserted!"));
            break;
        case DFPlayerCardRemoved:
            Serial.println(F("Card Removed!"));
            break;
        case DFPlayerCardOnline:
            Serial.println(F("Card Online!"));
            break;
        case DFPlayerPlayFinished:
            Serial.print(F("Number:"));
            Serial.print(value);
            Serial.println(F(" Play Finished!"));
            break;
        case DFPlayerError:
            Serial.print(F("DFPlayerError:"));
            switch (value) {
                case Busy:
                    Serial.println(F("Card not found"));
                    break;
                case Sleeping:
                    Serial.println(F("Sleeping"));
                    break;
                case SerialWrongStack:
                    Serial.println(F("Get Wrong Stack"));
                    break;
                case CheckSumNotMatch:
                    Serial.println(F("Check Sum Not Match"));
                    break;
                case FileIndexOut:
                    Serial.println(F("File Index Out of Bound"));
                    break;
                case FileMismatch:
                    Serial.println(F("Cannot Find File"));
                    break;
                case Advertise:
                    Serial.println(F("In Advertise"));
                    break;
                default:
                    break;
            }
            break;
        default:
            break;
    }
}

/*==Light Detector==========================================================================================*/
bool coinCheck() {
    if ((((millis() - coin_timerDelay) > coin_TimeOutCoinBack)) && noTaxi) {
        phone_coinTimeOut();
        Serial.println("TimeOut Coin Back");
        coin_timerDelay = millis();
    }
    // if coin inserted return 1 else
    return true;
}

/*==LCD=====================================================================================================*/
void LCD_Update() {
    static unsigned int counterLCD = 0;

    if ((((millis() - UpdateLCDAfterDelayTimer) > UpdateLCDAfterDelay)) && !KeypadTyping && noTaxi) {
        UpdateLCD = true;
        Serial.println("LCD refresh");
    }

    if (UpdateLCD && noTaxi) {
        LCD_homescreen();
        UpdateLCDAfterDelayTimer = millis();
        UpdateLCD = false;
        Serial.print("UpdateLCD ");
        Serial.println(counterLCD);

        if (KeypadTyping) {
            LCD_keypadscreen();
        } else {
            LCD_homescreen();
        }
        counterLCD++;
    } else if (UpdateLCD && EndGame) {
        UpdateLCDAfterDelayTimer = millis();
        UpdateLCD = false;
        Serial.print("NoUpdateLCD ");
        Serial.println(counterLCD);
        LCD_TaxiArrived();
        counterLCD++;
    }
}

void LCD_keypadscreen() {
    if (noTaxi) {
        for (uint16_t i = 0; i < strlen((pass_tele_num.guess)); i++) {
            lcd.setCursor(countMiddle + i, 0);
            lcd.print(pass_tele_num.guess[i]);
            if (i == 11) {
                break;
            }
        }
    }
}

void LCD_homescreen() {
    lcd.clear();
    lcd.home();
    lcd.setCursor(0, 0);
    lcd.print("Num: ");
}

void LCD_TaxiArrived() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Call Ended");
}

void LCD_TimeOut() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("TimeOut.. Try Again");
}

void LCD_correct() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Calling Taxi...");
}

void LCD_showCleared() {
    lcd.clear();
    lcd.print("CLEARED");
    LCD_homescreen();
}

void LCD_off() {
    lcd.clear();
    lcd.noBacklight();
    lcd.setCursor(0, 0);
    lcd.print("OFF..");
}

void LCD_wrong() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Calling Number...");
}

/*==KEYPAD==================================================================================================*/
void Keypad_Update() {
    if (KeypadCodeCorrect) {
        KeypadCodeCorrect = false;
    } else if (KeypadCodeWrong) {
        KeypadCodeWrong = false;
    }

    MyKeypad.getKey();

    if (strlen((pass_tele_num.guess)) == strlen(taxi_number) && noTaxi) {
        Serial.println("5 Zeichen eingebeben - ueberpruefe Passwort");
        checkPassword();
        Serial.println("Check password Done");
    }
}

void keypadEvent(KeypadEvent eKey) {
    Serial.println("Event Happened");
    lastKeypadAction = millis();
    coin_timerDelay = millis();
    switch (MyKeypad.getState()) {
        case PRESSED:
            Serial.print("Taste: ");
            Serial.print(eKey);
            Serial.print(" -> Code: ");
            Serial.print(pass_tele_num.guess);
            Serial.println(eKey);
            KeypadTyping = true;
            UpdateLCD = true;

            switch (eKey) {
                case '#':
                    Serial.println("Hash Not Used");
                    break;
                case '*':
                    Serial.println("cleared");
                    passwordReset();
                    if (noTaxi) {
                        LCD_showCleared();
                    }
                    break;
                default:
                    pass_tele_num.append(eKey);
                    playButtonPressed(eKey);
                    break;
            }
            break;

        case HOLD:
            Serial.print("HOLD: ");
            Serial.println(eKey);
            switch (eKey) {
                case '*':
                    software_Reset();
                    break;
                default:
                    break;
            }
            break;

        default:
            break;
    }
}

void checkPassword() {
    // Show last digit on LCD
    if (strlen(pass_tele_num.guess) == 0) {return;}
    UpdateLCD = true;
    LCD_Update();
    delay(500);
    if (pass_tele_num.evaluate()) {
        KeypadCodeCorrect = true;
        KeypadTyping = false;
        Serial.println("Taxi is called");
        phone_correct();
    } else {
        KeypadCodeWrong = true;
        KeypadTyping = false;
        Serial.println("Wrong number");
        phone_wrong();
    }
}

void passwordReset() {
    KeypadTyping = false;
    UpdateLCD = true;

    pass_tele_num.reset();
    Serial.println("Password reset");
}

/*============================================================================================================
//===INIT=====================================================================================================
//==========================================================================================================*/

/*==INPUTS==================================================================================================*/
bool input_Init() {
    inputs.begin(INPUT_I2C_ADD);
    for (int i = 0; i < INPUT_AMOUNT; i++) {
        inputs.pinMode(inputPinArray[i], INPUT);
    }
    return true;
}

/*===LCD====================================================================================================*/
bool lcd_Init() {
    lcd.begin(20, 4);  // 20*4 New LiquidCrystal
    lcd.setCursor(0, 0);
    lcd.print("Ending...");
    delay(500);
    /*	for (int i =0; i<0; i++){
                    delay(500);
                    lcd.noBacklight();
                    delay(500);
                    lcd.backlight();
            }
    */
    LCD_off();

    return true;
}

/*===Servo==================================================================================================*/
bool servo_Init() {
    myservo.begin(SERVO_I2C_ADD);
    delay(20);
    myservo.write(servo_defaultstate);
    delay(20);
    /*
    for (int pos = servo_correctstate; pos <= servo_wrongstate; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    if (pos == servo_defaultstate){
      delay(1000);
    }else  if (pos == servo_wrongstate){
      delay(1000);
    }else  if (pos == servo_correctstate){
      delay(1000);
    }
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  for (int pos = servo_wrongstate; pos >= servo_correctstate; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    if (pos == servo_defaultstate){
      delay(1000);
    }else  if (pos == servo_wrongstate){
      delay(1000);
    }else  if (pos == servo_correctstate){
      delay(1000);
    }
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  */
    myservo.write(servo_wrongstate);
    delay(1000);
    myservo.write(servo_defaultstate);
    delay(20);
    return true;
}

/*===KEYPAD=================================================================================================*/
bool keypad_Init() {
    MyKeypad.addEventListener(keypadEvent);  // Event Listener erstellen
    MyKeypad.begin(makeKeymap(KeypadKeys));
    MyKeypad.setHoldTime(5000);
    MyKeypad.setDebounceTime(20);

    return true;
}

/*===MOTHER=================================================================================================*/
bool relay_Init() {
    relay.begin(RELAY_I2C_ADD);
    for (int i = 0; i < REL_MAX; i++) {
        relay.pinMode(i, OUTPUT);
        relay.digitalWrite(i, HIGH);
    }

    // delay(1000);

    for (int i = 0; i < REL_AMOUNT; i++) {
        relay.digitalWrite(relayPinArray[i], relayInitArray[i]);
        Serial.print("     ");
        Serial.print("Relay [");
        Serial.print(relayPinArray[i]);
        Serial.print("] set to ");
        Serial.println(relayInitArray[i]);
        delay(1);
    }

    Serial.println();

    return true;
}

/*===AUDIO=================================================================================================*/
bool DFP_Init() {
    altSerial.begin(9600);
    Serial.println(F("Initializing DFPlayer ... (May take 3~5 seconds)"));

    if (!myDFPlayer.begin(altSerial)) {  // Use softwareSerial to communicate with mp3. mySoftwareSerial
        Serial.println(F("Unable to begin:"));
        Serial.println(F("1.Please recheck the connection!"));
        Serial.println(F("2.Please insert the SD card!"));
        wdt_enable(WDTO_8S);
        while (true) {
            if (myDFPlayer.begin(altSerial)) {
                wdt_reset();
                break;
            }
            delay(0);  // Code to compatible with ESP8266 watch dog.
        }
    }
    Serial.println(F("DFPlayer Mini online."));

    myDFPlayer.volume(15);  // Set volume value. From 0 to 30
    //  myDFPlayer.play(1);  //Play the first mp3
    return true;
}
/*============================================================================================================
//===BASICS===================================================================================================
//==========================================================================================================*/
void print_logo_infos(String progTitle) {
    Serial.println(F("+-----------------------------------+"));
    Serial.println(F("|    TeamEscape HH&S ENGINEERING    |"));
    Serial.println(F("+-----------------------------------+"));
    Serial.println();
    Serial.println(progTitle);
    Serial.println();
    delay(750);
}

void i2c_scanner() {
    Serial.println(F("I2C scanner:"));
    Serial.println(F("Scanning..."));
    byte wire_device_count = 0;

    for (byte i = 8; i < 120; i++) {
        Wire.beginTransmission(i);
        if (Wire.endTransmission() == 0) {
            Serial.print(F("Found address: "));
            Serial.print(i, DEC);
            Serial.print(F(" (0x"));
            Serial.print(i, HEX);
            Serial.print(F(")"));
            if (i == 39) Serial.print(F(" -> LCD"));
            if (i == 56) Serial.print(F(" -> LCD-I2C-Board"));
            if (i == 57) Serial.print(F(" -> Input-I2C-board"));
            if (i == 60) Serial.print(F(" -> Display"));
            if (i == 63) Serial.print(F(" -> Relay"));
            if (i == 22) Serial.print(F(" -> Servo-I2C-Board"));
            Serial.println();
            wire_device_count++;
            delay(1);
        }
    }
    Serial.print(F("Found "));
    Serial.print(wire_device_count, DEC);
    Serial.println(F(" device(s)."));

    Serial.println();

    delay(500);
}

void software_Reset() {
    Serial.println(F("Restarting in"));
    delay(250);
    for (byte i = 3; i > 0; i--) {
        Serial.println(i);
        delay(100);
    }
    asm volatile("  jmp 0");
}