import pandas as pd
from engine import diagnose_transaction

df = pd.read_csv("data/transactions.csv")

for _, transaction in df.iterrows():

    result = diagnose_transaction(transaction)

    print("\n----------------------------")
    print("Transaction:", transaction["transaction_id"])
    print("Scenario:", transaction["scenario"])
    print("Status:", result["status"])
    print("Diagnosis:", result["diagnosis"])
    print("Action:", result["action"])
    print("Severity:", result["severity"])