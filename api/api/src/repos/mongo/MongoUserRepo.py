from .MongoRepo import MongoRepo


class MongoUserRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_user_by_uid(self, uid):
        return self.retrieve("users", uid, "uid")

    def retrieve_user_by_key(self, key):
        return self.retrieve("keys", key)

    def update_user(self, id, data):
        return self.update("users", id, data)

    def persist_user(self, data, id):
        return self.persist("users", data, id)

    def find_one_user_by_name(self, name):
        return self.find_one_by_name("users", name)

    def check_user_exists(self, uid):
        return self.exists("users", uid, "uid")

    def retrieve_tier(self, tier):
        return self.find_one_by_name("tiers", tier)

    def retrieve_dataset_ingestion_usage(self, uid):
        return self.find_in_time_range("usage", uid, "dataset_ingested", "type")

    def retrieve_dataset_download_usage(self, uid):
        return self.find_in_time_range("usage", uid, "dataset_download", "type")

    def retrieve_model_ingestion_usage(self, uid):
        return self.find_in_time_range("usage", uid, "model_ingested", "type")

    def retrieve_keys(self, uid):
        return self.retrieve("keys", match={"uid": uid})

    def persist_key(self, data):
        return self.persist("keys", data, id=data["id"])

    def delete_key(self, key):
        return self.delete("keys", key)


# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImUtdHB2cDI4NEZlX1pfVzVZRUpfaiJ9.eyJuaWNrbmFtZSI6Iml0IiwibmFtZSI6Iml0QGVhcnRocHVsc2UuZXMiLCJwaWN0dXJlIjoiaHR0cHM6Ly9zLmdyYXZhdGFyLmNvbS9hdmF0YXIvNjU1NzQxYmI2ZDkzMDNmNjljMGY2YTUzYmU2MjMwZDQ_cz00ODAmcj1wZyZkPWh0dHBzJTNBJTJGJTJGY2RuLmF1dGgwLmNvbSUyRmF2YXRhcnMlMkZpdC5wbmciLCJ1cGRhdGVkX2F0IjoiMjAyNC0wOC0wNVQxMDoxNzowMS40NTVaIiwiZW1haWwiOiJpdEBlYXJ0aHB1bHNlLmVzIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOi8vZWFydGhwdWxzZS5ldS5hdXRoMC5jb20vIiwiYXVkIjoic0M1V2Zsem1Qb2owNThGSllMMmNrRU51dHhKTDRQVFciLCJpYXQiOjE3MjI4NjY5NjUsImV4cCI6MTcyMjkwMjk2NSwic3ViIjoiYXV0aDB8NjE2YjAwNTdhZjBjNzUwMDY5MWEwMjZlIn0.cAtB_qmaUC6r5xFlgE7o7MR2LYIPY1jJmajPbCkPzXHpJ-8GUqeU2_1SQTDbI0K3cqw5Gc0t26uXMyO-TaQ4bivdJGvss6GF9PL7pTZRS2EPX2_axTFqnfKWKhYV31GI9ZB2JHczsOtXCnW3XVdj2KW8BNZ1Gma1mFqwRYgaQ86WZ7EPoibrOcXwOqyJoA-3nOCCdz10XmS1t57kAdq5KCE9msDgQvUuyDe_QfjvtgKuS7g0Rp2-Zt2793XIvXFxg1j-YJu6oaSNWclzskztQux7LtdyLMOlBFo9v8PCOWZFdjzNO_oQLCsw7OfhhmBbpai3MIWBjN65KpNj9juZxg
