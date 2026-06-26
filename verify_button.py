import requests

BASE_URL = "http://localhost:8889"

# Fetch the HTML
response = requests.get(f"{BASE_URL}/")
html = response.text

# Check the structure of a column
import re

# Find the first column's structure
column_pattern = r'<div class="column">(.*?)</div>\s*</div>\s*</div>'
matches = re.findall(column_pattern, html, re.DOTALL)

if matches:
    first_column = matches[0]
    print("First column structure (abbreviated):")
    print("-" * 50)
    
    # Show the order of elements
    if '<div class="column-header">' in first_column:
        header_pos = first_column.find('<div class="column-header">')
        button_pos = first_column.find('class="add-card-btn"')
        
        print(f"✓ Column header found at position: {header_pos}")
        print(f"✓ Add card button found at position: {button_pos}")
        
        if button_pos > header_pos:
            print("\n✓ Button is AFTER the header (correct order)")
        else:
            print("\n✗ Button is BEFORE the header (wrong order)")
        
        # Count how many times the button appears
        button_count = first_column.count('class="add-card-btn"')
        print(f"\nButton appears {button_count} time(s) in this column")
    else:
        print("✗ Column header not found in first match")
        print("\nFirst 500 chars of column HTML:")
        print(first_column[:500])
else:
    print("✗ No columns found in HTML")
