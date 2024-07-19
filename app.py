from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from logger import logger
from schemas import *
from flask_cors import CORS

import requests

info = Info(title="PUC Trading Bank - Bank service", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentation", description="Documentation of User service")
routes_tag = Tag(name="Routes", description="Implemented routes for Bank service")

user_endpoint = "http://127.0.0.1:5001/"
transaction_endpoint = "http://127.0.0.1:5002/"
translation_endpoint = "https://api.currencyapi.com/v3/latest"
API_KEY = ""

def get_translation_rate(currency:str):
    payload = {
        "apikey": API_KEY,        
        "base_currency": currency,
        "currencies": "USD"
    }
    
    response = requests.get(translation_endpoint, params=payload)
    return response.json()["data"]["USD"]["value"]

@app.get('/', tags=[home_tag])
def home():
    """Redirects to the Swagger documentation of Bank Service
    """
    return redirect('/openapi/swagger')

@app.post('/deposit', tags=[routes_tag],
          responses={"200": UserViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_cash_to_user(form: BankUserOperationSchema):
    """Adds money to a user's account
    This route communicates with:
        - User service to add money
        - Transaction service to register the transaction in the data base
        - API Currency to have a cotation if the incoming money is other than USD
    """ 
    id_user = form.id_user
    currency = form.currency
    amount = form.amount
    translation_rate = 1
    
    if amount <= 0: 
        error_message = "Amount must be an positive number"
        return {"message": error_message} , 406

    
    if currency != "USD":
        translation_rate = get_translation_rate(currency)
    
    ''' Request to user service '''
    
    payload = {
        "id": id_user,
        "delta": amount * translation_rate
    }
    
    response = requests.put(user_endpoint + "user", params=payload)
    
    ''' Request to transaction service '''
    
    payload_transaction = {
        "amount": amount,
        "currency_source": currency,
        "currency_target": "USD",
        "id_target": id_user,
        "id_source": -1
    }

    resp = requests.post(transaction_endpoint + "transaction", data=payload_transaction)

    print(resp)

    return response.json(), 200

@app.post('/transfer', tags=[routes_tag],
          responses={"200": UserViewSchema, "409": ErrorSchema, "400": ErrorSchema, "406": ErrorSchema})
def transfer_cash_to_user(form: BankUserTransferSchema):
    """Transfer money from a user's account (A) to another user's account (B)
    This route communicates with:
        - User service to check balance of user A and take its money
        - User service to add money to B
        - Transaction service to register the transaction in the data base
        - API Currency to have a cotation if the incoming money is other than USD
    """ 
    id_user = form.id_user
    id_target = form.id_target
    currency = form.currency
    amount = form.amount
    translation_rate = 1
    
    if amount <= 0: 
        error_message = "Amount must be an positive number"
        return {"message": error_message} , 406
    
    if id_user == id_target <= 0: 
        error_message = "Transfer must be done to a different user. For deposits, use the deposit route"
        return {"message": error_message} , 406
    
    if currency != "USD":
        translation_rate = get_translation_rate(currency)
    
    ''' Request to user service '''
    
    user_balance = requests.get(user_endpoint + "user", params={"id": id_user}).json()['balance']

    delta = amount * translation_rate
    
    if user_balance < delta:
        error_message = "User has no enough balance to transfer."
        return {"message": error_message} , 406
    
    ''' Takes the money from sender'''
    payload_sender = {
        "id": id_user,
        "delta": -delta
    }    
    
    response = requests.put(user_endpoint + "user", params=payload_sender)
    
    ''' And gives to the receiver '''
    payload_receiver = {
        "id": id_target,
        "delta": delta
    }    
    
    response = requests.put(user_endpoint + "user", params=payload_receiver)
    
    ''' Request to transaction service to register'''
    
    payload_transaction = {
        "amount": amount,
        "currency_source": currency,
        "currency_target": "USD",
        "id_target": id_target,
        "id_source": id_user
    }

    resp = requests.post(transaction_endpoint + "transaction", data=payload_transaction)

    print(resp)

    return response.json(), 200

@app.post('/withdraw', tags=[routes_tag],
          responses={"200": UserViewSchema, "409": ErrorSchema, "400": ErrorSchema, "406": ErrorSchema})
def rem_cash_from_user(form: BankUserOperationSchema):
    """Withdraws money from a user's account
    This route communicates with:
        - User service to check balance of user A and take its money
        - Transaction service to register the transaction in the data base
        - API Currency to have a cotation if the money requested is other than USD
    """ 
    id_user = form.id_user
    currency = form.currency
    amount = form.amount
    translation_rate = 1
    
    if amount <= 0:
        error_message = "Amount must be an positive number"
        return {"message": error_message} , 406
    
    if currency != "USD":
        translation_rate = get_translation_rate(currency)
    
    delta = amount * translation_rate
    print(delta)
    
    user_balance = requests.get(user_endpoint + "user", params={"id": id_user}).json()['balance']
    
    if user_balance < delta:
        error_message = "User has no enough balance to withdraw."
        return {"message": error_message} , 406
    
    payload = {
        "id": id_user,
        "delta": -delta
    }
    
    response = requests.put(user_endpoint + "user", params=payload)
    
    payload_transaction = {
        "amount": amount,
        "currency_source": currency,
        "currency_target": "USD",
        "id_target": -1,
        "id_source": id_user
    }
    requests.post(transaction_endpoint + "transaction", data=payload_transaction)

    return response.json(), 200

@app.post('/transactions', tags=[routes_tag],
          responses={"200": ListOfTransactionsSchema, "409": ErrorSchema, "400": ErrorSchema, "406": ErrorSchema})
def get_transactions_from_user(form: BankUserTransactionsSchema):
    """Retrieves all transactions related to a user
        This route communicates with:
        - Transaction service to catch all transactions registered to the user
        
        Returns a structure with all deposits, withdraws, transfers received and transfers sent.
    """ 
    id_user = form.id_user
    
    user_transactions = requests.get(transaction_endpoint + "transactions", params={"id_user": id_user}).json()["transactions"]
    
    response = {}
    
    response["deposits"] = [transaction for transaction in user_transactions 
                            if(transaction["id_source"]== -1 and transaction["id_target"] == id_user)] 
    
    response["withdraws"] = [transaction for transaction in user_transactions 
                            if(transaction["id_source"] == id_user and transaction["id_target"] == -1)] 
    
    response["transfers_sent"] = [transaction for transaction in user_transactions 
                            if(transaction["id_source"] == id_user and transaction["id_target"] not in [-1, id_user])]
    
    response["transfers_received"] = [transaction for transaction in user_transactions 
                            if(transaction["id_source"] not in [-1, id_user] and transaction["id_target"] == id_user)] 

    return response, 200

