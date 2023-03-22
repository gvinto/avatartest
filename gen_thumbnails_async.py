from PIL import Image
import glob, time
import asyncio
import concurrent.futures

MARGIN = 10
THUMBNAIL_SIZE = 48

def generate_thumbnail(base_img_copy, item_id: str) -> Image:

    base_img = base_img_copy

    item_img = Image.open(f"img/{item_id}.png")
    item_bbox = item_img.getbbox()

    item_width = item_bbox[2] - item_bbox[0]
    item_height = item_bbox[3] - item_bbox[1]

    # Thumbnail needs to be a square image
    x_padding, y_padding = 0, 0
    if item_width < item_height:
        x_padding = (item_height - item_width) // 2
    elif item_height < item_width:
        y_padding = (item_width - item_height) // 2

    margin_bbox = (
        item_bbox[0] - MARGIN - x_padding,
        item_bbox[1] - MARGIN - y_padding,
        item_bbox[2] + MARGIN + x_padding,
        item_bbox[3] + MARGIN + y_padding,
    )
    
    # potential of 1px discrepency due to int division from earlier step
    bbox_width = margin_bbox[2] - margin_bbox[0]
    bbox_height = margin_bbox[3] - margin_bbox[1]
    # print(item_id, bbox_width, bbox_height)

    if bbox_width != bbox_height:
        margin_bbox[2] += bbox_height - bbox_width

    # enlarge bounding box for cases where it's smaller than thumbnail size
    bbox_width = margin_bbox[2] - margin_bbox[0]
    bbox_height = margin_bbox[3] - margin_bbox[1]
    if bbox_width < THUMBNAIL_SIZE:
        padding = (THUMBNAIL_SIZE - bbox_width)//2

        margin_bbox = (
            margin_bbox[0] - padding,
            margin_bbox[1] - padding,
            margin_bbox[2] + padding,
            margin_bbox[3] + padding,
        )

    # background and back items draw behind the base layer
    if item_id.startswith('back'):
        item_img.paste(base_img, None, base_img)
        base_img = item_img

    # don't include base layer for pet thumbnails
    elif item_id.startswith('pet'):
        base_img = item_img

    else:
        base_img.paste(item_img, None, item_img)

    crop_img = base_img.crop(margin_bbox)

    background = Image.new(
        "RGBA", crop_img.size, "#FFFFFF"
    )  # Create a white rgba background
    background.paste(crop_img, (0, 0), crop_img)

    background.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
    # print(background.size)
    # background.show()

    background.save(f"gen_thumbnails/{item_id}.png", optimize=True, quality=95)

    return item_id, background

async def main():
    start = time.perf_counter()
    loop = asyncio.get_running_loop()

    base_img_copy = Image.open("img/base_m_001.png")

    with concurrent.futures.ThreadPoolExecutor() as pool:
        blocking_tasks = []

        # get the path/directory
        folder_dir = "img"

        # iterate over files in
        # that directory
        for filepath in glob.iglob(f"{folder_dir}/*.png"):
            
            # check if the image ends with png
            if filepath.endswith(".png"):
                
                filename = filepath.split("\\")[1]
                item_id = filename.split(".")[0]
                # print(item_id)
                # thumbnail = generate_thumbnail(item_id)
                # thumbnail = await loop.run_in_executor(pool, generate_thumbnail, item_id)
                blocking_tasks.append(loop.run_in_executor(pool, generate_thumbnail, base_img_copy.copy(), item_id))

        completed, pending = await asyncio.wait(blocking_tasks)
        results = [t.result() for t in completed]
        
        for result in results:
            print(result)

    end = time.perf_counter()
    print(f"Time taken: {end-start}s")

if __name__ == '__main__':
    asyncio.run(main())