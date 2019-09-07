from storages.backends.s3boto3 import S3Boto3Storage
class MediaStorage(S3Boto3Storage):
    location = 'media/'
    bucket_name = 'extoremedia.jonus.co.kr'
    custom_domain = 'extoremedia.jonus.co.kr'
    file_overwrite = False