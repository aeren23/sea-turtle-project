import json
import pandas as pd

# Load files
with open('archiveu/turtles-data/data/annotations.json', 'r') as f:
    data = json.load(f)

anns = pd.DataFrame(data['annotations'])
imgs = pd.DataFrame(data['images'])
meta = pd.read_csv('archiveu/turtles-data/data/metadata_splits.csv')

# Merge
df = anns.merge(imgs, left_on='image_id', right_on='id', suffixes=('', '_img'))
# Ensure file_name is consistent
df = df.merge(meta, on='file_name', suffixes=('', '_meta'))

# Extract orientation
df['orientation'] = df['attributes'].apply(lambda x: x.get('orientation') if isinstance(x, dict) else None)

# Check for 'virtual identity' matches between train and valid
df['virtual_id'] = df['identity'] + "_" + df['orientation'].fillna('None')

print("Split counts:")
print(df['split_closed'].value_counts())

train_df = df[df['split_closed'] == 'train']
valid_df = df[df['split_closed'] == 'valid']

train_vids = set(train_df['virtual_id'])
valid_vids = set(valid_df['virtual_id'])

matches = train_vids.intersection(valid_vids)
print(f"\nUnique Virtual IDs in Train: {len(train_vids)}")
print(f"Unique Virtual IDs in Valid: {len(valid_vids)}")
print(f"Virtual IDs present in BOTH (Matches): {len(matches)}")

if len(valid_vids) > 0:
    print(f"Percentage of Valid Virtual IDs present in Train: {len(matches)/len(valid_vids)*100:.2f}%")

# Check distribution of orientations
print("\nOrientation distribution:")
print(df.groupby(['split_closed', 'orientation']).size())
