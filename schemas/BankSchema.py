from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BankUserOperationSchema(BaseModel):
    """ Defines how a deposit/withdraw is made
    """
    id_user: int = 1
    currency: str = "USD"
    amount: float = 50.00
    
class BankUserTransferSchema(BaseModel):
    """ Defines how a transfer is made
    """
    id_user: int = 1
    id_target: int = 2
    currency: str = "USD"
    amount: float = 50.00

class BankUserTransactionsSchema(BaseModel):
    """ Defines how user's transactions are searched
    """
    id_user: int = 1

class UserSchema(BaseModel):
    """ Defines the definition of a new user to be insert
    """
    first_name: str = "Mark"
    last_name: str = "Zuckerberg"
    document: str = "12345678900"

class UserViewSchema(BaseModel):
    """ Defines how a user is returned
    """
    id: int = 1
    first_name: str = "Mark"
    last_name: str = "Zuckerberg"
    balance: float = 0.0
    registration_date : str = "15/09/2023"
    
class TransactionViewSchema(BaseModel):
    """ Defines how a user is returned
    """
    id_transaction: int = 1
    id_source: int = 1
    currency_source: str = "USD"
    id_target: int = 1
    currency_target: str = "USD"
    amount: float = 50.0
    translation_rate: float = 1.0
    registration_date : datetime = datetime.now()
    

class ListOfTransactionsSchema(BaseModel):
    deposits: List[TransactionViewSchema]
    withdraws: List[TransactionViewSchema]
    transfers_sent: List[TransactionViewSchema]
    transfers_received: List[TransactionViewSchema]
