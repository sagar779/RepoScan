import pandas as pd

df = pd.read_excel('output/Application_Depth_Tracker_20260122_113558.xlsx', sheet_name='Complexity_Metrics')
ajax_files = df[df['AJAX_Calls_Count'] > 0]

print("Files with AJAX calls:")
print("="*70)
for idx, row in ajax_files.iterrows():
    print(f"{row['Filename']}: {row['AJAX_Calls_Count']} calls")

print(f"\nTotal AJAX calls: {ajax_files['AJAX_Calls_Count'].sum()}")
