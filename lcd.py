import time
import RPi.GPIO as GPIO
import warnings
GPIO.setwarnings(False)
# Define GPIO pins for LCD

LCD_RS = 11
LCD_E = 13
LCD_D4 = 15
LCD_D5 = 16
LCD_D6 = 18
LCD_D7 = 22

# LCD_RS = 24 LCD_E = 23 LCD_D4 = 17 LCD_D5 = 27 LCD_D6 = 22 LCD_D7 = 5

LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LCD_E, GPIO.OUT)
GPIO.setup(LCD_RS, GPIO.OUT)
GPIO.setup(LCD_D4, GPIO.OUT)
GPIO.setup(LCD_D5, GPIO.OUT)
GPIO.setup(LCD_D6, GPIO.OUT)
GPIO.setup(LCD_D7, GPIO.OUT)


def init():
    byte(0x33, False)  # 110011 Initialise
    byte(0x32, False)  # 110010 Initialise
    byte(0x06, False)  # 000110 Cursor move direction
    byte(0x0C, False)  # 001100 Display On, Cursor Off, Blink Off
    byte(0x28, False)  # 101000 Data length, number of lines, font size
    byte(0x01, False)  # 000001 Clear display
    time.sleep(0.0005)


def toggle_enable():
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)

def byte(bits, mode):
    GPIO.output(LCD_RS, mode)
    GPIO.output(LCD_D4, (bits & 0x10 == 0x10))
    GPIO.output(LCD_D5, (bits & 0x20 == 0x20))
    GPIO.output(LCD_D6, (bits & 0x40 == 0x40))
    GPIO.output(LCD_D7, (bits & 0x80 == 0x80))
    toggle_enable()
    GPIO.output(LCD_D4, (bits & 0x01 == 0x01))
    GPIO.output(LCD_D5, (bits & 0x02 == 0x02))
    GPIO.output(LCD_D6, (bits & 0x04 == 0x04))
    GPIO.output(LCD_D7, (bits & 0x08 == 0x08))
    toggle_enable()


def Print(message, line):
    message = message.ljust(16, " ")
    byte(line, False)
    for i in range(16):
        byte(ord(message[i]), True)    


def display(one,two):
    byte(0x01, False)
    init()
    Print(one, 0x80)
    Print(two, 0xC0)
    time.sleep(2)

if __name__ == "__main__":
    print("check")
    display("liquid Crystal","code check")
