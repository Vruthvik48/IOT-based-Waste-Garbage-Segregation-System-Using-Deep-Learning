import RPi.GPIO as GPIO
import time

# Define GPIO pin for servo
SERVO_PIN = 16

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set up PWM on the servo pin
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz frequency
pwm.start(0)

def rotate_servo(direction):
    if direction == "clockwise":
        pwm.ChangeDutyCycle(3.5)  # Adjust for continuous rotation clockwise
    elif direction == "counterclockwise":
        pwm.ChangeDutyCycle(10.5)  # Adjust for continuous rotation counterclockwise
    else:
        pwm.ChangeDutyCycle(0)  # Stop the servo

try:
    while True:
        rotate_servo("clockwise")
        time.sleep(0.8)  # Rotate clockwise for 2 seconds
        rotate_servo("counterclockwise")
        time.sleep(0.8)  # Rotate counterclockwise for 2 seconds
        rotate_servo("stop")
        time.sleep(2)  # Pause for a moment
except KeyboardInterrupt:
    print("\nExiting program...")
    pwm.stop()
    GPIO.cleanup()
