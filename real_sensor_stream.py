#!/usr/bin/env python3
"""
Real Sensor Data Stream for Enviro+ 
Simplified version that reads actual sensor data
"""

import time
import requests
import json
import smbus2
import random
from datetime import datetime

# I2C bus setup
bus = smbus2.SMBus(1)

def read_bme280_sensor():
    """Read temperature, humidity, and pressure from BME280 sensor"""
    try:
        # BME280 I2C address
        bme280_addr = 0x76
        
        # Read calibration data
        cal_data = bus.read_i2c_block_data(bme280_addr, 0x88, 24)
        
        # Convert calibration data
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
            'pressure': round(pressure, 2)
        }
    except Exception as e:
        print(f"BME280 Error: {e}")
        return None

def read_gas_sensor():
    """Read gas sensor (simplified - using analog reading)"""
    try:
        # For now, we'll use a realistic range based on typical gas sensor readings
        # In a real implementation, you'd read from the ADC
        gas_reading = random.uniform(200000, 400000)  # Ohms
        return round(gas_reading, 2)
    except Exception as e:
        print(f"Gas Sensor Error: {e}")
        return 250000

def read_light_sensor():
    """Read light sensor (simplified)"""
    try:
        # Simulate light reading based on time of day
        hour = datetime.now().hour
        if 6 <= hour <= 18:  # Daytime
            light = random.uniform(200, 1000)
        else:  # Nighttime
            light = random.uniform(0, 50)
        return round(light, 2)
    except Exception as e:
        print(f"Light Sensor Error: {e}")
        return 100

def read_noise_sensor():
    """Read noise sensor (simplified)"""
    try:
        # Simulate noise level
        noise = random.uniform(30, 80)
        return round(noise, 2)
    except Exception as e:
        print(f"Noise Sensor Error: {e}")
        return 50

def calculate_aqi(gas_reading, temperature, humidity):
    """Calculate Air Quality Index based on sensor readings"""
    try:
        # Simplified AQI calculation
        # Lower gas resistance = worse air quality
        base_aqi = max(0, min(500, (500000 - gas_reading) / 1000))
        
        # Adjust based on temperature and humidity
        temp_factor = 1 + (abs(temperature - 22) / 100)  # Optimal around 22°C
        humidity_factor = 1 + (abs(humidity - 50) / 200)  # Optimal around 50%
        
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
            print(f"✅ Data sent: {sensor_data['temperature']:.1f}°C, {sensor_data['humidity']:.1f}%, AQI: {sensor_data['aqi']:.1f}")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def main():
    """Main sensor reading loop"""
    print("🌡️ Starting Real Sensor Data Stream...")
    print("📡 Reading from BME280 sensor and simulated other sensors")
    print("🔄 Sending data every 5 seconds...")
    print("-" * 50)
    
    while True:
        try:
            # Read BME280 sensor (real data)
            bme_data = read_bme280_sensor()
            
            if bme_data:
                # Read other sensors (simulated for now)
                gas_reading = read_gas_sensor()
                light_reading = read_light_sensor()
                noise_reading = read_noise_sensor()
                
                # Calculate AQI
                aqi = calculate_aqi(gas_reading, bme_data['temperature'], bme_data['humidity'])
                
                # Prepare sensor data
                sensor_data = {
                    'temperature': bme_data['temperature'],
                    'humidity': bme_data['humidity'],
                    'pressure': bme_data['pressure'],
                    'gas': gas_reading,
                    'light': light_reading,
                    'noise': noise_reading,
                    'aqi': aqi,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Send to backend
                send_to_backend(sensor_data)
                
            else:
                print("❌ Failed to read BME280 sensor")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping sensor stream...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(5)  # Send data every 5 seconds

if __name__ == "__main__":
    main()

