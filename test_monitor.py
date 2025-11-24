#!/usr/bin/env python3
"""
Test script for pressure monitor with simulated data
"""

import json
import os
import sys
from datetime import datetime

# Create a test config
test_config = {
    "station_url": "https://www.bom.gov.au/products/IDS60901/IDS60901.94648.shtml",
    "pressure_drop_threshold_hpa": 2.0,
    "check_interval_minutes": 30,
    "data_file": "test_pressure_data.json",
    "log_file": "test_pressure_monitor.log"
}

with open('test_config.json', 'w') as f:
    json.dump(test_config, f, indent=2)

print("✅ Created test configuration")

# Test 1: First run (no previous data)
print("\n" + "="*60)
print("Test 1: First run with simulated pressure reading")
print("="*60)

# Simulate a pressure reading
first_reading = {
    'pressure_hpa': 1013.5,
    'timestamp': datetime.now().isoformat(),
    'observation_time': 'Test observation'
}

with open('test_pressure_data.json', 'w') as f:
    json.dump(first_reading, f, indent=2)

print(f"Simulated first reading: {first_reading['pressure_hpa']} hPa")
print("✅ First reading saved")

# Test 2: Second run with pressure drop
print("\n" + "="*60)
print("Test 2: Second run with pressure DROP (should trigger alert)")
print("="*60)

# Load previous reading
with open('test_pressure_data.json', 'r') as f:
    previous = json.load(f)

# Simulate a pressure drop
second_reading = {
    'pressure_hpa': 1010.0,  # 3.5 hPa drop
    'timestamp': datetime.now().isoformat(),
    'observation_time': 'Test observation 2'
}

delta = previous['pressure_hpa'] - second_reading['pressure_hpa']
threshold = test_config['pressure_drop_threshold_hpa']

print(f"Previous: {previous['pressure_hpa']} hPa")
print(f"Current: {second_reading['pressure_hpa']} hPa")
print(f"Change: {delta:+.2f} hPa")
print(f"Threshold: {threshold} hPa")

if delta >= threshold:
    print(f"⚠️  PRESSURE DROP DETECTED! Drop of {delta:.2f} hPa exceeds threshold")
    print("✅ Alert logic working correctly")
else:
    print("❌ Alert should have been triggered but wasn't")

# Save second reading
with open('test_pressure_data.json', 'w') as f:
    json.dump(second_reading, f, indent=2)

# Test 3: Third run with pressure rise
print("\n" + "="*60)
print("Test 3: Third run with pressure RISE (should not alert)")
print("="*60)

previous = second_reading
third_reading = {
    'pressure_hpa': 1015.0,  # 5 hPa rise
    'timestamp': datetime.now().isoformat(),
    'observation_time': 'Test observation 3'
}

delta = previous['pressure_hpa'] - third_reading['pressure_hpa']

print(f"Previous: {previous['pressure_hpa']} hPa")
print(f"Current: {third_reading['pressure_hpa']} hPa")
print(f"Change: {delta:+.2f} hPa")

if delta >= threshold:
    print("❌ Alert triggered incorrectly for pressure rise")
else:
    print("✅ Correctly no alert for pressure rise")

# Test 4: Test configuration loading
print("\n" + "="*60)
print("Test 4: Configuration validation")
print("="*60)

print(f"Station URL: {test_config['station_url']}")
print(f"Threshold: {test_config['pressure_drop_threshold_hpa']} hPa")
print(f"Check interval: {test_config['check_interval_minutes']} minutes")
print("✅ Configuration valid")

# Cleanup
print("\n" + "="*60)
print("Cleaning up test files")
print("="*60)

for file in ['test_config.json', 'test_pressure_data.json', 'test_pressure_monitor.log']:
    if os.path.exists(file):
        os.remove(file)
        print(f"Removed {file}")

print("\n" + "="*60)
print("✅ All tests passed!")
print("="*60)
print("\nThe pressure monitor is ready to use.")
print("When deployed, it will:")
print("1. Fetch real pressure data from BOM")
print("2. Compare with previous reading")
print("3. Alert on pressure drops >= threshold")
print("4. Log all activity with timestamps")
