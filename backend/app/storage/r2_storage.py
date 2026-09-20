from app.storage.base import StorageBackend


class R2Storage(StorageBackend):
    """
    Stockage sur Cloudflare R2 (API compatible S3, tier gratuit jusqu'a 10 Go/mois).
    Import de boto3 differe pour ne pas alourdir le demarrage quand STORAGE_BACKEND=local.
    """

    def __init__(
        self,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        public_base_url: str = "",
    ):
        import boto3

        self.bucket_name = bucket_name
        self.public_base_url = public_base_url.rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",
        )

    def save(self, key: str, data: bytes, content_type: str) -> str:
        self.client.put_object(Bucket=self.bucket_name, Key=key, Body=data, ContentType=content_type)
        if self.public_base_url:
            return f"{self.public_base_url}/{key}"
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket_name, "Key": key}, ExpiresIn=3600
        )

    def read(self, key: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket_name, Key=key)
        return obj["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket_name, Key=key)
