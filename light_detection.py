import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
try:
    import lgpio
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False

DEFAULT_IMAGE_PATH = "./images/day1.jpg"

def load_image(image_path):
    """Load an image using OpenCV"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def analyze_brightness(img):
    """Calculate average brightness of the image"""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return np.mean(gray)

def analyze_color_temperature(img):
    """Analyze color temperature - warmer colors suggest morning/sunset"""
    b, g, r = cv2.split(img)
    
    # Calculate color ratios
    red_ratio = np.mean(r) / (np.mean(b) + np.mean(g) + np.mean(r))
    blue_ratio = np.mean(b) / (np.mean(b) + np.mean(g) + np.mean(r))
    
    return red_ratio, blue_ratio

def detect_time_of_day(image_path=None, brightness_threshold=80):
    """
    Detect if image shows morning or night scene
    
    Args:
        image_path: Path to the image file
        brightness_threshold: Threshold for brightness (0-255)
    
    Returns:
        tuple: (prediction, confidence, metrics)
    """
    
    if image_path is None:
        image_path = DEFAULT_IMAGE_PATH
    
    # Load image
    img = load_image(image_path)
    if img is None:
        return None, 0, {}
    
    # Analyze brightness
    avg_brightness = analyze_brightness(img)
    
    # Analyze color temperature
    red_ratio, blue_ratio = analyze_color_temperature(img)
    
    # Calculate metrics
    metrics = {
        'brightness': avg_brightness,
        'red_ratio': red_ratio,
        'blue_ratio': blue_ratio,
        'brightness_threshold': brightness_threshold
    }
    
    # Decision logic
    if avg_brightness < brightness_threshold:
        prediction = "Night"
        confidence = min((brightness_threshold - avg_brightness) / brightness_threshold, 1.0)
    else:
        # For brighter images, consider color temperature
        if red_ratio > blue_ratio * 1.2:  # Warmer colors
            prediction = "Morning/Golden Hour"
            confidence = 0.7 + (red_ratio - blue_ratio) * 0.3
        else:
            prediction = "Day/Morning"
            confidence = 0.6 + (avg_brightness - brightness_threshold) / 255 * 0.4
    
    confidence = min(confidence, 1.0)  # Cap at 1.0
    
    return prediction, confidence, metrics

def visualize_analysis(image_path=None):
    """Create visualization of the analysis"""
    if image_path is None:
        image_path = DEFAULT_IMAGE_PATH
    
    img = load_image(image_path)
    if img is None:
        return
    
    prediction, confidence, metrics = detect_time_of_day(image_path)
    
    # Create subplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Display original image
    ax1.imshow(img)
    ax1.set_title('Original Image')
    ax1.axis('off')
    
    # Display histogram
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ax2.hist(gray.flatten(), 256, [0, 256], alpha=0.7, color='blue')
    ax2.axvline(metrics['brightness'], color='red', linestyle='--', 
                label=f'Avg Brightness: {metrics["brightness"]:.1f}')
    ax2.axvline(metrics['brightness_threshold'], color='orange', linestyle='--', 
                label=f'Threshold: {metrics["brightness_threshold"]}')
    ax2.set_xlabel('Pixel Intensity')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Brightness Distribution')
    ax2.legend()
    
    # Add prediction text
    plt.suptitle(f'Prediction: {prediction} (Confidence: {confidence:.2f})', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def get_light_plot(image_path=None):
    """Return a matplotlib Figure for the current image analysis."""
    if image_path is None:
        image_path = DEFAULT_IMAGE_PATH
    
    img = load_image(image_path)
    if img is None:
        fig = plt.figure()
        plt.text(0.5, 0.5, 'Image not found', ha='center', va='center')
        return fig
    prediction, confidence, metrics = detect_time_of_day(image_path)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    ax1.imshow(img)
    ax1.set_title('Original Image')
    ax1.axis('off')
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ax2.hist(gray.flatten(), 256, [0, 256], alpha=0.7, color='blue')
    ax2.axvline(metrics['brightness'], color='red', linestyle='--', 
                label=f'Avg Brightness: {metrics["brightness"]:.1f}')
    ax2.axvline(metrics['brightness_threshold'], color='orange', linestyle='--', 
                label=f'Threshold: {metrics["brightness_threshold"]}')
    ax2.set_xlabel('Pixel Intensity')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Brightness Distribution')
    ax2.legend()
    fig.suptitle(f'Prediction: {prediction} (Confidence: {confidence:.2f})', fontsize=12, fontweight='bold')
    fig.tight_layout()
    return fig

# Simple stubs for door status and control
_door_status = 'Closed'

def get_door_status():
    global _door_status
    return _door_status

SERVO_PIN = 17  # GPIO17
_chip = None
_servo_initialized = False

SERVO_OPEN_DUTY = 2   # Open (2% duty cycle, ~1ms pulse)
SERVO_CLOSED_DUTY = 8  # Closed (8% duty cycle, ~2ms pulse)

def _init_servo():
    global _servo_initialized, _chip
    if not RPI_AVAILABLE or _servo_initialized:
        return
    _chip = lgpio.gpiochip_open(0)  # Open GPIO chip 0 (default for Pi 5)
    lgpio.gpio_claim_output(_chip, SERVO_PIN)  # Configure pin as output
    lgpio.tx_pwm(_chip, SERVO_PIN, 50, SERVO_CLOSED_DUTY)  # Initialize PWM at 50Hz, closed position
    _servo_initialized = True

def _set_servo(duty):
    if not RPI_AVAILABLE:
        print(f"[Mock] Set servo to duty {duty}")
        return
    _init_servo()
    if _chip is not None:
        lgpio.tx_pwm(_chip, SERVO_PIN, 50, duty)  # Set PWM duty cycle

def open_door():
    global _door_status
    _door_status = 'Open'
    print('Door status: OPEN (motor should be opening)')
    _set_servo(SERVO_OPEN_DUTY)

def close_door():
    global _door_status
    _door_status = 'Closed'
    print('Door status: CLOSED (motor should be closing)')
    _set_servo(SERVO_CLOSED_DUTY)

def cleanup_servo():
    global _servo_initialized, _pwm
    if RPI_AVAILABLE:
        try:
            if _pwm:
                _pwm.stop()
            GPIO.cleanup()
        except Exception as e:
            print(f"GPIO cleanup error: {e}")
    _servo_initialized = False
    _pwm = None

# Example usage
if __name__ == "__main__":
    image_path = DEFAULT_IMAGE_PATH
    try:
        prediction, confidence, metrics = detect_time_of_day(image_path)
        
        print("=" * 50)
        print("MORNING vs NIGHT DETECTION RESULTS")
        print("=" * 50)
        print(f"Image: {image_path}")
        print(f"Prediction: {prediction}")
        print(f"Confidence: {confidence:.2f}")
        print("\nMetrics:")
        print(f"  Average Brightness: {metrics['brightness']:.1f}/255")
        print(f"  Red Ratio: {metrics['red_ratio']:.3f}")
        print(f"  Blue Ratio: {metrics['blue_ratio']:.3f}")
        print(f"  Brightness Threshold: {metrics['brightness_threshold']}")
        
        # Uncomment to show visualization
        # visualize_analysis(image_path)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to install required packages:")
        print("pip install opencv-python pillow matplotlib numpy")
        print("For servo control, install: sudo apt install python3-rpi-lgpio")
    finally:
        cleanup_servo()
