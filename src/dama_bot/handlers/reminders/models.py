from pydantic import BaseModel
from datetime import datetime

class Reminder(BaseModel):
    text: str
    remind_at: datetime

    @property
    def due(self) -> bool:
        return datetime.now() > self.remind_at
