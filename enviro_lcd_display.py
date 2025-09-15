#!/usr/bin/env python3
"""
Enviro+ LCD Temperature Display
Displays temperature and other sensor data on the Enviro+ LCD screen
"""

import time
import sys
import requests
import random
from datetime import datetime

# Add the local packages to Python path
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')

try:
    import st7735
    from PIL import Image, ImageDraw, ImageFont
    LCD_AVAILABLE = True
except ImportError as e:
    print(f"LCD libraries not available: {e}")
    LCD_AVAILABLE = False

try:
    from pimoroni_bme280 import BME280
    from smbus2 import SMBus
    SENSOR_AVAILABLE = True
except ImportError as e:
    print(f"Sensor libraries not available: {e}")
    SENSOR_AVAILABLE = False

# LCD Configuration for Enviro+
LCD_WIDTH = 160
LCD_HEIGHT = 80
LCD_ROTATION = 0

# Temperature thresholds
TEMP_COLD = 18
TEMP_NORMAL_MAX = 28
TEMP_WARM_MAX = 32

def setup_lcd():
    """Setup the LCD display"""
    if not LCD_AVAILABLE:
        return None
    
    try:
        # Initialize ST7735 LCD
        lcd = st7735.ST7735(
            port=0,
            cs=1,
            dc=9,
            backlight=12,
            rotation=LCD_ROTATION,
            spi_speed_hz=4000000
        )
        
        # Clear the display
        lcd.begin()
        lcd.clear()
        
        print("✅ LCD initialized successfully")
        return lcd
    except Exception as e:
        print(f"❌ LCD setup error: {e}")
        return None

def get_temperature_color(temp):
    """Get color based on temperature"""
    if temp < TEMP_COLD:
        return (0, 0, 255)      # Blue - Cold
    elif temp <= TEMP_NORMAL_MAX:
        return (0, 255, 0)      # Green - Normal
    elif temp <= TEMP_WARM_MAX:
        return (255, 255, 0)    # Yellow - Warm
    else:
        return (255, 0, 0)      # Red - Hot

def get_temperature_status(temp):
    """Get temperature status text"""
    if temp < TEMP_COLD:
        return "COLD"
    elif temp <= TEMP_NORMAL_MAX:
        return "NORMAL"
    elif temp <= TEMP_WARM_MAX:
        return "WARM"
    else:
        return "HOT"

def read_sensor_data():
    """Read sensor data from BME280 or API"""
    if SENSOR_AVAILABLE:
        try:
            bus = SMBus(1)
            bme280 = BME280(i2c_dev=bus)
            
            temperature = bme280.get_temperature()
            humidity = bme280.get_humidity()
            pressure = bme280.get_pressure()
            
            return {
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure,
                'source': 'sensor'
            }
        except Exception as e:
            print(f"Sensor read error: {e}")
    
    # Fallback to API
    try:
        response = requests.get('http://localhost:3000/api/sensors')
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return {
                    'temperature': data[0]['temperature'],
                    'humidity': data[0]['humidity'],
                    'pressure': data[0]['pressure'],
                    'source': 'api'
                }
    except Exception as e:
        print(f"API read error: {e}")
    
    # Final fallback to mock data
    return {
        'temperature': random.uniform(15, 35),
        'humidity': random.uniform(30, 70),
        'pressure': random.uniform(980, 1020),
        'source': 'mock'
    }

def draw_lcd_display(lcd, sensor_data):
    """Draw sensor data on LCD"""
    if not lcd or not LCD_AVAILABLE:
        return
    
    try:
        # Create image
        image = Image.new('RGB', (LCD_WIDTH, LCD_HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Try to load a font, fallback to default if not available
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        temp = sensor_data['temperature']
        humidity = sensor_data['humidity']
        pressure = sensor_data['pressure']
        source = sensor_data['source']
        
        # Get temperature color and status
        temp_color = get_temperature_color(temp)
        temp_status = get_temperature_status(temp)
        
        # Draw background with temperature color (dimmed)
        bg_color = tuple(int(c * 0.1) for c in temp_color)
        draw.rectangle([0, 0, LCD_WIDTH, LCD_HEIGHT], fill=bg_color)
        
        # Draw temperature (large)
        temp_text = f"{temp:.1f}°C"
        draw.text((5, 5), temp_text, font=font_large, fill=temp_color)
        
        # Draw status
        draw.text((5, 25), temp_status, font=font_small, fill=temp_color)
        
        # Draw humidity
        humidity_text = f"H: {humidity:.0f}%"
        draw.text((5, 40), humidity_text, font=font_small, fill=(255, 255, 255))
        
        # Draw pressure
        pressure_text = f"P: {pressure:.0f}hPa"
        draw.text((5, 55), pressure_text, font=font_small, fill=(255, 255, 255))
        
        # Draw source indicator
        source_text = f"({source})"
        draw.text((5, 70), source_text, font=font_small, fill=(128, 128, 128))
        
        # Draw time
        time_text = datetime.now().strftime("%H:%M")
        draw.text((LCD_WIDTH - 40, 5), time_text, font=font_small, fill=(255, 255, 255))
        
        # Display on LCD
        lcd.display(image)
        
    except Exception as e:
        print(f"LCD draw error: {e}")

def main():
    """Main function to display temperature on LCD"""
    print("🌡️  Enviro+ LCD Temperature Display")
    print("=" * 40)
    print(f"LCD Available: {LCD_AVAILABLE}")
    print(f"Sensor Available: {SENSOR_AVAILABLE}")
    print("=" * 40)
    
    # Setup LCD
    lcd = setup_lcd()
    
    if not lcd:
        print("❌ LCD not available - running in console mode")
    
    try:
        while True:
            # Read sensor data
            sensor_data = read_sensor_data()
            
            # Display on LCD
            if lcd:
                draw_lcd_display(lcd, sensor_data)
            
            # Also print to console
            temp = sensor_data['temperature']
            humidity = sensor_data['humidity']
            pressure = sensor_data['pressure']
            source = sensor_data['source']
            status = get_temperature_status(temp)
            
            print(f"\n📊 Sensor Data ({source}):")
            print(f"  Temperature: {temp:.1f}°C ({status})")
            print(f"  Humidity: {humidity:.1f}%")
            print(f"  Pressure: {pressure:.1f} hPa")
            print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Wait before next update
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping LCD display...")
        if lcd:
            lcd.clear()
            lcd.set_backlight(0)  # Turn off backlight
        print("✅ LCD display stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        if lcd:
            lcd.clear()
        sys.exit(1)

if __name__ == "__main__":
    main()



