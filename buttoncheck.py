import RPi.GPIO as GPIO
import time

# Define GPIO pins for the buttons  15-16-18-22
button_pin1 = 37
button_pin2 = 22
button_pin3 = 15
button_pin4 = 16

# Setup GPIO mode and pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_pin4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(button_pin1) == GPIO.LOW:
            print("Button 1 pressed")
            time.sleep(0.2)  # Add a small delay to avoid rapid multiple readings

        if GPIO.input(button_pin2) == GPIO.LOW:
            print("Button 2 pressed")
            time.sleep(0.2)

        if GPIO.input(button_pin3) == GPIO.LOW:
            print("Button 3 pressed")
            time.sleep(0.2)

        if GPIO.input(button_pin4) == GPIO.LOW:
            print("Button 4 pressed")
            time.sleep(0.2)

except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    GPIO.cleanup()
