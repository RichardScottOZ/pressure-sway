#!/usr/bin/env python3
"""
Barometric Pressure Monitor
Monitors BOM (Bureau of Meteorology) website for pressure drops
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup


class PressureMonitor:
    """Monitor barometric pressure from BOM website."""

    def __init__(self, config_file: str = "config.json"):
        """Initialize the pressure monitor with configuration."""
        self.config = self.load_config(config_file)
        self.setup_logging()
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file {config_file} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing config file: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Set up logging to file and console."""
        log_file = self.config.get('log_file', 'pressure_monitor.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def fetch_pressure_data(self) -> Optional[Dict[str, Any]]:
        """Fetch and parse pressure data from BOM website."""
        url = self.config['station_url']
        
        try:
            logging.info(f"Fetching data from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the observations table
            # BOM pages typically have a table with class or id containing observation data
            table = soup.find('table')
            
            if not table:
                logging.error("Could not find observations table in HTML")
                return None
            
            # Parse the table to find pressure data
            # Look for rows containing pressure information
            pressure_value = None
            observation_time = None
            
            rows = table.find_all('tr')
            
            # Try to find pressure in table rows
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True).lower()
                    
                    # Look for pressure-related keywords
                    if any(keyword in cell_text for keyword in ['pressure', 'qnh', 'mslp']):
                        # Try to get value from next cell or same row
                        if i + 1 < len(cells):
                            value_text = cells[i + 1].get_text(strip=True)
                            try:
                                # Extract numeric value
                                pressure_value = float(value_text.split()[0])
                                break
                            except (ValueError, IndexError):
                                continue
                
                if pressure_value:
                    break
            
            # Alternative: look for specific patterns in the HTML
            if not pressure_value:
                # Try finding by looking for text patterns
                text = soup.get_text()
                lines = text.split('\n')
                for line in lines:
                    if 'pressure' in line.lower() or 'qnh' in line.lower():
                        # Try to extract number followed by hPa
                        import re
                        match = re.search(r'(\d+\.?\d*)\s*hPa', line)
                        if match:
                            pressure_value = float(match.group(1))
                            break
            
            if not pressure_value:
                logging.error("Could not extract pressure value from page")
                return None
            
            # Try to find observation time
            for meta in soup.find_all('p'):
                text = meta.get_text()
                if 'issued at' in text.lower() or 'observations' in text.lower():
                    observation_time = text.strip()
                    break
            
            result = {
                'pressure_hpa': pressure_value,
                'timestamp': datetime.now().isoformat(),
                'observation_time': observation_time or 'Unknown'
            }
            
            logging.info(f"Successfully parsed pressure: {pressure_value} hPa")
            return result
            
        except requests.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error parsing data: {e}")
            return None
    
    def load_last_reading(self) -> Optional[Dict[str, Any]]:
        """Load the last pressure reading from file."""
        data_file = self.config.get('data_file', 'pressure_data.json')
        
        if not os.path.exists(data_file):
            return None
        
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Error reading last reading: {e}")
            return None
    
    def save_reading(self, reading: Dict[str, Any]):
        """Save the current reading to file."""
        data_file = self.config.get('data_file', 'pressure_data.json')
        
        try:
            with open(data_file, 'w') as f:
                json.dump(reading, f, indent=2)
        except IOError as e:
            logging.error(f"Error saving reading: {e}")
    
    def check_pressure_drop(self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]):
        """Check if pressure has dropped significantly and log it."""
        if not previous:
            logging.info("No previous reading available for comparison")
            return
        
        current_pressure = current['pressure_hpa']
        previous_pressure = previous['pressure_hpa']
        delta = previous_pressure - current_pressure
        threshold = self.config.get('pressure_drop_threshold_hpa', 2.0)
        
        logging.info(f"Pressure change: {delta:+.2f} hPa (Previous: {previous_pressure}, Current: {current_pressure})")
        
        if delta >= threshold:
            logging.warning(
                f"⚠️  PRESSURE DROP DETECTED! ⚠️\n"
                f"  Previous: {previous_pressure} hPa at {previous.get('timestamp')}\n"
                f"  Current:  {current_pressure} hPa at {current.get('timestamp')}\n"
                f"  Drop:     {delta:.2f} hPa (threshold: {threshold} hPa)\n"
                f"  This may indicate approaching weather change."
            )
        elif delta <= -threshold:
            logging.info(
                f"ℹ️  Pressure rise detected: {abs(delta):.2f} hPa "
                f"(Previous: {previous_pressure}, Current: {current_pressure})"
            )
    
    def run(self):
        """Run a single check cycle."""
        logging.info("=" * 60)
        logging.info("Starting pressure check")
        
        # Fetch current data
        current_reading = self.fetch_pressure_data()
        
        if not current_reading:
            logging.error("Failed to fetch current pressure data")
            return
        
        # Load previous reading
        previous_reading = self.load_last_reading()
        
        # Check for pressure drop
        self.check_pressure_drop(current_reading, previous_reading)
        
        # Save current reading for next comparison
        self.save_reading(current_reading)
        
        logging.info("Pressure check completed")
        logging.info("=" * 60)


def main():
    """Main entry point."""
    monitor = PressureMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
