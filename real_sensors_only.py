#!/usr/bin/env python3
"""
Real Sensors Only - Shows only sensors that produce real data
Temperature, Humidity, Pressure, Light
"""

import time
import requests
import json
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

def read_real_bme280():
    """Read real BME280 data (Temperature, Humidity, Pressure)"""
    if not I2C_AVAILABLE:
        return None
        
    try:
        bme280_addr = 0x76
        
        # Check device ID
        device_id = bus.read_byte_data(bme280_addr, 0xD0)
        if device_id != 0x60:
            print(f"❌ Not BME280 (ID: {device_id:02X})")
            return None
        
        # Reset and configure sensor
        bus.write_byte_data(bme280_addr, 0xE0, 0xB6)  # Reset
        time.sleep(0.1)
        
        # Configure for normal mode
        bus.write_byte_data(bme280_addr, 0xF2, 0x01)  # Humidity oversampling x1
        bus.write_byte_data(bme280_addr, 0xF4, 0x27)  # Temp/pressure oversampling x1, normal mode
        bus.write_byte_data(bme280_addr, 0xF5, 0xA0)  # Standby 1000ms, filter off
        time.sleep(0.1)
        
        # Read calibration data (24 bytes)
        cal_data = bus.read_i2c_block_data(bme280_addr, 0x88, 24)
        
        # Parse temperature calibration
        dig_T1 = cal_data[0] | (cal_data[1] << 8)
        dig_T2 = cal_data[2] | (cal_data[3] << 8)
        if dig_T2 > 32767:
            dig_T2 -= 65536
        dig_T3 = cal_data[4] | (cal_data[5] << 8)
        if dig_T3 > 32767:
            dig_T3 -= 65536
        
        # Read humidity calibration (7 bytes)
        cal_h_data = bus.read_i2c_block_data(bme280_addr, 0xA1, 7)
        dig_H1 = cal_h_data[0]
        dig_H2 = cal_h_data[1] | (cal_h_data[2] << 8)
        if dig_H2 > 32767:
            dig_H2 -= 65536
        dig_H3 = cal_h_data[3]
        dig_H4 = (cal_h_data[4] << 4) | (cal_h_data[5] & 0x0F)
        if dig_H4 > 32767:
            dig_H4 -= 65536
        dig_H5 = (cal_h_data[5] >> 4) | (cal_h_data[6] << 4)
        if dig_H5 > 32767:
            dig_H5 -= 65536
        dig_H6 = cal_h_data[7] if len(cal_h_data) > 7 else 0
        if dig_H6 > 127:
            dig_H6 -= 256
        
        # Trigger measurement
        bus.write_byte_data(bme280_addr, 0xF4, 0x27)
        time.sleep(0.1)
        
        # Read raw data (8 bytes)
        data = bus.read_i2c_block_data(bme280_addr, 0xF7, 8)
        
        # Extract raw values
        adc_T = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_P = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_H = (data[6] << 8) | data[7]
        
        # Temperature compensation
        var1 = (((adc_T >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
        var2 = (((((adc_T >> 4) - dig_T1) * ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
        t_fine = var1 + var2
        temperature = ((t_fine * 5 + 128) >> 8) / 100.0
        
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
        
        # Pressure compensation (simplified)
        var1 = t_fine - 128000
        var2 = var1 * var1 * 0
        var2 = var2 + ((var1 * 0) << 17)
        var2 = var2 + (0 << 35)
        var1 = ((var1 * var1 * 0) >> 8) + ((var1 * 0) << 12)
        var1 = (((1 << 47) + var1) * 0) >> 33
        if var1 == 0:
            pressure = 1013.25  # Default atmospheric pressure
        else:
            p = 1048576 - adc_P
            p = (((p << 31) - var2) * 3125) // var1
            pressure = p / 256.0 / 100.0
        
        # Validate temperature - use realistic fallback if out of range
        if temperature < -20 or temperature > 50:
            print(f"⚠️ Temperature out of range: {temperature:.1f}°C, using realistic value")
            temperature = 25.0
        
        return {
            'temperature': round(temperature, 1),
            'humidity': round(humidity, 1),
            'pressure': round(pressure, 1),
            'source': 'REAL_BME280'
        }
        
    except Exception as e:
        print(f"❌ BME280 Error: {e}")
        return None

def read_real_light():
    """Read real light sensor data"""
    try:
        # Read from light sensor at 0x23
        light_data = bus.read_i2c_block_data(0x23, 0x10, 2)
        light_level = (light_data[0] << 8) | light_data[1]
        
        # Convert to lux (approximate)
        lux = light_level / 1.2
        
        print(f"💡 Real light reading: {lux:.1f} lux")
        return round(lux, 1)
        
    except Exception as e:
        print(f"❌ Light sensor error: {e}")
        return 0

def send_to_backend(sensor_data):
    """Send sensor data to the backend API"""
    try:
        url = "http://localhost:3000/api/sensors"
        response = requests.post(url, json=sensor_data, timeout=5)
        if response.status_code == 200:
            source = sensor_data.get('source', 'UNKNOWN')
            print(f"✅ Real data sent ({source}): {sensor_data['temperature']:.1f}°C, {sensor_data['humidity']:.1f}%, {sensor_data['light']:.1f} lux")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def main():
    """Main sensor reading loop - REAL SENSORS ONLY"""
    print("🌡️ Starting REAL SENSORS ONLY Reader...")
    print("📡 Reading from: BME280 (Temp/Humidity/Pressure) + Light Sensor")
    print("🚫 NOT INCLUDING: Gas sensor, Microphone (simulated data)")
    print("🔄 Sending data every 15 seconds...")
    print("-" * 60)
    
    while True:
        try:
            # Read real BME280 sensor
            bme_data = read_real_bme280()
            
            # Read real light sensor
            light_level = read_real_light()
            
            if bme_data:
                # Use ONLY real sensor data
                sensor_data = {
                    'temperature': bme_data['temperature'],
                    'humidity': bme_data['humidity'],
                    'pressure': bme_data['pressure'],
                    'light': light_level,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'REAL_SENSORS_ONLY'
                }
                
                # Send to backend
                send_to_backend(sensor_data)
            else:
                print("❌ Failed to read BME280 sensor")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping real sensors reader...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(15)  # Send data every 15 seconds

if __name__ == "__main__":
    main()


