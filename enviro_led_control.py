#!/usr/bin/env python3
"""
Enviro LED Temperature Control
Controls the LED on the Enviro board to indicate temperature status:
- Blue: Cold (< 18°C)
- Green: Normal (18-28°C) 
- Yellow: Warm (28-32°C)
- Red: Hot (> 32°C)
"""

import time
import sys
import os

# Add the local packages to Python path
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')

try:
    from enviroplus import gas
    from pimoroni_bme280 import BME280
    from smbus2 import SMBus
    ENVIRO_AVAILABLE = True
except ImportError as e:
    print(f"Enviro libraries not available: {e}")
    ENVIRO_AVAILABLE = False

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
    """Set LED color on Enviro board"""
    try:
        # Import here to avoid issues if not available
        from enviroplus import LED
        led = LED()
        r, g, b = color
        led.set_led(r, g, b)
        print(f"LED set to RGB({r}, {g}, {b})")
    except ImportError:
        print("LED control not available - using console output only")
    except Exception as e:
        print(f"Error setting LED: {e}")

def read_sensor_data():
    """Read temperature from BME280 sensor"""
    try:
        # Initialize BME280 sensor
        bus = SMBus(1)
        bme280 = BME280(i2c_dev=bus)
        
        # Read sensor data
        temperature = bme280.get_temperature()
        humidity = bme280.get_humidity()
        pressure = bme280.get_pressure()
        
        return {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure
        }
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return None

def main():
    """Main function to control LED based on temperature"""
    print("🌡️  Enviro LED Temperature Control")
    print("=" * 40)
    print(f"Temperature thresholds:")
    print(f"  Cold: < {TEMP_COLD}°C (Blue)")
    print(f"  Normal: {TEMP_COLD}-{TEMP_NORMAL_MAX}°C (Green)")
    print(f"  Warm: {TEMP_NORMAL_MAX}-{TEMP_WARM_MAX}°C (Yellow)")
    print(f"  Hot: > {TEMP_WARM_MAX}°C (Red)")
    print("=" * 40)
    
    try:
        while True:
            # Read sensor data
            sensor_data = read_sensor_data()
            
            if sensor_data:
                temp = sensor_data['temperature']
                humidity = sensor_data['humidity']
                pressure = sensor_data['pressure']
                
                # Determine temperature status
                status = get_temperature_status(temp)
                color = LED_COLORS[status]
                
                # Display current readings
                print(f"\n📊 Current Readings:")
                print(f"  Temperature: {temp:.1f}°C ({status.upper()})")
                print(f"  Humidity: {humidity:.1f}%")
                print(f"  Pressure: {pressure:.1f} hPa")
                
                # Set LED color
                set_led_color(color)
                
                # Send data to our smart garden API
                try:
                    import requests
                    api_data = {
                        'temperature': temp,
                        'humidity': humidity,
                        'pressure': pressure,
                        'gas': 250000,  # Mock gas reading
                        'reducing': 150000,
                        'nh3': 75000
                    }
                    
                    response = requests.post('http://localhost:3000/api/sensors', json=api_data)
                    if response.status_code == 201:
                        print("✅ Data sent to smart garden API")
                    else:
                        print(f"⚠️  API response: {response.status_code}")
                except Exception as e:
                    print(f"⚠️  Could not send to API: {e}")
                
            else:
                print("❌ Failed to read sensor data")
            
            # Wait before next reading
            print(f"⏱️  Waiting 30 seconds...")
            time.sleep(30)
            
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
