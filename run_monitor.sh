#!/bin/bash
# Continuous pressure monitoring script
# Runs the pressure monitor in a loop with configurable interval

# Default interval: 30 minutes (1800 seconds)
INTERVAL=${CHECK_INTERVAL:-1800}

echo "Starting pressure monitor (checking every ${INTERVAL} seconds)"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    echo "=========================================="
    echo "Running pressure check at $(date)"
    echo "=========================================="
    
    python pressure_monitor.py
    
    echo ""
    echo "Next check in ${INTERVAL} seconds ($(($INTERVAL / 60)) minutes)"
    echo ""
    
    sleep $INTERVAL
done
