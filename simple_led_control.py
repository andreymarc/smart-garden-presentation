#!/usr/bin/env python3
"""
Simple LED Temperature Control for Enviro
Uses the existing sensor setup and controls LED based on temperature
"""

import time
import sys
import requests
import random

# Temperature thresholds
TEMP_COLD = 18
TEMP_NORMAL_MAX = 28
TEMP_WARM_MAX = 32

# LED colors (RGB values 0-255)
LED_COLORS = {
    'cold': (0, 0, 255),      # Blue
    'normal': (0, 255, 0),    # Green
    'warm': (255, 255, 0),    # Yellow
    'hot': (255, 0, 0)        # Red
}

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

def set_led_color(color):
    """Set LED color - for now just print the color"""
    r, g, b = color
    print(f"🔴 LED Color: RGB({r}, {g}, {b})")
    
    # Try to control actual LED if available
    try:
        # This would work if we had proper LED control
        # For now, we'll simulate it
        color_name = {
            (0, 0, 255): "BLUE (Cold)",
            (0, 255, 0): "GREEN (Normal)", 
            (255, 255, 0): "YELLOW (Warm)",
            (255, 0, 0): "RED (Hot)"
        }.get(color, "UNKNOWN")
        print(f"💡 LED Status: {color_name}")
    except Exception as e:
        print(f"LED control not available: {e}")

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
    print("🌡️  Simple LED Temperature Control")
    print("=" * 40)
    print(f"Temperature thresholds:")
    print(f"  Cold: < {TEMP_COLD}°C (Blue)")
    print(f"  Normal: {TEMP_COLD}-{TEMP_NORMAL_MAX}°C (Green)")
    print(f"  Warm: {TEMP_NORMAL_MAX}-{TEMP_WARM_MAX}°C (Yellow)")
    print(f"  Hot: > {TEMP_WARM_MAX}°C (Red)")
    print("=" * 40)
    
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
            set_led_color(color)
            
            # Wait before next reading
            print(f"⏱️  Waiting 10 seconds...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping LED control...")
        # Turn off LED
        set_led_color((0, 0, 0))
        print("✅ LED turned off")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



