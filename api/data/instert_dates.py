import random
from datetime import date, timedelta
from api.models import Contract

# Calculate date range
today = date.today()
start_date = today - timedelta(days=90)         # 3 months ago
end_date = today + timedelta(days=2*365)        # 2 years from now

contracts = Contract.objects.all()
for contract in contracts:
    # Pick a random number of days between start_date and end_date
    delta_days = (end_date - start_date).days
    random_days = random.randint(0, delta_days)
    contract.end_date = start_date + timedelta(days=random_days)
    contract.save()

print(f"Updated {contracts.count()} contracts with random end dates.")