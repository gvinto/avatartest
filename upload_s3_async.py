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
    async with session.client("s3") as s3:
        bucket = 'launchpad-305326993135' #await s3.Bucket('launchpad-305326993135')

        # Clear out S3 images folder (can omit since new uploads will overwrite)
        # await bucket.objects.filter(Prefix='avatar/images/').delete()

        # Upload all images to S3
        img_files = glob.glob("img/*.png")
        num_files = len(img_files)
        count = 0
        LOG.info(f'Found {num_files} files. Starting upload...')
        for filepath in img_files:
            filename = filepath.split('\\')[1]
            LOG.info(f'Uploading {count}/{num_files} files...')

            tasks.append(asyncio.ensure_future(upload(s3, filepath, filename, bucket, 'avatar/images/')))

            count+=1

        # Upload items_db.json
        LOG.info(f'Uploading items_db.json...')
        tasks.append(asyncio.ensure_future(upload(s3, 'items_db.json', 'items_db.json', bucket, 'avatar/config/')))

        LOG.info(f'Uploading in background, please wait...')
        await asyncio.gather(*tasks)

    end = time.perf_counter()
    print(f"Time taken: {end-start}s")


if __name__ == '__main__':
    asyncio.run(main())