import os
import sys
from multiprocessing import Pool
import threading
import boto3

from sickdb.config import settings


class S3FSUpload(threading.Thread):
	"""
	Uploading is a separate class as suggested for thread-safe
	use of multiprocessing by the boto3 docs:
	http://boto3.readthedocs.io/en/latest/guide/resources.html#multithreading-multiprocessing
	"""

    def run(self, bucket, key, file_path):
    	"""
    	TODO: metadata storeage
    	"""
        sys.stderr.write("INFO: Uploading {} to {}".format(
            file_path, s3_path))
        session = boto3.session.Session()
        s3 = session.resource('s3')
        s3.Object(bucket, key).put(
            Body=open(file_path, 'rb'))
        return "s3://{}".format(os.path.join(bucket, key))  # TODO: validation


class S3FS(object):

    def __init__(self, num_workers=8, **kwargs):
        self.bucket = kwargs.get("s3_bucket", settings.S3_BUCKET)
        self.key = kwargs.get("s3_key", settings.S3_PATH_KEY)
        self.num_workers = num_workers

    def add(self, song):
        name = song.file.split("/")[-1]
        path = os.path.join(self.key, name)
        return S3FSUpload().run(self.bucket, path, song.file)

    def add_many(self, songs):
        with Pool(self.num_workers) as p:
            for upload_path in p.imap_unordered(self.add, songs):
                sys.stderr.write("Sucessfully uploaded {}".format(upload_path))
