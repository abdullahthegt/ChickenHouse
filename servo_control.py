import RPi.GPIO as GPIO
from time import sleep

# === Setup ===
SERVO_PIN = 17  # GPIO17 (physical pin 11)

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set PWM to 50Hz (standard for SG90)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# === Functions ===
def rotate_servo(angle):
    """
    Rotate SG90 servo to the given angle (0 to 180 degrees).
    """
    duty = 2 + (angle / 18)  # Map angle to duty cycle
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

# === Main Script ===
try:
    print("Rotating to 0° (Open)")
    rotate_servo(0)
    sleep(2)

    print("Rotating to 90° (Middle)")
    rotate_servo(90)
    sleep(2)

    print("Rotating to 180° (Closed)")
    rotate_servo(180)
    sleep(2)

except KeyboardInterrupt:
    print("Program stopped manually")

finally:
    pwm.stop()
    GPIO.cleanup()
