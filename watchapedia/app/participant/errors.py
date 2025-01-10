from fastapi import HTTPException

class ParticipantAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Participant already exists")

class ParticipantNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Participant not found")