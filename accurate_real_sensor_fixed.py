#!/usr/bin/env python3

import smbus2
import time
import requests
import json
import sys

# Temperature offset to compensate for Pi heating
TEMPERATURE_OFFSET = -2.0  # Small offset to account for Pi heating

def read_bme280():
    """Read BME280 sensor with proper calibration and offset"""
    bus = smbus2.SMBus(1)
    address = 0x76
    
    try:
        # Read calibration data
        cal1 = bus.read_i2c_block_data(address, 0x88, 24)
        cal2 = bus.read_i2c_block_data(address, 0xA1, 1)
        cal3 = bus.read_i2c_block_data(address, 0xE1, 7)
        
        # Read sensor data
        data = bus.read_i2c_block_data(address, 0xF7, 8)
        
        # Temperature calculation
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        dig_T1 = cal1[0] | (cal1[1] << 8)
        dig_T2 = cal1[2] | (cal1[3] << 8)
        dig_T3 = cal1[4] | (cal1[5] << 8)
        
        if dig_T2 > 32767:
            dig_T2 -= 65536
        if dig_T3 > 32767:
            dig_T3 -= 65536
        
        var1 = (temp_raw / 16384.0 - dig_T1 / 1024.0) * dig_T2
        var2 = ((temp_raw / 131072.0 - dig_T1 / 8192.0) * (temp_raw / 131072.0 - dig_T1 / 8192.0)) * dig_T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0 + TEMPERATURE_OFFSET
        
        # Humidity calculation
        hum_raw = (data[6] << 8) | data[7]
        dig_H1 = cal2[0]
        dig_H2 = cal1[6] | (cal1[7] << 8)
        dig_H3 = cal1[8]
        dig_H4 = (cal1[9] << 4) | (cal1[10] & 0x0F)
        dig_H5 = (cal1[11] << 4) | (cal1[10] >> 4)
        dig_H6 = cal1[12]
        
        if dig_H2 > 32767:
            dig_H2 -= 65536
        if dig_H4 > 32767:
            dig_H4 -= 65536
        if dig_H5 > 32767:
            dig_H5 -= 65536
        if dig_H6 > 127:
            dig_H6 -= 256
        
        var_H = t_fine - 76800.0
        var_H = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * var_H)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * var_H * (1.0 + dig_H3 / 67108864.0 * var_H)))
        humidity = max(0.0, min(100.0, var_H))
        
        # Pressure calculation
        press_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        dig_P1 = cal1[6] | (cal1[7] << 8)
        dig_P2 = cal1[8] | (cal1[9] << 8)
        dig_P3 = cal1[10] | (cal1[11] << 8)
        dig_P4 = cal1[12] | (cal1[13] << 8)
        dig_P5 = cal1[14] | (cal1[15] << 8)
        dig_P6 = cal1[16] | (cal1[17] << 8)
        dig_P7 = cal1[18] | (cal1[19] << 8)
        dig_P8 = cal1[20] | (cal1[21] << 8)
        dig_P9 = cal1[22] | (cal1[23] << 8)
        
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
        if response.status_code == 200:
            print(f"✅ Data sent: {sensor_data['temperature']}°C, {sensor_data['humidity']}% RH, {sensor_data['pressure']} hPa")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    print("🌡️  Smart Garden Sensor Reader (Fixed Temperature)")
    print("=" * 50)
    print(f"Temperature offset: {TEMPERATURE_OFFSET}°C")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            sensor_data = read_bme280()
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

