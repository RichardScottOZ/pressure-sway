#!/usr/bin/env python3
"""
Barometric Pressure Monitor
Monitors BOM (Bureau of Meteorology) website for pressure drops.
Enhanced to use a configurable User-Agent, retries, and prefer BOM JSON feed.
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup


class PressureMonitor:
    """Monitor barometric pressure from BOM website."""

    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.session = requests.Session()
        self.session.headers.update(self._base_headers())

    def load_config(self, config_file: str) -> Dict[str, Any]:
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
        log_file = self.config.get('log_file', 'pressure_monitor.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def _base_headers(self) -> Dict[str, str]:
        ua = self.config.get(
            "user_agent",
            "pressure-sway-monitor/1.0 (+https://github.com/RichardScottOZ/pressure-sway)"
        )
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _json_endpoint(self) -> Optional[str]:
        if "json_url" in self.config and self.config["json_url"]:
            return self.config["json_url"]
        station_url = self.config.get("station_url")
        if not station_url:
            return None
        # Derive product/station from HTML URL pattern: /products/IDS60901/IDS60901.94648.shtml
        m = re.search(r'/products/([A-Z0-9]+)/([A-Z0-9]+\.\d+)\.shtml', station_url)
        if m:
            product_id = m.group(1)
            file_stub = m.group(2)
            return f"https://reg.bom.gov.au/fwo/{product_id}/{file_stub}.json"
        return None

    def fetch_pressure_data(self) -> Optional[Dict[str, Any]]:
        json_url = self._json_endpoint()
        if json_url:
            logging.info(f"Attempting JSON endpoint: {json_url}")
            data = self._fetch_json(json_url)
            if data:
                return data
            else:
                logging.warning("JSON fetch failed; falling back to HTML scrape.")
        html_url = self.config.get('station_url')
        if not html_url:
            logging.error("No station_url provided in config.")
            return None
        return self._fetch_html(html_url)

    def _request_with_retries(self, url: str, method: str = "GET",
                              max_attempts: int = 3, backoff_base: float = 2.0) -> Optional[requests.Response]:
        for attempt in range(1, max_attempts + 1):
            try:
                response = self.session.request(method, url, timeout=30)
                if response.status_code == 403:
                    logging.error(f"403 Forbidden on attempt {attempt}. Site may be blocking requests; "
                                  f"verify User-Agent or reduce frequency.")
                response.raise_for_status()
                return response
            except requests.HTTPError as e:
                status = getattr(e.response, "status_code", "unknown")
                logging.warning(f"HTTP error (status {status}) attempt {attempt}/{max_attempts}: {e}")
                if attempt < max_attempts:
                    sleep_for = backoff_base ** (attempt - 1)
                    logging.info(f"Retrying in {sleep_for:.1f}s...")
                    time.sleep(sleep_for)
            except requests.RequestException as e:
                logging.warning(f"Network error attempt {attempt}/{max_attempts}: {e}")
                if attempt < max_attempts:
                    sleep_for = backoff_base ** (attempt - 1)
                    logging.info(f"Retrying in {sleep_for:.1f}s...")
                    time.sleep(sleep_for)
        logging.error(f"Failed to retrieve {url} after {max_attempts} attempts.")
        return None

    def _fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        resp = self._request_with_retries(url)
        if not resp:
            return None
        try:
            j = resp.json()
        except ValueError as e:
            logging.error(f"JSON parse error: {e}")
            return None

        data_list = j.get("observations", {}).get("data", [])
        if not data_list:
            logging.error("JSON response lacks 'observations.data'")
            return None

        latest = data_list[-1]
        pressure_fields = ["press", "qnh", "mslp"]
        pressure_value = None
        for field in pressure_fields:
            if field in latest and isinstance(latest[field], (int, float)):
                pressure_value = float(latest[field])
                break

        if pressure_value is None:
            logging.error("No pressure field found in JSON (checked press/qnh/mslp).")
            return None

        observation_time = latest.get("local_date_time_full") or latest.get("local_date_time")
        result = {
            "pressure_hpa": pressure_value,
            "timestamp": datetime.now().isoformat(),
            "observation_time": observation_time or "Unknown(JSON)"
        }
        logging.info(f"Parsed pressure from JSON: {pressure_value} hPa")
        return result

    def _fetch_html(self, url: str) -> Optional[Dict[str, Any]]:
        logging.info(f"Fetching HTML station page: {url}")
        self.session.headers["Referer"] = url
        resp = self._request_with_retries(url)
        if not resp:
            return None

        soup = BeautifulSoup(resp.content, 'html.parser')
        table = soup.find('table')
        if not table:
            logging.error("Could not find observations table in HTML")
            return None

        pressure_value = None
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True).lower()
                if any(keyword in cell_text for keyword in ['pressure', 'qnh', 'mslp']):
                    if i + 1 < len(cells):
                        value_text = cells[i + 1].get_text(strip=True)
                        if value_text:
                            try:
                                parts = value_text.split()
                                if parts:
                                    pressure_value = float(parts[0])
                                    break
                            except (ValueError, IndexError):
                                continue
            if pressure_value:
                break

        if not pressure_value:
            text = soup.get_text()
            for line in text.splitlines():
                if 'pressure' in line.lower() or 'qnh' in line.lower():
                    match = re.search(r'(\d+\.?\d*)\s*hPa', line)
                    if match:
                        pressure_value = float(match.group(1))
                        break

        if not pressure_value:
            logging.error("Could not extract pressure value from HTML page")
            return None

        observation_time = None
        for meta in soup.find_all('p'):
            t = meta.get_text()
            if 'issued at' in t.lower() or 'observations' in t.lower():
                observation_time = t.strip()
                break

        result = {
            'pressure_hpa': pressure_value,
            'timestamp': datetime.now().isoformat(),
            'observation_time': observation_time or 'Unknown(HTML)'
        }
        logging.info(f"Successfully parsed pressure from HTML: {pressure_value} hPa")
        return result

    def load_last_reading(self) -> Optional[Dict[str, Any]]:
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
        data_file = self.config.get('data_file', 'pressure_data.json')
        try:
            with open(data_file, 'w') as f:
                json.dump(reading, f, indent=2)
        except IOError as e:
            logging.error(f"Error saving reading: {e}")

    def check_pressure_drop(self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]):
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
        logging.info("=" * 60)
        logging.info("Starting pressure check")

        current_reading = self.fetch_pressure_data()
        if not current_reading:
            logging.error("Failed to fetch current pressure data (no reading captured)")
            return

        previous_reading = self.load_last_reading()
        self.check_pressure_drop(current_reading, previous_reading)
        self.save_reading(current_reading)

        logging.info("Pressure check completed")
        logging.info("=" * 60)


def main():
    monitor = PressureMonitor()
    monitor.run()


if __name__ == "__main__":
    main()