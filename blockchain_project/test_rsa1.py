import rsa
import time
import hashlib
import base64
import requests
import os
import yaml

def get_config(config_file="config_test_rsa.yaml"):
    if "CONFIG" in os.environ:
        config_file=os.environ["CONFIG"]
    with open(config_file) as file:
        config=yaml.safe_load(file)
    
    return config

config=get_config()
public=config["public_key"]
private=config["private_key"]
receiver=config["receiver"]
amount=config["amount"]

with open(public, "rb") as file:
    public_key=rsa.PublicKey.load_pkcs1(file.read())

with open(public, "rb") as file:
    public_key_txt=file.read().decode()

with open(private, "rb") as file:
    private_key=rsa.PrivateKey.load_pkcs1(file.read())

with open(receiver, "rb") as file:
    public_key_receiver=file.read().decode()

def get_checksum(transaction):
    return hashlib.sha256((str(transaction["amount"])+transaction["receiver"]+str(transaction["date"])).encode()).hexdigest()

def encode_data(data):
    return base64.b64encode(str(data).encode())


transaction={
                    'amount':int(amount),
                    'sender':public_key_txt[:-1],
                    'receiver':public_key_receiver[:-1],
                    'date':time.time(),
                    'signature':''
            }

r=True
while r:
    message=get_checksum(transaction)
    message=message.encode()

    signature=rsa.sign(message, private_key, "SHA-256")

    a=rsa.verify(message, signature, public_key)

    transaction["signature"]=signature
    ans=str(encode_data(transaction))
    if "/" not in ans:
        r=False

print(requests.get("https://jack.rittaker.com/new_client/"+ans).text)