/* Random number sensor 
 *  
 *  Implements a dummy sensor that complies with the json-sensor requirements 
 *  
 *  Deniz Bozyigit 2018  
 *  
 */

void setup() {
  // put your setup code here,  
  
  Serial.begin(9600);           // set up Serial library at 9600 bps 
  Serial.println("{\"status\": \"starting\"");  // prints hello with ending line break 
}

long rand_number;

void loop() {
  // put your main code here, to run repeatedly:
  rand_number = random(1000);
  Serial.print("{\"value\": ");
  Serial.print(rand_number);
  Serial.println("}");
  delay(1000);      

}
