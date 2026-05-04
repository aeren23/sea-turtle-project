"""Quick dataset analysis script for understanding training data distribution."""
import json
import csv
import statistics
from pathlib import Path

data_root = Path(r"c:\Users\alihe\OneDrive\Masaüstü\sea-turtle-project\archiveu\turtles-data\data")

# Load annotations
with open(data_root / "annotations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== TOP-LEVEL KEYS ===")
print(list(data.keys()))

print("\n=== CATEGORIES ===")
for cat in data.get("categories", []):
    print(cat)

img_count = len(data.get("images", []))
print(f"\n=== IMAGES COUNT: {img_count} ===")
if data.get("images"):
    print("Sample image:", data["images"][0])

ann_count = len(data.get("annotations", []))
print(f"\n=== ANNOTATIONS COUNT: {ann_count} ===")
if data.get("annotations"):
    print("Sample annotation:", data["annotations"][0])

# Find head category id
head_cat_id = None
for cat in data.get("categories", []):
    if cat["name"] == "head":
        head_cat_id = cat["id"]
        break

print(f"\nHead category ID: {head_cat_id}")

# Check orientation distribution
orientations = {}
head_count = 0
for ann in data.get("annotations", []):
    if ann.get("category_id") == head_cat_id:
        head_count += 1
        attrs = ann.get("attributes", {})
        orient = attrs.get("orientation", "unknown")
        orientations[orient] = orientations.get(orient, 0) + 1

print(f"\n=== HEAD ANNOTATIONS: {head_count} ===")
print("Orientation distribution:", orientations)

# Check identity distribution from metadata
identities = {}
splits = {}
with open(data_root / "metadata_splits.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cols = None
    for row in reader:
        if cols is None:
            cols = list(row.keys())
        ident = row["identity"]
        split = row.get("split_closed", "unknown")
        identities[ident] = identities.get(ident, 0) + 1
        splits[split] = splits.get(split, 0) + 1

print(f"\n=== CSV COLUMNS: {cols} ===")
print(f"\n=== UNIQUE IDENTITIES (from metadata): {len(identities)} ===")
print(f"Split distribution: {splits}")

# Images per identity stats
counts = list(identities.values())
print(f"Min images/identity: {min(counts)}")
print(f"Max images/identity: {max(counts)}")
print(f"Mean images/identity: {statistics.mean(counts):.1f}")
print(f"Median images/identity: {statistics.median(counts):.1f}")

# Critical for MPerClassSampler m=4
few_shot_4 = sum(1 for c in counts if c < 4)
few_shot_2 = sum(1 for c in counts if c < 2)
print(f"Identities with < 4 images: {few_shot_4} / {len(identities)}")
print(f"Identities with < 2 images: {few_shot_2} / {len(identities)}")

# Now simulate what the parser actually produces (with virtual identities)
print("\n\n=== VIRTUAL IDENTITY ANALYSIS (orientation-based) ===")
# Map image_id to file_name
images_dict = {}
for img in data.get("images", []):
    images_dict[img["id"]] = img["file_name"]

# Build virtual identities
virtual_ids = {}
train_virtual_ids = {}
valid_virtual_ids = {}

meta_dict = {}
with open(data_root / "metadata_splits.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        meta_dict[row["file_name"]] = row

for ann in data.get("annotations", []):
    if ann.get("category_id") != head_cat_id:
        continue
    image_id = ann["image_id"]
    file_name = images_dict.get(image_id)
    if not file_name or file_name not in meta_dict:
        continue
    
    meta = meta_dict[file_name]
    orient = ann.get("attributes", {}).get("orientation", "unknown")
    vid = f"{meta['identity']}_{orient}"
    split = meta.get("split_closed", "unknown")
    
    virtual_ids[vid] = virtual_ids.get(vid, 0) + 1
    if split == "train":
        train_virtual_ids[vid] = train_virtual_ids.get(vid, 0) + 1
    elif split == "valid":
        valid_virtual_ids[vid] = valid_virtual_ids.get(vid, 0) + 1

print(f"Total virtual identities: {len(virtual_ids)}")
print(f"Train virtual identities: {len(train_virtual_ids)}")
print(f"Valid virtual identities: {len(valid_virtual_ids)}")

train_counts = list(train_virtual_ids.values())
if train_counts:
    print(f"\nTRAIN stats:")
    print(f"  Min images/vid: {min(train_counts)}")
    print(f"  Max images/vid: {max(train_counts)}")
    print(f"  Mean: {statistics.mean(train_counts):.1f}")
    print(f"  Median: {statistics.median(train_counts):.1f}")
    print(f"  Total train samples: {sum(train_counts)}")
    few4 = sum(1 for c in train_counts if c < 4)
    few2 = sum(1 for c in train_counts if c < 2)
    print(f"  VIDs with < 4 images: {few4} / {len(train_virtual_ids)} ({100*few4/len(train_virtual_ids):.1f}%)")
    print(f"  VIDs with < 2 images: {few2} / {len(train_virtual_ids)} ({100*few2/len(train_virtual_ids):.1f}%)")
    print(f"  VIDs with == 1 image: {sum(1 for c in train_counts if c == 1)}")

valid_counts = list(valid_virtual_ids.values())
if valid_counts:
    print(f"\nVALID stats:")
    print(f"  Min images/vid: {min(valid_counts)}")
    print(f"  Max images/vid: {max(valid_counts)}")
    print(f"  Mean: {statistics.mean(valid_counts):.1f}")
    print(f"  Median: {statistics.median(valid_counts):.1f}")
    print(f"  Total valid samples: {sum(valid_counts)}")

# Check overlap between train and valid virtual IDs
overlap = set(train_virtual_ids.keys()) & set(valid_virtual_ids.keys())
print(f"\nVirtual IDs in BOTH train and valid: {len(overlap)}")
print(f"Virtual IDs ONLY in valid (unseen): {len(set(valid_virtual_ids.keys()) - set(train_virtual_ids.keys()))}")
