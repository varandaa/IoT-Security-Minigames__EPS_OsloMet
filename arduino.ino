#include <Adafruit_NeoPixel.h>

/* -------------------------------------------------------------------------
   LED Strip Configuration
   ------------------------------------------------------------------------- */
const int LED_PIN = 7;
const int NUM_PIXELS = 60;
const int BRIGHTNESS = 50;
Adafruit_NeoPixel strip(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

/* -------------------------------------------------------------------------
   Block Definitions
   ------------------------------------------------------------------------- */
int blockStart[5] = {18, 24, 30, 37, 49};
int blockSize [5] = { 4,  2,  3,  6, 11};

/* -------------------------------------------------------------------------
   Special event pixels for '2' and 'A'
   ------------------------------------------------------------------------- */
int eventPixels[5] = {21, 24, 30, 37, 49};

/* -------------------------------------------------------------------------
   Animation state
   ------------------------------------------------------------------------- */
float posB[5]   = {0.0, 1.0, 0.5, 1.2, 2.1};
float speedB[5];
int   dirB[5]   = {1, -1, 1, -1, 1};
unsigned long lastUpdate = 0;
const unsigned long UPDATE_INTERVAL = 33;

/* -------------------------------------------------------------------------
   Persistent red flags
   ------------------------------------------------------------------------- */
bool persistentRed[5] = {false,false,false,false,false};

/* -------------------------------------------------------------------------
   Blinking control for G (global blink)
   ------------------------------------------------------------------------- */
bool blinkG = false;
unsigned long blinkG_start = 0;
const unsigned long BLINKG_DURATION = 2000UL;

bool blinkToggle = true;
unsigned long lastBlinkToggle = 0;
const unsigned long BLINK_INTERVAL = 400UL;

/* -------------------------------------------------------------------------
   State Variable
   ------------------------------------------------------------------------- */
char stateChar = '1';

/* ------------------------------------------------------------------------- */
inline void setGreen(int idx, int val){
  if(idx>=0 && idx<NUM_PIXELS) strip.setPixelColor(idx, strip.Color(0, val, 0));
}

inline void setRed(int idx, int val){
  if(idx>=0 && idx<NUM_PIXELS) strip.setPixelColor(idx, strip.Color(val, 0, 0));
}

void turnAllOff(){
  for(int i=0;i<NUM_PIXELS;i++) strip.setPixelColor(i, 0, 0, 0);
}

void animateBlock(int b) {
  int start = blockStart[b];
  int len   = blockSize[b];

  // Clear current block
  for (int i = 0; i < len; i++)
    strip.setPixelColor(start + i, 0, 0, 0);

  // Calculate current integer position
  int p1 = (int)posB[b];
  if (p1 < 0) p1 = 0;
  if (p1 >= len) p1 = len - 1;

  // Calculate second pixel (avoid overflow or duplication)
  int p2 = p1 + 1;
  if (p2 >= len) p2 = p1 - 1;
  if (p2 < 0) p2 = p1;

  // Light both pixels in green
  setGreen(start + p1, BRIGHTNESS);
  setGreen(start + p2, BRIGHTNESS);
}

// Blink a whole block for blocks 1 and 2
void blinkBlock(int b){
  int start = blockStart[b];
  int len   = blockSize[b];
  if(blinkToggle){
    for(int i=0;i<len;i++) setGreen(start + i, BRIGHTNESS);
  } else {
    for(int i=0;i<len;i++) strip.setPixelColor(start + i, 0,0,0);
  }
}

void renderPersistentReds(){
  for(int b=0;b<5;b++){
    if(persistentRed[b]){
      for(int i=0;i<blockSize[b];i++)
        setRed(blockStart[b] + i, BRIGHTNESS);
    }
  }
}

void renderState(){
  unsigned long now = millis();

  // --- Handle global blink G ---
  if(blinkG){
    if(now - blinkG_start >= BLINKG_DURATION){
      blinkG = false;
      for(int b=0;b<5;b++) persistentRed[b] = true;
    } else {
      if(now - lastBlinkToggle >= BLINK_INTERVAL){
        lastBlinkToggle = now;
        blinkToggle = !blinkToggle;
      }
      turnAllOff();
      if(blinkToggle){
        for(int b=0;b<5;b++)
          for(int i=0;i<blockSize[b];i++)
            setRed(blockStart[b] + i, BRIGHTNESS);
      }
      strip.show();
      return;
    }
  }

  // Update animation positions
  if(now - lastUpdate >= UPDATE_INTERVAL){
    lastUpdate = now;
    for(int b=0;b<5;b++){
      posB[b] += dirB[b] * speedB[b];
      if(posB[b] < 0.0f){ posB[b]=0.0f; dirB[b]*=-1; }
      if(posB[b] > (blockSize[b]-1)){ posB[b]=blockSize[b]-1; dirB[b]*=-1; }
    }
  }

  if(now - lastBlinkToggle >= BLINK_INTERVAL){
    lastBlinkToggle = now;
    blinkToggle = !blinkToggle;
  }

  turnAllOff();

  switch(stateChar){
    case '1': break;

    case '2':
      if (blinkToggle) {
        for (int i = 0; i < 5; i++) setGreen(eventPixels[i], BRIGHTNESS);
      }
      break;

    case 'A':
      if(blinkToggle){
        for(int i=0;i<5;i++) setRed(eventPixels[i], BRIGHTNESS);
      }
      break;

    case 'B':
      for(int b=0;b<5;b++){
        if(!persistentRed[b])
          for(int i=0;i<blockSize[b];i++)
            setGreen(blockStart[b] + i, BRIGHTNESS);
      }
      break;

    case '3': {
      int animBlock = 4;
      for(int b=0;b<5;b++){
        if(persistentRed[b]) continue;
        if(b==animBlock){
          (b==1 || b==2) ? blinkBlock(b) : animateBlock(b);
        } else {
          for(int i=0;i<blockSize[b];i++) setGreen(blockStart[b]+i, BRIGHTNESS);
        }
      }
    } break;

    case '4': {
      int animBlock = 1;
      for(int b=0;b<5;b++){
        if(persistentRed[b]) continue;
        if(b==animBlock){
          (b==1 || b==2) ? blinkBlock(b) : animateBlock(b);
        } else {
          for(int i=0;i<blockSize[b];i++) setGreen(blockStart[b]+i, BRIGHTNESS);
        }
      }
    } break;

    case '5': {
      int animBlock = 0;
      for(int b=0;b<5;b++){
        if(persistentRed[b]) continue;
        if(b==animBlock){
          (b==1 || b==2) ? blinkBlock(b) : animateBlock(b);
        } else {
          for(int i=0;i<blockSize[b];i++) setGreen(blockStart[b]+i, BRIGHTNESS);
        }
      }
    } break;

    case '6': {
      int animBlock = 2;
      for(int b=0;b<5;b++){
        if(persistentRed[b]) continue;
        if(b==animBlock){
          (b==1 || b==2) ? blinkBlock(b) : animateBlock(b);
        } else {
          for(int i=0;i<blockSize[b];i++) setGreen(blockStart[b]+i, BRIGHTNESS);
        }
      }
    } break;

    case '7': {
      int animBlock = 3;
      for(int b=0;b<5;b++){
        if(persistentRed[b]) continue;
        if(b==animBlock){
          (b==1 || b==2) ? blinkBlock(b) : animateBlock(b);
        } else {
          for(int i=0;i<blockSize[b];i++) setGreen(blockStart[b]+i, BRIGHTNESS);
        }
      }
    } break;
  }

  renderPersistentReds();
  strip.show();
}

void setup(){
  Serial.begin(9600);
  strip.begin();
  strip.setBrightness(BRIGHTNESS);
  strip.show();

  // speed proportional to block length
  float baseSpeed = 0.03;
  for(int b=0;b<5;b++){
    speedB[b] = baseSpeed * blockSize[b];
  }

  stateChar = '1';
}

void loop(){
  if(Serial.available()){
    char c = Serial.read();
    switch(c){
      case 'R':
        stateChar = '1';
        for(int b=0;b<5;b++) persistentRed[b]=false;
        blinkG=false;
        break;

      case '1': case '2': case 'A': case 'B':
      case '3': case '4': case '5': case '6': case '7':
        stateChar = c;
        break;

      case 'C': persistentRed[4]=true; stateChar='3'; break;
      case 'D': persistentRed[1]=true; stateChar='4'; break;
      case 'E': persistentRed[0]=true; stateChar='5'; break;
      case 'F': persistentRed[2]=true; stateChar='6'; break;
      case 'G':
        blinkG=true;
        blinkG_start=millis();
        stateChar='G';
        break;
    }
  }

  renderState();