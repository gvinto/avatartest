import glob
import json

item_list = []

for filepath in glob.glob("img/*.png"):
    
    filename = filepath.split('\\')[1]
    item_id = filename.split('.')[0]

    item_type = item_id.split('_')[0]

    # print(item_id, item_type, filename)

    item_list.append({'item_id':item_id, 
                      'item_type':item_type, 
                      'item_description': 'Description_text',
                      'item_thumbnail':'http://ds1p0td0v622j.cloudfront.net/thumbnails/'+filename})

print(item_list)

json_object = json.dumps(item_list, indent=4)
 
# Writing to sample.json
with open("items_db.json", "w") as outfile:
    outfile.write(json_object)