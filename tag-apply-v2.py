import boto3
import pandas as pd
from pathlib import Path

# =============================
# CONFIGURATION
# =============================
DRY_RUN = True  # Set to False to apply tags
INPUT_FILE = "tags.xlsx"
PROCESSED_FILE = Path("processed_arns.txt")

# Columns that are NOT tags (metadata)
NON_TAG_COLUMNS = {
    "Identifier",
    "ARN",
    "Resource type",
    "Region",
    "Service"
}

# =============================
# LOAD DATA
# =============================
df = pd.read_excel(INPUT_FILE)
df.columns = [c.strip() for c in df.columns]

if "ARN" not in df.columns:
    raise Exception("ARN column not found in XLSX")

# =============================
# LOAD PROCESSED ARNs (RESUME)
# =============================
processed_arns = set()
if PROCESSED_FILE.exists():
    processed_arns = set(PROCESSED_FILE.read_text().splitlines())

clients = {}

# =============================
# HELPERS
# =============================
def get_region_from_arn(arn: str) -> str:
    # arn:partition:service:region:account-id:resource
    region = arn.split(":")[3]
    return region if region else "us-east-1"

def normalize_tag_key(col_name: str) -> str:
    """
    Converts:
      'Tag: env' -> 'env'
      'env'      -> 'env'
    """
    return col_name.replace("Tag:", "").strip()

# =============================
# MAIN LOOP
# =============================
for _, row in df.iterrows():

    arn = row.get("ARN")
    if pd.isna(arn):
        continue

    # ✅ Resume support
    if arn in processed_arns:
        print(f"Skipping already processed: {arn}")
        continue

    try:
        region = get_region_from_arn(arn)

        if region not in clients:
            clients[region] = boto3.client(
                "resourcegroupstaggingapi",
                region_name=region
            )

        client = clients[region]
        tags = {}

        for col in df.columns:

            # Skip metadata columns
            if col in NON_TAG_COLUMNS:
                continue

            value = row[col]

            # Skip empty or placeholder values
            if pd.isna(value) or str(value).strip() == "(not tagged)":
                continue

            tag_key = normalize_tag_key(col)

            # Skip AWS system tags
            if tag_key.startswith("aws:"):
                continue

            tags[tag_key] = str(value)

        if not tags:
            print(f"No tags to apply: {arn}")
            processed_arns.add(arn)
            PROCESSED_FILE.write_text("\n".join(processed_arns))
            continue

        print(f"\nRegion: {region}")
        print(f"Resource: {arn}")
        print(f"Tags: {tags}")

        if not DRY_RUN:
            client.tag_resources(
                ResourceARNList=[arn],
                Tags=tags
            )

        # ✅ Mark as processed
        processed_arns.add(arn)
        PROCESSED_FILE.write_text("\n".join(processed_arns))

    except Exception as e:
        print(f"ERROR tagging {arn}: {e}")
        continue

print("\nDone.")