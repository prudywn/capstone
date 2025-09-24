#!/bin/bash

# Pretty print for both Nairobi and Mombasa data from Cassandra
echo "🌍 Air Quality Data from Cassandra (Both Cities)"
echo "============================================================"

docker exec cassandra cqlsh -e "USE air_quality_keyspace; SELECT city, date, hour, pm2_5, pm10, ozone, carbon_monoxide, nitrogen_dioxide FROM air_quality_by_city_date;" | python3 -c "
import sys
import re

lines = sys.stdin.readlines()
record_count = 0

for i, line in enumerate(lines):
    line = line.strip()
    
    # Skip header lines and separators
    if not line or '---' in line or 'city |' in line or 'rows)' in line or line.startswith('('):
        continue
    
    # Parse data lines
    if '|' in line and not line.startswith('('):
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 8:
            # Skip if this looks like a header row
            if parts[0] == 'city' or parts[1] == 'date':
                continue
                
            record_count += 1
            city_emoji = '🏙️' if parts[0] == 'Nairobi' else '🏖️'
            print(f'\\n{city_emoji} Record #{record_count} - {parts[0]}')
            print(f'   📅 Date: {parts[1]}')
            print(f'   🕐 Hour: {parts[2]}')
            print('   📊 Pollutants:')
            
            # Format each pollutant
            pollutants = [
                ('PM2.5', parts[3]),
                ('PM10', parts[4]),
                ('Ozone', parts[5]),
                ('Carbon Monoxide', parts[6]),
                ('Nitrogen Dioxide', parts[7])
            ]
            
            for name, value in pollutants:
                if value and value != 'null':
                    print(f'      • {name}: {value}')
                else:
                    print(f'      • {name}: N/A')
            
            print('-' * 40)

if record_count == 0:
    print('📭 No data found in Cassandra')
else:
    print(f'\\n✅ Displayed {record_count} records from Cassandra')
    print('\\n🏙️ = Nairobi | 🏖️ = Mombasa')
"
