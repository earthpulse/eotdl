"""
Responses for datasets endpoints
"""

retrieve_datasets_responses = {
    200: {
         "content": {
            "application/json": {
                        "example": [
                            {
                                "uid": "auth0|123",
                                "id": "123acb",
                                "name": "awesome-dataset",
                                "authors": [
                                    "awesome-author-1",
                                    "awesome-author-2"
                                ],
                                "source": "https://www.eotdl.com",
                                "license": "MIT",
                                "files": "123",
                                "versions": [
                                {
                                    "version_id": 1,
                                    "createdAt": "2023-10-12T07:14:16.642",
                                    "size": 1000
                                }
                                ],
                                "description": "My awesome dataset",
                                "tags": [
                                    'sar',
                                    'vector'
                                ],
                                "createdAt": "2023-10-25T16:08:29.666",
                                "updatedAt": "2023-10-26T11:31:21.189",
                                "likes": 100,
                                "downloads": 200,
                                "quality": 2
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
                "example":
                    [
                        {
                            "filename": "file_1.png",
                            "version": 1,
                            "checksum": "123acb"
                        },
                        {
                            "filename": "file_2.png",
                            "version": 1,
                            "checksum": "123acb"
                        }
                    ]
                }
            }
        }
}


ingest_files_responses = {
    200: {
        "content": {
            "application/json": {
                "example":
                    {
                        "dataset_id": "123acb",
                        "dataset_name": "awesome-dataset",
                        "filenames": "awesome-files"
                    }
                }
            }
        }
    }


create_dataset_responses = {
    200: {
        "content": {
            "application/json": {
                "example":
                    {
                        "dataset_id": "123acb"
                    }
                }
            }
        }
    }


get_dataset_version_responses = {
    200: {
        "content": {
            "application/json": {
                "example":
                    {
                        "dataset_id": "123acb",
                        "dataset_version": 1
                    }
                }
            }
        },
    409: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example":
                    {
                        "detail": "You are not authorized to perform this action"
                    }
                }
            }
        }
    }


update_dataset_responses = {
    200: {
         "content": {
            "application/json": {
                        "example": [
                            {
                                "id": "123acb",
                                "user": "awesome-user",
                                "name": "awesome-dataset",
                                "authors": [
                                    "awesome-author-1",
                                    "awesome-author-2"
                                ],
                                "source": "https://www.eotdl.com",
                                "license": "MIT",
                                "tags": [
                                    'sar',
                                    'vector'
                                ],
                                "description": "My awesome dataset"
                            }
                        ]
                    }
                }
        }
}