from pydantic import BaseModel

class BackupAcceptedResponse(BaseModel):
    status: str
    message: str