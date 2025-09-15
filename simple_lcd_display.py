#!/usr/bin/env python3
"""
Simple LCD Temperature Display for Enviro+
Displays temperature on the Enviro+ LCD screen
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
    print("✅ LCD libraries loaded")
except ImportError as e:
    print(f"❌ LCD libraries not available: {e}")
    LCD_AVAILABLE = False

# LCD Configuration for Enviro+
LCD_WIDTH = 160
LCD_HEIGHT = 80

def setup_lcd():
    """Setup the LCD display"""
    if not LCD_AVAILABLE:
        return None
    
    try:
        # Initialize ST7735 LCD with Enviro+ settings
        lcd = st7735.ST7735(
            port=0,
            cs=1,
            dc=9,
            backlight=12,
            rotation=0,
            spi_speed_hz=4000000
        )
        
        # Clear the display
        lcd.begin()
        lcd.clear()
        lcd.set_backlight(1)  # Turn on backlight
        
        print("✅ LCD initialized successfully")
        return lcd
    except Exception as e:
        print(f"❌ LCD setup error: {e}")
        return None

def get_temperature_color(temp):
    """Get color based on temperature"""
    if temp < 18:
        return (0, 0, 255)      # Blue - Cold
    elif temp <= 28:
        return (0, 255, 0)      # Green - Normal
    elif temp <= 32:
        return (255, 255, 0)    # Yellow - Warm
    else:
        return (255, 0, 0)      # Red - Hot

def get_temperature_status(temp):
    """Get temperature status text"""
    if temp < 18:
        return "COLD"
    elif temp <= 28:
        return "NORMAL"
    elif temp <= 32:
        return "WARM"
    else:
        return "HOT"

def get_current_temperature():
    """Get current temperature from API"""
    try:
        response = requests.get('http://localhost:3000/api/sensors')
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]['temperature']
    except Exception as e:
        print(f"API error: {e}")
    
    # Fallback to mock temperature
    return random.uniform(15, 35)

def draw_lcd_display(lcd, temperature):
    """Draw temperature on LCD"""
    if not lcd or not LCD_AVAILABLE:
        return
    
    try:
        # Create image
        image = Image.new('RGB', (LCD_WIDTH, LCD_HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Try to load fonts
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Get temperature color and status
        temp_color = get_temperature_color(temperature)
        temp_status = get_temperature_status(temperature)
        
        # Draw background with temperature color (dimmed)
        bg_color = tuple(int(c * 0.1) for c in temp_color)
        draw.rectangle([0, 0, LCD_WIDTH, LCD_HEIGHT], fill=bg_color)
        
        # Draw temperature (large, centered)
        temp_text = f"{temperature:.1f}°C"
        bbox = draw.textbbox((0, 0), temp_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (LCD_WIDTH - text_width) // 2
        draw.text((x, 10), temp_text, font=font_large, fill=temp_color)
        
        # Draw status (centered)
        bbox = draw.textbbox((0, 0), temp_status, font=font_medium)
        text_width = bbox[2] - bbox[0]
        x = (LCD_WIDTH - text_width) // 2
        draw.text((x, 35), temp_status, font=font_medium, fill=temp_color)
        
        # Draw time (small, bottom right)
        time_text = datetime.now().strftime("%H:%M")
        draw.text((LCD_WIDTH - 30, LCD_HEIGHT - 15), time_text, font=font_small, fill=(255, 255, 255))
        
        # Draw a border
        draw.rectangle([0, 0, LCD_WIDTH-1, LCD_HEIGHT-1], outline=temp_color, width=2)
        
        # Display on LCD
        lcd.display(image)
        
    except Exception as e:
        print(f"LCD draw error: {e}")

def main():
    """Main function to display temperature on LCD"""
    print("🌡️  Simple LCD Temperature Display")
    print("=" * 40)
    print(f"LCD Available: {LCD_AVAILABLE}")
    print("=" * 40)
    
    # Setup LCD
    lcd = setup_lcd()
    
    if not lcd:
        print("❌ LCD not available - running in console mode")
    
    try:
        while True:
            # Get current temperature
            temperature = get_current_temperature()
            status = get_temperature_status(temperature)
            
            # Display on LCD
            if lcd:
                draw_lcd_display(lcd, temperature)
            
            # Print to console
            print(f"\n📊 Temperature: {temperature:.1f}°C ({status})")
            print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Wait before next update
            time.sleep(3)
            
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



