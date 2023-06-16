import hashlib


# async def calculate_checksum(data_stream):
#     hasher = hashlib.md5()
#     async for chunk in data_stream:
#         hasher.update(chunk)
#     return hasher.hexdigest()


async def calculate_checksum(data_stream):
    sha1_hash = hashlib.sha1()
    async for chunk in data_stream:
        sha1_hash.update(chunk)
    return sha1_hash.hexdigest()
