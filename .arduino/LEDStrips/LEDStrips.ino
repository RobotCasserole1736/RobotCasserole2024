#include <FastLED.h>

//Constants related to hardware setup
#define NUM_LEDS   24
#define LED_PIN_LEFT     2
#define LED_PIN_RIGHT    3
#define CMD_INPUT_PIN    7

// Overall brigness control
#define BRIGHTNESS 100
// Desired FPS for the strip
#define FRAMES_PER_SECOND 120

const long pulseLengthGreenBlink = -350;  //pulse length in microseconds to command green blink
const long pulseLengthGreenSolid = 350; //pulse length in microseconds to command green solid
const long pulseLengthTolerance = 100; //command pulse length tolerance

//Buffer containing the desired color of each LED
CRGB led_left[NUM_LEDS];
CRGB led_right[NUM_LEDS - 1];
int pulseLen_us;

/**
 * One-time Init, at startup
 */
void setup()
{
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.addLeds<NEOPIXEL, LED_PIN_LEFT>(led_left, NUM_LEDS);
  FastLED.addLeds<NEOPIXEL, LED_PIN_RIGHT>(led_right, NUM_LEDS);

  //Set up a debug serial port
  Serial.begin(115200);

  //Configure the roboRIO communication pin to recieve data
  pinMode(CMD_INPUT_PIN, INPUT);

  FastLED.show(); //Ensure we get one LED update in prior to periodic - should blank out all LED's
}
/**
 * Periodic call. Will be called again and again.
 */
void loop()
{
  // do some periodic updates
  EVERY_N_MILLISECONDS(200)
  {
    pulseLen_us = pulseIn(CMD_INPUT_PIN, HIGH, 50000);
  }

  //Decode command PWM and display commanded image - default is team number + logo
  if(pulseLen_us <= (pulseLengthGreenBlink + pulseLengthTolerance) && pulseLen_us >= (pulseLengthGreenBlink - pulseLengthTolerance)){
    Green_Alert();
  } else if(pulseLen_us <= (pulseLengthGreenSolid + pulseLengthTolerance) && pulseLen_us >= (pulseLengthGreenSolid - pulseLengthTolerance)){
    Green_Solid();
  } else {
    CasseroleColorStripeChase_update();
  }

  // send the 'leds' array out to the actual LED strip
  FastLED.show();
  // insert a delay to keep the framerate modest
  FastLED.delay(1000 / FRAMES_PER_SECOND);
}

//**************************************************************
// Pattern: Casserole Color Stripes
//**************************************************************
#define STRIPE_WIDTH_PIXELS 5.0
#define STRIPE_SPEED_PIXELS_PER_LOOP 0.005
void CasseroleColorStripeChase_update()
{
  static double zeroPos = 0;
  zeroPos += STRIPE_SPEED_PIXELS_PER_LOOP;
  for (int i = 0; i < NUM_LEDS; i++)
  {

    //Create a "bumpy" waveform that shifts down the strip over time
    //Output range shoudl be [0,1]
    double pctDownStrip = (double)i / NUM_LEDS;
    double numCyclesOnStrip = (double)NUM_LEDS / (double)STRIPE_WIDTH_PIXELS / 2.0;
    double colorBump = sin(2 * PI * numCyclesOnStrip * (pctDownStrip - zeroPos)) * 0.5 + 0.5;

    //Square the value so that the edge is sharper.
    colorBump *= colorBump;

    //Scale to LED units
    colorBump *= 255;

    //Set the pixel color
    setPixel(i, 255,          //Red
             (int)colorBump,  //Green
             (int)colorBump); //Blue
  }
  for (int i = 0; i < NUM_LEDS; i++)
  {

    //Create a "bumpy" waveform that shifts down the strip over time
    //Output range shoudl be [0,1]
    double pctDownStrip = (double)i / NUM_LEDS;
    double numCyclesOnStrip = (double)NUM_LEDS / (double)STRIPE_WIDTH_PIXELS / 2.0;
    double colorBump = sin(2 * PI * numCyclesOnStrip * (pctDownStrip - zeroPos)) * 0.5 + 0.5;

    //Square the value so that the edge is sharper.
    colorBump *= colorBump;

    //Scale to LED units
    colorBump *= 255;

    //Set the pixel color
    setPixel(i, 255,          //Red
             (int)colorBump,  //Green
             (int)colorBump); //Blue
  }
}

//**************************************************************
// Pattern: Solid Color Sparkle
//**************************************************************
#define CYCLE_FREQ_LOOPS
void ColorSparkle_update(int red, int grn, int blu)
{
  for (int i = 0; i < NUM_LEDS; i++)
  {

    //Set all LED's to the input color, but
    //Randomly set an LED to white.
    if (random(0, NUM_LEDS) <= 0.15)
    {
      //shiny!
      setPixel(i, 255,    //Red
               (int)255,  //Green
               (int)255); //Blue
    }
    else
    {
      //Normal Color
      setPixel(i, red,    //Red
               (int)grn,  //Green
               (int)blu); //Blue
    }
  }
}

//**************************************************************
// Pattern:Green Alert
//**************************************************************
void Green_Alert(){
  static double g = 0;
  static int greenmode = 0;
  static boolean greenFade;
  
  if(g<=0){
    greenFade = true;
    greenmode++;
    if(greenmode == 2){
      greenmode = 0;
    }
    g = 0.1;
  }
  else if(254.0<=g){
    greenFade = false;
    g = 254.0;
  }
  
  if (greenFade==true){
    g+=40.0;
  }
  else if(greenFade==false){
    g-=40.0;
  }
    
  for (int i = 0; i < NUM_LEDS; i++){
    led_left[i] = CRGB(0,0,g);
    if(i < 23){
      led_right[i] = CRGB(0,0,g);
    }
  }
}

//**************************************************************
// Pattern:Green Solid
//**************************************************************
void Green_Solid(){
  for (int i = 0; i < NUM_LEDS; i++){
    led_left[i] = CRGB(0,0,255);
    if(i < 23){
      led_right[i] = CRGB(0,0,255);
    }    
  }
}

//**************************************************************
// Utilities
//**************************************************************
void setPixel(int Pixel, byte red, byte green, byte blue)
{
  // FastLED
  led_left[Pixel].r = red;
  led_left[Pixel].b = green;
  led_left[Pixel].g = blue; //our strips are rbg thbbbttt

  if(Pixel < 23){
    led_right[Pixel].r = red;
    led_right[Pixel].b = green;
    led_right[Pixel].g = blue; //our strips are rbg thbbbttt    
  }
}