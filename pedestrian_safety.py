import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD

# GPIO 초기화
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# 핀 설정
TRIG = 21
ECHO = 20
SERVO_PIN = 18

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 서보모터 설정
servo = GPIO.PWM(SERVO_PIN, 50) # 50Hz 주파수
servo.start(0) # 초기화

# LCD 초기화
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)

# 거리 측정 함수
def distance():
    GPIO.output(TRIG, False)
    time.sleep(2)
    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    start_time = time.time()
    stop_time = time.time()
    
    timeout = start_time + 0.5
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start_time = time.time()
        
    if time.time() >= timeout:
        return None
        
    timeout = start_time + 0.5
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        stop_time = time.time()
        
    if time.time() >= timeout:
        return None
        
    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2
    
    return distance

# 서보모터 각도 설정 함수
def set_servo_angle(angle):
    duty = (angle / 18) + 2
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

# 메인 루프
try:
    while True:
        dist = distance()
        if dist is not None:
            print(f"Measured Distance = {dist:.1f} cm")
            lcd.clear()
            lcd.write_string(f"Distance: {dist:.1f}cm")
            
            # 거리 값에 따라 서보모터 제어
            if dist < 14:
                set_servo_angle(180) # 서보모터를 180도 회전 (차단기 다운)
            else:
                set_servo_angle(90)  # 서보모터를 90도 회전 (차단기 업)
        else:
            print("Distance measurement timed out")
            lcd.clear()
            lcd.write_string("No Measurement")
            
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by User")
    servo.stop()
    GPIO.cleanup()