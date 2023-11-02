"""
Responses for the auth endpoints
"""


me_responses = {
    200: {
         "content": {
            "application/json": {
                        "example": {
                            "id": "123abc",
                            "uid": "auth0|123abc",
                            "name": "yourname",
                            "email": "mail@example.ai",
                            "picture": "yourpicture.png",
                            "createdAt": "2023-05-16T12:16:48.983",
                            "updatedAt": "2023-10-31T15:54:45.351",
                            "dataset_count": 5,
                            "models_count": 0,
                            "tier": "free",
                            "liked_datasets": [],
                            "terms": {
                                "geodb": False,
                                "sentinelhub": False,
                                "eoxhub": True,
                                "eotdl": False
                            }
                        }
                    }
                }
        },
    409: {
        "description": "No user found",
        "content": {
            "application/json": {
                        "example": {
                            "detail": "'NoneType' object has no attribute 'uid'"
                        }
                    }
                }
        },
    401: {
        "description": "Unauthorized token",
        "content": {
            "application/json": {
                        "example": {
                            "detail": "Invalid token"
                        }
                    }
                }
        }
    }


login_responses = {
    200: {
        "content": {
            "application/json": {
                        "example": {
                            "login_url": "https://earthpulse.eu.auth0.com/activate?user_code=123456",
                            "code": "123456abc",
                            "message": "Navigate to the URL and confirm to login. Then, request your token at the /token endpoint with the provided code."
                        }
                    }
                }
        }
}


logout_responses = {
    200: {
        "content": {
            "application/json": {
                        "example": {
                            "logout_url": "https://earthpulse.eu.auth0.com/v2/logout?cliend_id=123abc&returnTo=http://api.eotdl.com/auth/callback"
                        }
                    }
                }
        }
}


token_responses = {
    200: {
         "content": {
            "application/json": {
                        "example": {
                            "id_token": "123abc",
                            "expires_in": 86400,
                            "token_type": "Bearer"
                        }
                    }
                }
        },
    409: {
        "description": "No code provided",
        "content": {
            "application/json": {
                        "example": {
                            "detail": "Missing required parameter: device_code"
                        }
                    }
                }
        }
    }
