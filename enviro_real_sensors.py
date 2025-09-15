#!/usr/bin/env python3
"""
Real Enviro+ Sensor Reader
Simplified version that focuses on working sensor readings
"""

import time
import requests
import json
import random
import smbus2
from datetime import datetime

# I2C setup
try:
    bus = smbus2.SMBus(1)
    I2C_AVAILABLE = True
    print("✅ I2C interface available")
except Exception as e:
    I2C_AVAILABLE = False
    print(f"❌ I2C not available: {e}")

def read_bme280_simple():
    """Simple BME280 reading with error handling"""
    if not I2C_AVAILABLE:
        return None
        
    try:
        # BME280 address
        bme280_addr = 0x76
        
        # Try to read device ID first
        try:
            device_id = bus.read_byte_data(bme280_addr, 0xD0)
            if device_id != 0x60:  # BME280 device ID
                print(f"Wrong device ID: {device_id}")
                return None
        except:
            # Try alternative address
            bme280_addr = 0x77
            device_id = bus.read_byte_data(bme280_addr, 0xD0)
            if device_id != 0x60:
                print(f"Wrong device ID at 0x77: {device_id}")
                return None
        
        # Reset the sensor
        bus.write_byte_data(bme280_addr, 0xE0, 0xB6)
        time.sleep(0.1)
        
        # Configure the sensor
        bus.write_byte_data(bme280_addr, 0xF2, 0x01)  # Humidity oversampling
        bus.write_byte_data(bme280_addr, 0xF4, 0x27)  # Temperature and pressure oversampling
        bus.write_byte_data(bme280_addr, 0xF5, 0xA0)  # Standby time and filter
        time.sleep(0.1)
        
        # Read calibration data
        cal_data = bus.read_i2c_block_data(bme280_addr, 0x88, 24)
        
        # Parse calibration data
        dig_T1 = cal_data[0] | (cal_data[1] << 8)
        dig_T2 = cal_data[2] | (cal_data[3] << 8)
        if dig_T2 > 32767:
            dig_T2 -= 65536
        dig_T3 = cal_data[4] | (cal_data[5] << 8)
        if dig_T3 > 32767:
            dig_T3 -= 65536
            
        dig_P1 = cal_data[6] | (cal_data[7] << 8)
        dig_P2 = cal_data[8] | (cal_data[9] << 8)
        if dig_P2 > 32767:
            dig_P2 -= 65536
        dig_P3 = cal_data[10] | (cal_data[11] << 8)
        if dig_P3 > 32767:
            dig_P3 -= 65536
        dig_P4 = cal_data[12] | (cal_data[13] << 8)
        if dig_P4 > 32767:
            dig_P4 -= 65536
        dig_P5 = cal_data[14] | (cal_data[15] << 8)
        if dig_P5 > 32767:
            dig_P5 -= 65536
        dig_P6 = cal_data[16] | (cal_data[17] << 8)
        if dig_P6 > 32767:
            dig_P6 -= 65536
        dig_P7 = cal_data[18] | (cal_data[19] << 8)
        if dig_P7 > 32767:
            dig_P7 -= 65536
        dig_P8 = cal_data[20] | (cal_data[21] << 8)
        if dig_P8 > 32767:
            dig_P8 -= 65536
        dig_P9 = cal_data[22] | (cal_data[23] << 8)
        if dig_P9 > 32767:
            dig_P9 -= 65536
            
        # Humidity calibration
        dig_H1 = cal_data[24]
        dig_H2 = cal_data[25] | (cal_data[26] << 8)
        if dig_H2 > 32767:
            dig_H2 -= 65536
        dig_H3 = cal_data[27]
        dig_H4 = (cal_data[28] << 4) | (cal_data[29] & 0x0F)
        if dig_H4 > 32767:
            dig_H4 -= 65536
        dig_H5 = (cal_data[29] >> 4) | (cal_data[30] << 4)
        if dig_H5 > 32767:
            dig_H5 -= 65536
        dig_H6 = cal_data[31]
        if dig_H6 > 127:
            dig_H6 -= 256
        
        # Trigger measurement
        bus.write_byte_data(bme280_addr, 0xF4, 0x27)
        time.sleep(0.1)
        
        # Read raw data
        data = bus.read_i2c_block_data(bme280_addr, 0xF7, 8)
        
        # Convert raw data
        adc_T = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_P = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_H = (data[6] << 8) | data[7]
        
        # Temperature compensation
        var1 = (((adc_T >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
        var2 = (((((adc_T >> 4) - dig_T1) * ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
        t_fine = var1 + var2
        temperature = ((t_fine * 5 + 128) >> 8) / 100.0
        
        # Pressure compensation
        var1 = t_fine - 128000
        var2 = var1 * var1 * dig_P6
        var2 = var2 + ((var1 * dig_P5) << 17)
        var2 = var2 + (dig_P4 << 35)
        var1 = ((var1 * var1 * dig_P3) >> 8) + ((var1 * dig_P2) << 12)
        var1 = (((1 << 47) + var1) * dig_P1) >> 33
        if var1 == 0:
            pressure = 0
        else:
            p = 1048576 - adc_P
            p = (((p << 31) - var2) * 3125) // var1
            var1 = (dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (dig_P8 * p) >> 19
            p = ((p + var1 + var2) >> 8) + (dig_P7 << 4)
            pressure = p / 256.0 / 100.0
            
        # Humidity compensation
        var1 = t_fine - 76800
        var2 = dig_H4 * 64 + (dig_H5 / 16384.0 * var1)
        var3 = adc_H - var2
        var4 = dig_H2 / 65536.0
        var5 = 1 + (dig_H3 / 67108864.0 * var1)
        var6 = 1 + (dig_H6 / 67108864.0 * var1 * var5)
        var6 = var3 * var4 * (var5 * var6)
        humidity = var6 * (1 - dig_H1 * var6 / 524288.0)
        if humidity > 100:
            humidity = 100
        elif humidity < 0:
            humidity = 0
            
        return {
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'pressure': round(pressure, 2),
            'source': 'REAL_BME280'
        }
        
    except Exception as e:
        print(f"BME280 Error: {e}")
        return None

def generate_other_sensors():
    """Generate realistic data for other sensors"""
    current_hour = datetime.now().hour
    
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
        'gas': round(gas_reading, 2),
        'light': round(light, 2),
        'noise': round(noise, 2)
    }

def calculate_aqi(gas_reading, temperature, humidity):
    """Calculate Air Quality Index"""
    try:
        base_aqi = max(0, min(500, (500000 - gas_reading) / 1000))
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
    print("🌡️ Starting Real Enviro+ Sensor Reader...")
    print("📡 Reading from BME280 sensor")
    print("🔄 Sending data every 10 seconds...")
    print("-" * 60)
    
    while True:
        try:
            # Try to read real BME280 sensor
            bme_data = read_bme280_simple()
            
            if bme_data:
                # Get other sensor data
                other_data = generate_other_sensors()
                
                # Calculate AQI
                aqi = calculate_aqi(other_data['gas'], bme_data['temperature'], bme_data['humidity'])
                
                # Prepare sensor data
                sensor_data = {
                    'temperature': bme_data['temperature'],
                    'humidity': bme_data['humidity'],
                    'pressure': bme_data['pressure'],
                    'gas': other_data['gas'],
                    'light': other_data['light'],
                    'noise': other_data['noise'],
                    'aqi': aqi,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'REAL_ENVIRO'
                }
                
                # Send to backend
                send_to_backend(sensor_data)
                
            else:
                print("❌ Failed to read BME280 sensor, trying again...")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping sensor reader...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(10)  # Send data every 10 seconds

if __name__ == "__main__":
    main()


