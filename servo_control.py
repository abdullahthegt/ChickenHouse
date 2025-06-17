import lgpio
from time import sleep

# === Setup ===
SERVO_PIN = 17  # GPIO17 (physical pin 11)

# Open GPIO chip (default chip 0 for Pi 5)
chip = lgpio.gpiochip_open(0)

# Configure pin as output
lgpio.gpio_claim_output(chip, SERVO_PIN)

# Set PWM to 50Hz (standard for SG90)
lgpio.tx_pwm(chip, SERVO_PIN, 50, 0)  # Initialize PWM at 50Hz, 0% duty cycle

# === Functions ===
def rotate_servo(angle):
    """
    Rotate SG90 servo to the given angle (0 to 180 degrees).
    """
    duty = 2 + (angle / 18)  # Map angle to duty cycle (2% to 12% for 0-180°)
    lgpio.tx_pwm(chip, SERVO_PIN, 50, duty)  # Set PWM duty cycle
    sleep(0.5)  # Allow servo to reach position

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
    lgpio.tx_pwm(chip, SERVO_PIN, 50, 0)  # Stop PWM signal
    lgpio.gpio_free(chip, SERVO_PIN)  # Release GPIO pin
    lgpio.gpiochip_close(chip)  # Close GPIO chip