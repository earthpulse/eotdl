create_model_responses = {
    200: {"content": {"application/json": {"example": {"model_id": "123acb"}}}}
}

version_model_responses = {
    200: {
        "content": {
            "application/json": {"example": {"model_id": "123acb", "version": 1}}
        }
    }
}


update_model_responses = {
    200: {
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": "123acb",
                        "user": "awesome-user",
                        "name": "awesome-model",
                        "authors": ["awesome-author-1", "awesome-author-2"],
                        "source": "https://www.eotdl.com",
                        "license": "MIT",
                        "tags": ["sar", "vector"],
                        "description": "My awesome model",
                    }
                ]
            }
        }
    }
}

retrieve_models_responses = {
    200: {
        "content": {
            "application/json": {
                "example": [
                    {
                        "uid": "auth0|123",
                        "id": "123acb",
                        "name": "awesome-model",
                        "authors": ["awesome-author-1", "awesome-author-2"],
                        "source": "https://www.eotdl.com",
                        "license": "MIT",
                        "files": "123",
                        "versions": [
                            {
                                "version_id": 1,
                                "createdAt": "2023-10-12T07:14:16.642",
                                "size": 1000,
                            }
                        ],
                        "description": "My awesome model",
                        "tags": ["sar", "vector"],
                        "createdAt": "2023-10-25T16:08:29.666",
                        "updatedAt": "2023-10-26T11:31:21.189",
                        "likes": 100,
                        "downloads": 200,
                        "quality": 2,
                    }
                ]
            }
        }
    }
}

retrieve_files_responses = {
    200: {
        "content": {
            "application/json": {
                "example": [
                    {"filename": "file_1.png", "version": 1, "checksum": "123acb"},
                    {"filename": "file_2.png", "version": 1, "checksum": "123acb"},
                ]
            }
        }
    }
}


ingest_files_responses = {
    200: {
        "content": {
            "application/json": {
                "example": {
                    "model_id": "123acb",
                    "model_name": "awesome-model",
                    "filenames": "awesome-files",
                }
            }
        }
    }
}

ingest_model_responses = {
    200: {
        "content": {
            "application/json": {
                "example": {
                    "model_id": "123acb",
                    "model_name": "awesome-model",
                    "file_name": "file_1.png",
                }
            }
        }
    }
}

download_model_responses = {
    409: {
        "description": "File not found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "S3 operation failed; code: NoSuchKey, message: Object does not exist, resource: /bucket-name/123abc/File_None, request_id: 123abc, host_id: 123abc, bucket_name: bucket-name, object_name: 123abc/File_None"
                }
            }
        },
    }
}
