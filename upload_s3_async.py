import aioboto3
import asyncio
from pathlib import Path
import logging as LOG
import glob, time

LOG.basicConfig(level=LOG.INFO)

async def upload(s3, filepath, filename, bucket, bucket_path):
    blob_s3_key = f"{bucket_path}{filename}"
    staging_path = Path(filepath)
    try:
        with staging_path.open("rb") as spfp:
            LOG.info(f"Uploading {blob_s3_key} to s3")
            await s3.upload_fileobj(spfp, bucket, blob_s3_key)
            LOG.info(f"Finished Uploading {blob_s3_key} to s3")
    except Exception as e:
        LOG.error(f"Unable to s3 upload {staging_path} to {blob_s3_key}: {e} ({type(e)})")

async def main():
    start = time.perf_counter()
    tasks =[]

    session = aioboto3.Session()
    bucket_name = 'launchpad-305326993135'

    async with session.resource("s3") as s3:
        # Clear out S3 avatar images folder (can omit since new uploads will overwrite)
        bucket = await s3.Bucket(bucket_name)
        await bucket.objects.filter(Prefix='avatar/images/').delete()

    async with session.client("s3") as s3:
        # Upload all images to S3
        img_files = glob.glob("img/*.png")
        num_files = len(img_files)
        count = 0
        LOG.info(f'Found {num_files} image files. Starting upload...')
        for filepath in img_files:
            filename = filepath.split('\\')[1]
            LOG.info(f'Uploading {count}/{num_files} files...')

            tasks.append(asyncio.ensure_future(upload(s3, filepath, filename, bucket_name, 'avatar/images/')))

            count+=1

        # Upload all thumbnails to S3
        img_files = glob.glob("gen_thumbnails/*.png")
        num_files = len(img_files)
        count = 0
        LOG.info(f'Found {num_files} thumbnail files. Starting upload...')
        for filepath in img_files:
            filename = filepath.split('\\')[1]
            LOG.info(f'Uploading {count}/{num_files} files...')

            tasks.append(asyncio.ensure_future(upload(s3, filepath, filename, bucket_name, 'avatar/images/thumbnails/')))

            count+=1

        # Upload items_db.json
        LOG.info(f'Uploading items_db.json...')
        tasks.append(asyncio.ensure_future(upload(s3, 'items_db.json', 'items_db.json', bucket_name, 'avatar/config/')))

        # Upload items_db.json
        LOG.info(f'Uploading task_rewards.json...')
        tasks.append(asyncio.ensure_future(upload(s3, 'task_rewards.json', 'task_rewards.json', bucket_name, 'avatar/config/')))

        LOG.info(f'Uploading in background, please wait...')
        await asyncio.gather(*tasks)

    end = time.perf_counter()
    print(f"Time taken: {end-start}s")


if __name__ == '__main__':
    asyncio.run(main())