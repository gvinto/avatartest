import json, csv, glob, pathlib

COL_INITIATIVE = 0
COL_TASK = 1
COL_ITEMS = 6
COL_POINTS = 8
COL_LIMIT = 9

def clean(text:str):
    return text.replace("â€‹","").strip()

def all_color_variations(item_id:str) -> list:
    item_base_name = item_id[:item_id.rfind('_')]
    variation_files = glob.glob(f'img/{item_base_name}*')
    variation_items = [pathlib.PurePath(file).stem for file in variation_files]
    return variation_items

def main():
    # Item DB to verify starter item_ids are valid
    db_items = []
    with open("items_db.json", "r") as infile:
        items_db = json.load(infile)

    for item in items_db:
        db_items.append(item['item_id'])

    # print(f"{db_items=}")

    task_rewards = []
    invalid_items = []

    # Extract all starter item_ids
    with open("Taskboard_withWearables.csv", "r") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            # print(clean(row[COL_INITIATIVE]),clean(row[COL_TASK]),clean(row[COL_ITEMS]),clean(row[COL_POINTS]),clean(row[COL_LIMIT]))
            if "Initiative" in row[COL_INITIATIVE] or "Adhoc" in row[COL_INITIATIVE] or row[COL_INITIATIVE].startswith("â€‹") or "Varies" in row[COL_POINTS]:
                continue

            #extract list of items
            item_ids = clean(row[COL_ITEMS]).split('\n')
            COLOR_VARIATION_PLACEHOLDER = '<plus all the other colours>'
            if COLOR_VARIATION_PLACEHOLDER in item_ids:
                color_item = item_ids[item_ids.index(COLOR_VARIATION_PLACEHOLDER)-1]
                item_ids.remove(COLOR_VARIATION_PLACEHOLDER)
                item_ids.extend(all_color_variations(color_item))

            for item in item_ids:
                if not item:
                    item_ids.remove(item)
                elif item not in db_items:
                    invalid_items.append(item)
                    item_ids.remove(item)

            task = {
                    "category": clean(row[COL_INITIATIVE]),
                    "task": clean(row[COL_TASK]),
                    "points": {
                        "datadex_2023": int(clean(row[COL_POINTS]))
                    },
                    "limit": int(clean(row[COL_LIMIT])),
                    "items": item_ids
                }
            
            task_rewards.append(task)

    # print(task_rewards)
    task_rewards_json_object = json.dumps(task_rewards, indent=4)
    
    with open("task_rewards.json", "w") as outfile:
        outfile.write(task_rewards_json_object)

    invalid_items.sort()

    print(f"{invalid_items=}")

if __name__ == '__main__':
    main()