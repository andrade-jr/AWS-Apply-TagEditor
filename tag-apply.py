#Requeriments - install boto3 pandas openpyxl

import boto3
import pandas as pd

DRY_RUN = True  # change to False when ready

df = pd.read_excel("tags.xlsx")
df.columns = [c.strip() for c in df.columns]

if "ARN" not in df.columns:
    raise Exception("ARN column not found in XLSX")

clients = {}  # cache clients per region


def get_region_from_arn(arn: str) -> str:
    # arn:partition:service:region:account-id:resource
    region = arn.split(":")[3]
    return region if region else "us-east-1"

for _, row in df.iterrows():
    arn = row["ARN"]

    if pd.isna(arn):
        continue

    region = get_region_from_arn(arn)

    if region not in clients:
        clients[region] = boto3.client(
            "resourcegroupstaggingapi",
            region_name=region
        )

    client = clients[region]
    tags = {}

    for col in df.columns:
        if not col.startswith("Tag: "):
            continue

        tag_key = col.replace("Tag: ", "").strip()
        value = row[col]

        # Skip AWS system tags
        if tag_key.startswith("aws:"):
            continue

        # Skip empty / not tagged placeholders
        if pd.isna(value) or str(value).strip() == "(not tagged)":
            continue

        tags[tag_key] = str(value)

    if not tags:
        continue

    print(f"\nRegion: {region}")
    print(f"Resource: {arn}")
    print(f"Tags: {tags}")

    if not DRY_RUN:
        client.tag_resources(
            ResourceARNList=[arn],
            Tags=tags
        )

print("\nDone.")