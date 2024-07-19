from pydantic import BaseModel


class ErrorSchema(BaseModel):
    """ Defines how an error message is represented
    """
    mesage: str
