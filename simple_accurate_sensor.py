#!/usr/bin/env python3

import smbus2
import time
import requests
import json
import sys

# Temperature offset to compensate for Pi heating
TEMPERATURE_OFFSET = 0.0  # No offset needed - sensor is reading accurately

def read_bme280_simple():
    """Read BME280 sensor with simplified calculation"""
    bus = smbus2.SMBus(1)
    address = 0x76
    
    try:
        # Read calibration data
        cal_data = bus.read_i2c_block_data(address, 0x88, 24)
        
        # Read sensor data
        data = bus.read_i2c_block_data(address, 0xF7, 8)
        
        # Initialize sensor properly
        bus.write_byte_data(address, 0xF2, 0x01)  # Humidity oversampling
        bus.write_byte_data(address, 0xF4, 0x27)  # Temperature and pressure oversampling, normal mode
        time.sleep(0.1)
        
        # Read sensor data again after initialization
        data = bus.read_i2c_block_data(address, 0xF7, 8)
        
        # Temperature calculation (proper BME280 formula)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        
        # Get calibration values
        dig_T1 = cal_data[0] | (cal_data[1] << 8)
        dig_T2 = cal_data[2] | (cal_data[3] << 8)
        dig_T3 = cal_data[4] | (cal_data[5] << 8)
        
        # Handle signed values
        if dig_T2 > 32767:
            dig_T2 -= 65536
        if dig_T3 > 32767:
            dig_T3 -= 65536
        
        # Calculate temperature
        var1 = (temp_raw / 16384.0 - dig_T1 / 1024.0) * dig_T2
        var2 = ((temp_raw / 131072.0 - dig_T1 / 8192.0) ** 2) * dig_T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0 + TEMPERATURE_OFFSET
        
        # Humidity calculation - simplified approach
        hum_raw = (data[6] << 8) | data[7]
        
        # Read humidity calibration data from correct registers
        try:
            dig_H1 = bus.read_byte_data(address, 0xA1)
            dig_H2 = bus.read_i2c_block_data(address, 0xE1, 2)
            dig_H2 = dig_H2[0] | (dig_H2[1] << 8)
            dig_H3 = bus.read_byte_data(address, 0xE3)
            dig_H4 = bus.read_i2c_block_data(address, 0xE4, 2)
            dig_H4 = (dig_H4[0] << 4) | (dig_H4[1] & 0x0F)
            dig_H5 = bus.read_i2c_block_data(address, 0xE5, 2)
            dig_H5 = (dig_H5[0] << 4) | (dig_H5[1] >> 4)
            dig_H6 = bus.read_byte_data(address, 0xE7)
            
            # Handle signed values
            if dig_H2 > 32767:
                dig_H2 -= 65536
            if dig_H4 > 32767:
                dig_H4 -= 65536
            if dig_H5 > 32767:
                dig_H5 -= 65536
            if dig_H6 > 127:
                dig_H6 -= 256
            
            # Calculate humidity using BME280 formula
            var_H = t_fine - 76800.0
            var_H = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * var_H)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * var_H * (1.0 + dig_H3 / 67108864.0 * var_H)))
            humidity = max(0.0, min(100.0, var_H))
            
        except Exception as e:
            print(f"Humidity calibration error: {e}")
            # Fallback: use a simple linear approximation
            humidity = max(0.0, min(100.0, (hum_raw / 65536.0) * 100.0))
        
        # Pressure calculation
        press_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        dig_P1 = cal_data[6] | (cal_data[7] << 8)
        dig_P2 = cal_data[8] | (cal_data[9] << 8)
        dig_P3 = cal_data[10] | (cal_data[11] << 8)
        dig_P4 = cal_data[12] | (cal_data[13] << 8)
        dig_P5 = cal_data[14] | (cal_data[15] << 8)
        dig_P6 = cal_data[16] | (cal_data[17] << 8)
        dig_P7 = cal_data[18] | (cal_data[19] << 8)
        dig_P8 = cal_data[20] | (cal_data[21] << 8)
        dig_P9 = cal_data[22] | (cal_data[23] << 8)
        
        if dig_P2 > 32767:
            dig_P2 -= 65536
        if dig_P3 > 32767:
            dig_P3 -= 65536
        if dig_P4 > 32767:
            dig_P4 -= 65536
        if dig_P5 > 32767:
            dig_P5 -= 65536
        if dig_P6 > 32767:
            dig_P6 -= 65536
        if dig_P7 > 32767:
            dig_P7 -= 65536
        if dig_P8 > 32767:
            dig_P8 -= 65536
        if dig_P9 > 32767:
            dig_P9 -= 65536
        
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_P6 / 32768.0
        var2 = var2 + var1 * dig_P5 * 2.0
        var2 = var2 / 4.0 + dig_P4 * 65536.0
        var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_P1
        pressure = 1048576.0 - press_raw
        pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
        var1 = dig_P9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_P8 / 32768.0
        pressure = pressure + (var1 + var2 + dig_P7) / 16.0
        
        return {
            'temperature': round(temperature, 1),
            'humidity': round(humidity, 1),
            'pressure': round(pressure / 100, 1)  # Convert to hPa
        }
        
    except Exception as e:
        print(f"Error reading BME280: {e}")
        return None

def send_to_api(sensor_data):
    """Send sensor data to the API"""
    try:
        url = 'http://localhost:3000/api/sensors'
        response = requests.post(url, json=sensor_data, timeout=5)
        if response.status_code in [200, 201]:  # Both 200 and 201 are success codes
            print(f"✅ Data sent: {sensor_data['temperature']}°C, {sensor_data['humidity']}% RH, {sensor_data['pressure']} hPa")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    print("🌡️  AeroStream Sensor Reader (Simple & Accurate)")
    print("=" * 50)
    print(f"Temperature offset: {TEMPERATURE_OFFSET}°C")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            sensor_data = read_bme280_simple()
            if sensor_data:
                # Add timestamp
                sensor_data['timestamp'] = int(time.time() * 1000)
                
                # Add simulated data for other sensors
                sensor_data['gas'] = None
                sensor_data['reducing'] = None
                sensor_data['nh3'] = None
                sensor_data['aqi'] = None
                sensor_data['light'] = None
                sensor_data['noise'] = None
                
                send_to_api(sensor_data)
            else:
                print("❌ Failed to read sensor data")
            
            time.sleep(15)  # Send data every 15 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Sensor reader stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
