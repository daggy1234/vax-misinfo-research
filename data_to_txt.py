import json
from collections import Counter

with open("videos.json", "r") as file:
    lines = file.readlines()

terms = []
for line in lines:
    data = json.loads(line.strip())
    if data["search_term"] == "anti-vaccination":
        lab = data["annotation"]["label"]
        # if int(data["statistics"].get("commentCount", 1)) > 0:
        if data["annotation"]["label"] != "irrelevant":
            print(data["annotation"]["label"])
            print(f'https://youtube.com/watch?v={data["id"]}')

print(Counter(terms).most_common())
