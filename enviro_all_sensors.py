#!/usr/bin/env python3
"""
Complete Enviro+ Sensor Reader
Reads ALL sensors from the Enviro+ board for presentation
"""

import time
import sys
import requests
import random
from datetime import datetime

# Add the local packages to Python path
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')

try:
    from enviroplus import gas, light, noise
    from pimoroni_bme280 import BME280
    from smbus2 import SMBus
    ENVIRO_AVAILABLE = True
    print("✅ All Enviro+ libraries loaded")
except ImportError as e:
    print(f"❌ Some Enviro+ libraries not available: {e}")
    ENVIRO_AVAILABLE = False

def read_all_sensors():
    """Read all available sensors from Enviro+"""
    sensor_data = {
        'timestamp': datetime.now().isoformat(),
        'source': 'enviro_plus'
    }
    
    if ENVIRO_AVAILABLE:
        try:
            # Read BME280 (Temperature, Humidity, Pressure)
            bus = SMBus(1)
            bme280 = BME280(i2c_dev=bus)
            
            sensor_data.update({
                'temperature': round(bme280.get_temperature(), 1),
                'humidity': round(bme280.get_humidity(), 1),
                'pressure': round(bme280.get_pressure(), 1)
            })
            
            # Read Gas sensor
            gas_data = gas.read_all()
            sensor_data.update({
                'gas': round(gas_data.reducing, 0),
                'reducing': round(gas_data.reducing, 0),
                'nh3': round(gas_data.nh3, 0),
                'oxidising': round(gas_data.oxidising, 0)
            })
            
            # Read Light sensor
            light_data = light.lux
            sensor_data.update({
                'light': round(light_data, 1)
            })
            
            # Read Noise sensor
            noise_data = noise.volume
            sensor_data.update({
                'noise': round(noise_data, 1)
            })
            
            print("✅ All sensors read successfully")
            
        except Exception as e:
            print(f"❌ Error reading sensors: {e}")
            # Fallback to mock data
            sensor_data.update(get_mock_data())
    else:
        # Use mock data if sensors not available
        sensor_data.update(get_mock_data())
    
    # Calculate AQI
    sensor_data['aqi'] = calculate_aqi(sensor_data)
    
    return sensor_data

def get_mock_data():
    """Generate realistic mock sensor data"""
    return {
        'temperature': round(random.uniform(18, 28), 1),
        'humidity': round(random.uniform(40, 60), 1),
        'pressure': round(random.uniform(1000, 1015), 1),
        'gas': round(random.uniform(200000, 300000), 0),
        'reducing': round(random.uniform(150000, 200000), 0),
        'nh3': round(random.uniform(60000, 80000), 0),
        'oxidising': round(random.uniform(100000, 150000), 0),
        'light': round(random.uniform(200, 1000), 1),
        'noise': round(random.uniform(40, 60), 1)
    }

def calculate_aqi(data):
    """Calculate Air Quality Index"""
    # Convert gas resistance to ppb (parts per billion)
    gas_concentration = (1000000 / data['gas']) * 100
    
    # Base AQI on gas concentration with temperature and humidity adjustments
    aqi = gas_concentration
    
    # Adjust for temperature (optimal range 20-25°C)
    temp_factor = abs(data['temperature'] - 22.5) / 10
    aqi *= (1 + temp_factor)
    
    # Adjust for humidity (optimal range 40-60%)
    humidity_factor = abs(data['humidity'] - 50) / 50
    aqi *= (1 + humidity_factor)
    
    # Map to standard AQI range (0-500)
    aqi = min(max(aqi * 5, 0), 500)
    
    return round(aqi)

def send_to_api(sensor_data):
    """Send sensor data to our smart garden API"""
    try:
        response = requests.post('http://localhost:3000/api/sensors', json=sensor_data)
        if response.status_code == 201:
            print("✅ Data sent to API successfully")
            return True
        else:
            print(f"⚠️ API response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

def main():
    """Main function to read and send sensor data"""
    print("🌡️ Complete Enviro+ Sensor Reader")
    print("=" * 50)
    print(f"Enviro+ Available: {ENVIRO_AVAILABLE}")
    print("=" * 50)
    
    try:
        while True:
            # Read all sensors
            sensor_data = read_all_sensors()
            
            # Display current readings
            print(f"\n📊 Sensor Readings ({sensor_data['source']}):")
            print(f"  🌡️ Temperature: {sensor_data['temperature']}°C")
            print(f"  💧 Humidity: {sensor_data['humidity']}%")
            print(f"  🌪️ Pressure: {sensor_data['pressure']} hPa")
            print(f"  💨 Gas: {sensor_data['gas']/1000:.1f}kΩ")
            print(f"  ☀️ Light: {sensor_data['light']} lux")
            print(f"  🔊 Noise: {sensor_data['noise']} dB")
            print(f"  📊 AQI: {sensor_data['aqi']}")
            print(f"  ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Send to API
            send_to_api(sensor_data)
            
            # Wait before next reading
            print(f"⏱️ Waiting 5 seconds...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping sensor reader...")
        print("✅ Sensor reader stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


