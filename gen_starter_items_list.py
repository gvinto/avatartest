import json, csv

def main():
    # Item DB to verify starter item_ids are valid
    db_items = []
    with open("items_db.json", "r") as infile:
        items_db = json.load(infile)

    for item in items_db:
        db_items.append(item['item_id'])

    # print(f"{db_items=}")

    starter_items = []
    invalid_items = []

    # Extract all starter item_ids
    with open("Default_Wearables.csv", "r") as csvfile:
        csv_reader = csv.reader(csvfile)

        for row in csv_reader:
            for col in row:
                if col and "_" in col:
                    item_id = col.strip(" \n\t")
                    if item_id in db_items: 
                        starter_items.append(item_id)
                    else:
                        invalid_items.append(item_id)
                        

    #remove dupes (if any)
    starter_items = list(set(starter_items))

    # sort by item_id
    invalid_items.sort()
    starter_items.sort()

    print(f"{invalid_items=}")
    print(f"{starter_items=}")
    print(len(starter_items))



if __name__ == '__main__':
    main()