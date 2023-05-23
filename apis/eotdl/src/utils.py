import hashlib


async def calculate_checksum(data_stream):
    hasher = hashlib.md5()
    async for chunk in data_stream:
        hasher.update(chunk)
    return hasher.hexdigest()
