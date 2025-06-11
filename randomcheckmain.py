import tensorflow as tf
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import lcd

# Load trained model (compile=False to avoid unnecessary warning)
model = tf.keras.models.load_model("/home/pi/Desktop/tk187780/python/waste_classification_model.h5",
    compile=False
)

# Define class labels
class_labels = ["carrot", "lemon", "metal_cans", "paper", "plastic_bottles", "tomato", "potato", "wood"]

# Define categories
biodegradable = {"carrot", "lemon", "tomato", "potato"}
degradable = {"plastic_bottles", "metal_cans", "paper", "wood"}

# GPIO Pin Definitions
SERVO1_PIN = 36
SERVO2_PIN = 33
IR_PIN = 29
BUZZER_PIN = 31
BUTTON_PIN = 37  # <-- Add your button GPIO pin here

# GPIO Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO1_PIN, GPIO.OUT)
GPIO.setup(SERVO2_PIN, GPIO.OUT)
GPIO.setup(IR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Assuming button connected to GND

# Servo setup
servo1 = GPIO.PWM(SERVO1_PIN, 50)  # 50Hz PWM frequency
servo2 = GPIO.PWM(SERVO2_PIN, 50)
servo1.start(0)
servo2.start(0)

# Display start message
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

def predict_from_webcam():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    
    try:
        while True:
            time.sleep(1)
            if GPIO.input(IR_PIN) == GPIO.LOW:  # Object detected by IR
                button_pressed = GPIO.input(BUTTON_PIN) == GPIO.LOW  # Button pressed (active low)
                
                if button_pressed:
                    # Directly handle as non-biodegradable (button override)
                    lcd.display("detected", "Non-Biodegradable")
                    GPIO.output(BUZZER_PIN, GPIO.HIGH)
                    print("sorting as non-biodegradable")
                    time.sleep(0.5)
                    GPIO.output(BUZZER_PIN, GPIO.LOW)
                    
                    set_servo_angle(servo1, 90)
                    time.sleep(2)
                    set_servo_angle(servo2, 40)
                    time.sleep(2)
                    reset_servos()
                    continue  # Skip camera prediction
                
                # Button NOT pressed: use camera & model prediction
                lcd.display("Object Detected!", "Scanning...")
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                print("IR Detected! Opening Camera...")
                time.sleep(0.5)
                GPIO.output(BUZZER_PIN, GPIO.LOW)
                
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame!")
                    break
                
                if is_black(frame):
                    lcd.display("No Object", "Detected!")
                    cv2.putText(frame, "Nothing Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow('Waste Recognition', frame)
                    reset_servos()
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue
                
                # Preprocess frame
                frame_resized = cv2.resize(frame, (224, 224))
                frame_normalized = frame_resized / 255.0
                frame_expanded = np.expand_dims(frame_normalized, axis=0)
                
                # Prediction
                predictions = model.predict(frame_expanded, verbose=0)
                predicted_class = np.argmax(predictions, axis=1)[0]
                predicted_label = class_labels[predicted_class]
                
                # Decide category and operate servo
                if predicted_label in biodegradable:
                    lcd.display("Waste Type:", "Biodegradable")
                    print(f"Detected biodegradable waste")
                    set_servo_angle(servo1, 20)
                    time.sleep(2)
                    set_servo_angle(servo2, 40)
                    time.sleep(2)
                    reset_servos()
                elif predicted_label in degradable:
                    lcd.display("Waste Type:", "Non-Biodegradable")
                    print(f"Detected non-biodegradable waste")
                    set_servo_angle(servo1, 90)
                    time.sleep(2)
                    set_servo_angle(servo2, 40)
                    time.sleep(2)
                    reset_servos()
                else:
                    lcd.display("Waste Type:", "Unknown")
                    print(f"Detected unknown waste")
                    reset_servos()
                
                # Display prediction on frame
                cv2.putText(frame, f"Detected", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Waste Recognition', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            else:
                # No object detected
                lcd.display("Waiting for", "Object Detection")
                print("Waiting for object detection...")
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("Interrupted by user.")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        servo1.stop()
        servo2.stop()
        GPIO.cleanup()
        print("Cleaned up GPIO and exited.")

# Run the main function
predict_from_webcam()
