import glob
import json, yaml, csv
import requests
import logging as logger
from util.auth_util import gen_jwt_token

from config import URL_GPT_API

logger.basicConfig(level=logger.INFO)

def generate_item_names(session, item_ids):
    # Generate JWT which contains user's permissions
    jwt_data = {
        'email': 'gen_items_db@tech.gov.sg',
        'role': 'public',
        'permissions': [],
        'name': 'gen_items_db'
    }
    jwt_token = gen_jwt_token(jwt_data)
    headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {jwt_token}"}

    prompt = f"""generate a short and unique item name 3 words maximum for the following in game item_ids and return them in the JSON format: \n\n{{"item_id_1":"item name 1","item_id_2":"item name 2"}}\n\n --- \n\n {str(item_ids)}"""
    data = {'prompt': prompt}

    logger.info(f'Calling GPT prompt for: {prompt}')
    resp = session.post(f'{URL_GPT_API}/prompt', json=data, headers=headers)
    logger.info(f'{resp=}')

    try:
        response_json = resp.json()
    except:
        response_json = yaml.load(resp)

    logger.info(f"response: {response_json.get('response')}")
    return {'response':response_json.get('response')}

def generate_item_descriptions(session, item_ids):
    # Generate JWT which contains user's permissions
    jwt_data = {
        'email': 'gen_items_db@tech.gov.sg',
        'role': 'public',
        'permissions': [],
        'name': 'gen_items_db'
    }
    jwt_token = gen_jwt_token(jwt_data)
    headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {jwt_token}"}

    prompt = f"""generate a short, witty and unique item description of around 10 words for the following in game item_ids and return them in the JSON format: \n\n{{"item_id_1":"item description 1","item_id_2":"item description 2"}}\n\n --- \n\n {str(item_ids)}"""
    data = {'prompt': prompt}

    logger.info(f'Calling GPT prompt for: {prompt}')
    resp = session.post(f'{URL_GPT_API}/prompt', json=data, headers=headers)
    logger.info(f'{resp=}')

    try:
        response_json = resp.json()
    except:
        response_json = yaml.load(resp)

    logger.info(f"response: {response_json.get('response')}")
    return {'response':response_json.get('response')}

def main():
    items_db = []

    all_img_files = glob.glob("img/*.png")

    item_names = dict()
    with open("item_names.json", "r") as name_file:
        item_names = json.load(name_file)

    item_descriptions = dict()
    with open("item_descriptions.json", "r") as desc_file:
        item_descriptions = json.load(desc_file)

    session = requests.Session()

    names_to_generate = []
    descriptions_to_generate = []
    item_ids = []
    for filepath in all_img_files:
        
        filename = filepath.split('\\')[1]
        item_id = filename.split('.')[0]
        item_type = item_id.split('_')[0]

        item_ids.append([item_id])

        if item_id not in item_names or not item_names[item_id] or item_names[item_id] == "Description_text":
            # collect all into a list for batch generation
            names_to_generate.append(item_id)

        if item_id not in item_descriptions or not item_descriptions[item_id] or item_descriptions[item_id] == "Description_text":
            # collect all into a list for batch generation
            descriptions_to_generate.append(item_id)

    with open('item_ids.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write multiple rows
        writer.writerows(item_ids)

    batch_size = 50

    for i in range(0, len(names_to_generate), batch_size):
        # generate in batches and put into dict
        items_batch = names_to_generate[i:i+batch_size]
        response = generate_item_names(session, items_batch)
        #process response
        response_txt = response.get('response')
        response_txt = response_txt[response_txt.index("{"):]
        response_txt = response_txt.replace('<|im_sep|>','')
        # response_txt = response_txt.replace('\'','"')
        items_response = json.loads(response_txt)
        item_names.update(items_response)

        item_names_json_object = json.dumps(item_names, indent=4)
        with open("item_names.json", "w") as outfile:
            outfile.write(item_names_json_object)

    for i in range(0, len(descriptions_to_generate), batch_size):
        # generate in batches and put into dict
        items_batch = descriptions_to_generate[i:i+batch_size]
        response = generate_item_descriptions(session, items_batch)
        #process response
        response_txt = response.get('response')
        response_txt = response_txt[response_txt.index("{"):]
        response_txt = response_txt.replace('<|im_sep|>','')
        # response_txt = response_txt.replace('\'','"')
        items_response = json.loads(response_txt)
        item_descriptions.update(items_response)

        items_description_json_object = json.dumps(item_descriptions, indent=4)
        with open("item_descriptions.json", "w") as outfile:
            outfile.write(items_description_json_object)
        
    for filepath in all_img_files:
        
        filename = filepath.split('\\')[1]
        item_id = filename.split('.')[0]

        item_type = item_id.split('_')[0]
        
        # print(item_id, item_type, filename)
        items_db.append({'item_id':item_id, 
                        'item_type':item_type, 
                        'item_name': item_names[item_id],
                        'item_description': item_descriptions[item_id],
                        'item_thumbnail':'http://ds1p0td0v622j.cloudfront.net/thumbnails/'+filename})
        
        # item_descriptions[item_id] = 'Description_text'

    print(items_db)

    items_db_json_object = json.dumps(items_db, indent=4)
    
    with open("items_db.json", "w") as outfile:
        outfile.write(items_db_json_object)



if __name__ == '__main__':
    main()
    # session = requests.Session()
    # item_ids = ['addon_001_belt_black'] #,'addon_001_belt_green','addon_001_belt_pink'


    # print(generate_item_names(session,item_ids))