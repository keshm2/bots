#include <sparki.h>

const int k = 2000; // constant so I don't have to retype it over and over again

void setup() // initial setup function to get Saprki moving
{
  
  sparki.moveForward(15); // moves sparki forward 15 cm
  delay(k - 1000); // delays for 1 second
  sparki.moveStop(); // stops sparki from moving 
  delay(k - 1000);
  sparki.gripperOpen(); // opens sparki grippers for 4 seconds
  delay(k + 2000);
  sparki.gripperClose(); // closes sparki gripper for 2 seconds
  delay(k);
  sparki.moveBackward(15); // move sparki back 15 cm
  delay(k - 1000);
  sparki.moveStop();
  delay(k - 1000);
  sparki.moveLeft(90); // turn sparki right 90 degrees
  


}

void loop() // this code will always run after the setup function
{

  int a = sparki.ping(); // stored into variable a so I dont have to keep calling ping function
  while(a > 5) // the distance is greater than 5 cm
  {
    sparki.moveForward(); // keep sparki moving forward
    sparki.RGB(31, 156, 141); // indicate sparki is moving forward
    if(a < 5 or a == 5) // if the distance comes equal to or less than 5 cm, stop sparki
    {
      sparki.moveStop();
    }
  }
  
  sparki.moveStop(); 
  delay(k);
  sparki.servo(SERVO_RIGHT); // turn sparki head right  
  delay(k - 1500);
  int b = sparki.ping(); // variable b storage for ping function
  delay(k);
  sparki.servo(SERVO_LEFT); // turn sparki left
  delay(k - 1500);
  int c = sparki.ping(); // variable c storage for ping function
  delay(k);
  sparki.RGB(255,255,255); // random white rgb for fun
  sparki.servo(SERVO_CENTER); // center sparki head

  if(b > c) // if the distance to the right is greater than the left, turn right 90 degrees
  {
    sparki.moveRight(90);
    delay(k);
    sparki.moveForward();
  }
  else if(b < c) // otherwise turn left 90 degrees
  {
    sparki.moveLeft(90);
    delay(k);
    sparki.moveForward();
  }

  if(b < 10 and c < 10) // if both the distances are less than 10, it means spaki has reached its destination
  {
    sparki.moveForward(2);
    sparki.moveStop();
    delay(k - 1000);
    sparki.gripperOpen(); // drop the block 
    delay(k + 1000);
    sparki.gripperStop();
    delay(k);
    sparki.moveBackward();
    
  }
}