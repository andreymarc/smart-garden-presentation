#!/usr/bin/env python3
"""
GPIO LED Temperature Control for Enviro
Controls an external LED connected to GPIO pins based on temperature readings
LED Connection: Red=GPIO18, Green=GPIO23, Blue=GPIO24
"""

import time
import sys
import requests
import random

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("RPi.GPIO not available")

# GPIO pins for RGB LED (you can change these based on your wiring)
RED_PIN = 18
GREEN_PIN = 23
BLUE_PIN = 24

# Temperature thresholds
TEMP_COLD = 18
TEMP_NORMAL_MAX = 28
TEMP_WARM_MAX = 32

# LED colors (RGB values 0-1 for PWM)
LED_COLORS = {
    'cold': (0, 0, 1),        # Blue
    'normal': (0, 1, 0),      # Green
    'warm': (1, 1, 0),        # Yellow (Red + Green)
    'hot': (1, 0, 0),         # Red
    'off': (0, 0, 0)          # Off
}

def setup_gpio():
    """Setup GPIO pins for LED control"""
    if not GPIO_AVAILABLE:
        return False
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RED_PIN, GPIO.OUT)
        GPIO.setup(GREEN_PIN, GPIO.OUT)
        GPIO.setup(BLUE_PIN, GPIO.OUT)
        
        # Setup PWM for smooth color control
        red_pwm = GPIO.PWM(RED_PIN, 1000)  # 1kHz frequency
        green_pwm = GPIO.PWM(GREEN_PIN, 1000)
        blue_pwm = GPIO.PWM(BLUE_PIN, 1000)
        
        red_pwm.start(0)
        green_pwm.start(0)
        blue_pwm.start(0)
        
        return red_pwm, green_pwm, blue_pwm
    except Exception as e:
        print(f"GPIO setup error: {e}")
        return False

def set_led_color(color, pwm_objects=None):
    """Set LED color using GPIO PWM"""
    r, g, b = color
    
    if pwm_objects and GPIO_AVAILABLE:
        try:
            red_pwm, green_pwm, blue_pwm = pwm_objects
            # Convert 0-1 values to 0-100 for PWM
            red_pwm.ChangeDutyCycle(r * 100)
            green_pwm.ChangeDutyCycle(g * 100)
            blue_pwm.ChangeDutyCycle(b * 100)
            
            color_name = {
                (0, 0, 1): "BLUE (Cold)",
                (0, 1, 0): "GREEN (Normal)", 
                (1, 1, 0): "YELLOW (Warm)",
                (1, 0, 0): "RED (Hot)",
                (0, 0, 0): "OFF"
            }.get(color, "UNKNOWN")
            print(f"✅ LED set to {color_name} RGB({r:.1f}, {g:.1f}, {b:.1f})")
            return True
        except Exception as e:
            print(f"❌ LED control error: {e}")
            return False
    else:
        # Fallback - just print the color
        color_name = {
            (0, 0, 1): "BLUE (Cold)",
            (0, 1, 0): "GREEN (Normal)", 
            (1, 1, 0): "YELLOW (Warm)",
            (1, 0, 0): "RED (Hot)",
            (0, 0, 0): "OFF"
        }.get(color, "UNKNOWN")
        print(f"💡 LED would be set to {color_name} RGB({r:.1f}, {g:.1f}, {b:.1f})")
        return False

def cleanup_gpio(pwm_objects=None):
    """Cleanup GPIO resources"""
    if pwm_objects:
        try:
            red_pwm, green_pwm, blue_pwm = pwm_objects
            red_pwm.stop()
            green_pwm.stop()
            blue_pwm.stop()
        except:
            pass
    
    if GPIO_AVAILABLE:
        try:
            GPIO.cleanup()
        except:
            pass

def get_temperature_status(temp):
    """Determine temperature status based on thresholds"""
    if temp < TEMP_COLD:
        return 'cold'
    elif temp <= TEMP_NORMAL_MAX:
        return 'normal'
    elif temp <= TEMP_WARM_MAX:
        return 'warm'
    else:
        return 'hot'

def get_current_temperature():
    """Get current temperature from our smart garden API"""
    try:
        response = requests.get('http://localhost:3000/api/sensors')
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]['temperature']
    except Exception as e:
        print(f"Could not get temperature from API: {e}")
    
    # Fallback to mock temperature
    return random.uniform(15, 35)

def main():
    """Main function to control LED based on temperature"""
    print("🌡️  GPIO LED Temperature Control")
    print("=" * 40)
    print(f"Temperature thresholds:")
    print(f"  Cold: < {TEMP_COLD}°C (Blue)")
    print(f"  Normal: {TEMP_COLD}-{TEMP_NORMAL_MAX}°C (Green)")
    print(f"  Warm: {TEMP_NORMAL_MAX}-{TEMP_WARM_MAX}°C (Yellow)")
    print(f"  Hot: > {TEMP_WARM_MAX}°C (Red)")
    print("=" * 40)
    print(f"GPIO Pins: Red={RED_PIN}, Green={GREEN_PIN}, Blue={BLUE_PIN}")
    print(f"GPIO Available: {GPIO_AVAILABLE}")
    print("=" * 40)
    
    # Setup GPIO
    pwm_objects = setup_gpio()
    
    try:
        while True:
            # Get current temperature
            temp = get_current_temperature()
            
            # Determine temperature status
            status = get_temperature_status(temp)
            color = LED_COLORS[status]
            
            # Display current reading
            print(f"\n📊 Current Temperature: {temp:.1f}°C ({status.upper()})")
            
            # Set LED color
            set_led_color(color, pwm_objects)
            
            # Wait before next reading
            print(f"⏱️  Waiting 10 seconds...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping LED control...")
        # Turn off LED
        set_led_color(LED_COLORS['off'], pwm_objects)
        cleanup_gpio(pwm_objects)
        print("✅ LED turned off and GPIO cleaned up")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup_gpio(pwm_objects)
        sys.exit(1)

if __name__ == "__main__":
    main()


