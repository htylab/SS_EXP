void setup()
{
  Serial.begin(115200); 
}

void loop()
{

  int val1 = analogRead(0);

  Serial.print(val1);
  Serial.print("\n"); 
  delay(10);
}
