import pandas as pd

df = pd.read_csv("fgcoop-security.csv")
df.to_excel("FGCOOP-Security.xlsx", index=False)
print("Saved: FGCOOP-Security.xlsx")