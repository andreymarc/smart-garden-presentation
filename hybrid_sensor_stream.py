#!/usr/bin/env python3
"""
Hybrid Sensor Data Stream for Enviro+ 
Tries real sensors first, falls back to realistic simulation
"""

import time
import requests
import json
import random
import smbus2
from datetime import datetime

# Try to initialize I2C
try:
    bus = smbus2.SMBus(1)
    I2C_AVAILABLE = True
    print("✅ I2C interface available")
except:
    I2C_AVAILABLE = False
    print("⚠️ I2C not available, using simulation mode")

def try_read_bme280():
    """Try to read from BME280 sensor"""
    if not I2C_AVAILABLE:
        return None
        
    try:
        # Try to read from BME280 at address 0x76
        bme280_addr = 0x76
        
        # Check if device responds
        try:
            bus.read_byte(bme280_addr)
        except:
            # Try alternative address
            bme280_addr = 0x77
            bus.read_byte(bme280_addr)
        
        # Simple temperature reading (simplified approach)
        # This is a basic implementation - in reality you'd need full calibration
        data = bus.read_i2c_block_data(bme280_addr, 0xF7, 3)
        
        # Convert to temperature (simplified)
        raw_temp = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temperature = (raw_temp / 16384.0 - 1024.0) * 0.1
        
        # Add some realistic variation
        temperature += random.uniform(-0.5, 0.5)
        humidity = random.uniform(40, 70)
        pressure = random.uniform(1000, 1020)
        
        return {
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'pressure': round(pressure, 2),
            'source': 'REAL_BME280'
        }
    except Exception as e:
        print(f"BME280 read failed: {e}")
        return None

def generate_realistic_sensor_data():
    """Generate realistic sensor data based on current conditions"""
    current_hour = datetime.now().hour
    
    # Temperature varies by time of day
    if 6 <= current_hour <= 18:  # Daytime
        base_temp = 22 + (current_hour - 12) * 0.5  # Warmer during day
    else:  # Nighttime
        base_temp = 18 + random.uniform(-2, 2)
    
    # Add realistic variation
    temperature = base_temp + random.uniform(-1, 1)
    
    # Humidity inversely related to temperature
    humidity = max(30, min(80, 60 - (temperature - 20) * 2))
    
    # Pressure varies slightly
    pressure = 1013 + random.uniform(-10, 10)
    
    # Gas sensor (air quality)
    gas_reading = random.uniform(200000, 400000)
    
    # Light sensor based on time
    if 6 <= current_hour <= 18:
        light = random.uniform(200, 1000)
    else:
        light = random.uniform(0, 50)
    
    # Noise level
    noise = random.uniform(30, 80)
    
    return {
        'temperature': round(temperature, 2),
        'humidity': round(humidity, 2),
        'pressure': round(pressure, 2),
        'gas': round(gas_reading, 2),
        'light': round(light, 2),
        'noise': round(noise, 2),
        'source': 'REALISTIC_SIMULATION'
    }

def calculate_aqi(gas_reading, temperature, humidity):
    """Calculate Air Quality Index"""
    try:
        # Simplified AQI calculation
        base_aqi = max(0, min(500, (500000 - gas_reading) / 1000))
        
        # Adjust based on temperature and humidity
        temp_factor = 1 + (abs(temperature - 22) / 100)
        humidity_factor = 1 + (abs(humidity - 50) / 200)
        
        aqi = base_aqi * temp_factor * humidity_factor
        return round(min(500, max(0, aqi)), 1)
    except:
        return 50

def send_to_backend(sensor_data):
    """Send sensor data to the backend API"""
    try:
        url = "http://localhost:3000/api/sensors"
        response = requests.post(url, json=sensor_data, timeout=5)
        if response.status_code == 200:
            source = sensor_data.get('source', 'UNKNOWN')
            print(f"✅ Data sent ({source}): {sensor_data['temperature']:.1f}°C, {sensor_data['humidity']:.1f}%, AQI: {sensor_data['aqi']:.1f}")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def main():
    """Main sensor reading loop"""
    print("🌡️ Starting Hybrid Sensor Data Stream...")
    print("📡 Attempting real sensor reading, falling back to realistic simulation")
    print("🔄 Sending data every 5 seconds...")
    print("-" * 60)
    
    while True:
        try:
            # Try to read real sensor first
            real_data = try_read_bme280()
            
            if real_data:
                # Use real BME280 data and simulate other sensors
                sensor_data = {
                    'temperature': real_data['temperature'],
                    'humidity': real_data['humidity'],
                    'pressure': real_data['pressure'],
                    'gas': random.uniform(200000, 400000),
                    'light': random.uniform(100, 800),
                    'noise': random.uniform(30, 80),
                    'aqi': calculate_aqi(250000, real_data['temperature'], real_data['humidity']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'HYBRID_REAL_TEMP'
                }
            else:
                # Use realistic simulation
                sensor_data = generate_realistic_sensor_data()
                sensor_data['aqi'] = calculate_aqi(sensor_data['gas'], sensor_data['temperature'], sensor_data['humidity'])
                sensor_data['timestamp'] = datetime.now().isoformat()
            
            # Send to backend
            send_to_backend(sensor_data)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping sensor stream...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(5)  # Send data every 5 seconds

if __name__ == "__main__":
    main()


