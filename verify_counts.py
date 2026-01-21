import pandas as pd
import glob
import os

# Find the latest report
list_of_files = glob.glob('output_complexity_v4/*.xlsx')
latest_file = max(list_of_files, key=os.path.getctime)
print(f"Checking file: {latest_file}")

# Load the "Complexity_Metrics" tab
df = pd.read_excel(latest_file, sheet_name='Complexity_Metrics')

# Filter for test_patterns.html
row = df[df['Filename'] == 'test_patterns.html'].iloc[0]

print("--- Actual Counts ---")
print(f"Inline CSS: {row['Inline_CSS_Count']}")
print(f"Internal CSS: {row['Internal_CSS_Count']}")
print(f"Inline JS: {row['Inline_JS_Count']}")
print(f"Internal JS: {row['Internal_JS_Count']}")
print(f"AJAX Calls: {row['AJAX_Calls_Count']}")
print(f"Dynamic JS: {row['Dynamic_JS_Gen_Count']}")
print(f"Dynamic CSS: {row['Dynamic_CSS_Gen_Count']}")
print("---------------------")

expected = {
    'Inline_CSS_Count': 1,
    'Internal_CSS_Count': 2,
    'Inline_JS_Count': 2,
    'Internal_JS_Count': 5,
    'AJAX_Calls_Count': 8,
    'Dynamic_JS_Gen_Count': 8,
    'Dynamic_CSS_Gen_Count': 8
}

all_match = True
for key, val in expected.items():
    if row[key] != val:
        print(f"MISMATCH! {key}: Expected {val}, Got {row[key]}")
        all_match = False

if all_match:
    print("SUCCESS: All counts match expected values.")
else:
    print("FAILURE: Some counts do not match.")
