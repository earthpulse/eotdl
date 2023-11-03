class DatasetAlreadyExistsError(Exception):
    message = "Dataset already exists"

    def __init__(self):
        super().__init__(self.message)


class DatasetDoesNotExistError(Exception):
    message = "Dataset doesn't exist"

    def __init__(self):
        super().__init__(self.message)


class FileDoesNotExistError(Exception):
    message = "File doesn't exist"

    def __init__(self):
        super().__init__(self.message)


class NameCharsValidationError(Exception):
    message = "Use only alphanumeric characters and hypens (-). Names cannot start with numbers. Whitespaces are not allowed."

    def __init__(self):
        super().__init__(self.message)


class NameLengthValidationError(Exception):
    def __init__(self, max_len, min_len):
        message = (
            f"Name must be less than {max_len} characters, and more than {min_len}"
        )
        super().__init__(message)


class DescriptionLengthValidationError(Exception):
    def __init__(self, max_len, min_len):
        message = f"Description must be less than {max_len} characters, and more than {min_len}"
        super().__init__(message)


class DatasetAlreadyLikedError(Exception):
    message = "Dataset already liked"

    def __init__(self):
        super().__init__(self.message)


class ChunkUploadChecksumMismatch(Exception):
    message = "Checksum mismatch."

    def __init__(self):
        super().__init__(self.message)


class UploadIdDoesNotExist(Exception):
    message = "Upload Id not found."

    def __init__(self):
        super().__init__(self.message)


class ChecksumMismatch(Exception):
    message = "Checksum mismatch."

    def __init__(self):
        super().__init__(self.message)


class DatasetVersionDoesNotExistError(Exception):
    message = "Dataset version doesn't exist"

    def __init__(self):
        super().__init__(self.message)
