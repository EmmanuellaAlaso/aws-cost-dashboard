import boto3
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt

print("Fetching AWS cost data...")

client = boto3.client('ce')

# Define date range (last 7 days)
end = date.today()
start = end - timedelta(days=7)

response = client.get_cost_and_usage(
    TimePeriod={
        'Start': start.strftime('%Y-%m-%d'),
        'End': end.strftime('%Y-%m-%d')
    },
    Granularity='DAILY',
    Metrics=['UnblendedCost'],
    GroupBy=[
        {'Type': 'DIMENSION', 'Key': 'SERVICE'}
    ]
)

# Process data
rows = []
for result in response['ResultsByTime']:
    for group in result['Groups']:
        rows.append({
            'Date': result['TimePeriod']['Start'],
            'Service': group['Keys'][0],
            'Cost ($)': float(group['Metrics']['UnblendedCost']['Amount'])
        })

df = pd.DataFrame(rows)
print(df)

# Plot chart
if df.empty:
    print("⚠️ No cost data found.")
else:
    df_pivot = df.pivot_table(index='Date', columns='Service', values='Cost ($)', aggfunc='sum').fillna(0)
    df_pivot.plot(kind='line', marker='o', figsize=(10,6))

    plt.title('AWS Daily Cost by Service (Last 7 Days)')
    plt.ylabel('Cost ($)')
    plt.xlabel('Date')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('aws_cost_chart.png')
    plt.show()
    print("✅ Chart saved as aws_cost_chart.png")
