import tensorflow as tf
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import lcd

# Load trained model
model = tf.keras.models.load_model(
    "/home/pi/Desktop/tk187780/python/waste_classification_model.h5",
    compile=False
)

# Class labels
class_labels = ["carrot", "lemon", "metal_cans", "paper", "plastic_bottles", "tomato", "potato", "wood"]

# Categories
biodegradable = {"carrot", "lemon", "tomato", "potato"}
degradable = {"plastic_bottles", "metal_cans", "paper", "wood"}

# GPIO Pin Definitions
SERVO1_PIN = 36
SERVO2_PIN = 33
IR_PIN = 29
BUZZER_PIN = 31

# GPIO Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO1_PIN, GPIO.OUT)
GPIO.setup(SERVO2_PIN, GPIO.OUT)
GPIO.setup(IR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Servo setup
servo1 = GPIO.PWM(SERVO1_PIN, 50)  # 50Hz
servo2 = GPIO.PWM(SERVO2_PIN, 50)
servo1.start(0)
servo2.start(0)

# Start message
lcd.display("IOT Based", "Garbage Monitoring")
print("IOT Based Garbage Monitoring Started...")

def set_servo_angle(servo, angle):
    duty_cycle = (angle / 18) + 2
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.4)
    servo.ChangeDutyCycle(0)

def reset_servos():
    set_servo_angle(servo2, 0)
    set_servo_angle(servo1, 50)

def is_black(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    return brightness < 50

def capture_and_predict():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to grab frame!")
        return

    if is_black(frame):
        lcd.display("No Object", "Detected!")
        print("No object detected in camera frame.")
        reset_servos()
        return

    # Preprocess and Predict
    frame_resized = cv2.resize(frame, (224, 224))
    frame_normalized = frame_resized / 255.0
    frame_expanded = np.expand_dims(frame_normalized, axis=0)

    predictions = model.predict(frame_expanded, verbose=0)
    predicted_class = np.argmax(predictions, axis=1)[0]
    predicted_label = class_labels[predicted_class]

    # Decide category and operate servo
    if predicted_label in biodegradable:
        category = "Biodegradable"
        lcd.display("Waste Type:", "Biodegradable")
        print(f"Detected:({category})")
        set_servo_angle(servo1, 20)
        time.sleep(2)
        set_servo_angle(servo2, 40)
        time.sleep(2)
        reset_servos()
    elif predicted_label in degradable:
        category = "Degradable"
        lcd.display("Waste Type:", "non-biodegradable")
        print(f"Detected:({category})")
        set_servo_angle(servo1, 90)
        time.sleep(2)
        set_servo_angle(servo2, 40)
        time.sleep(2)
        reset_servos()
    else:
        category = "Unknown"
        lcd.display("Waste Type:", "Unknown")
        print(f"Detected: {predicted_label} (Unknown)")
        reset_servos()
    # Display prediction
    cv2.putText(frame, f"({category})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Waste Recognition', frame)

def monitor_ir_sensor():
    try:
        while True:
            if GPIO.input(IR_PIN) == GPIO.LOW:
                lcd.display("Object Detected!", "Scanning...")
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                print("IR Detected! Opening Camera...")
                time.sleep(0.5)
                GPIO.output(BUZZER_PIN, GPIO.LOW)

                # Capture and predict
                capture_and_predict()

            else:
                lcd.display("Waiting for", "Object Detection")
                print("Waiting for object detection...")
                time.sleep(0.5)

            

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        servo1.stop()
        servo2.stop()
        GPIO.cleanup()
        print("Cleaned up GPIO and exited.")

# Start monitoring
monitor_ir_sensor()
