#importing
import subprocess
import hashlib
import time
import json
import flask
import requests
import yaml
import sys
import os
import rsa
import signal
import base64
from flask import url_for
from random import randint
from time import sleep


#config
def get_config(config_file="config.yaml"):
    if "CONFIG" in os.environ:
        config_file=os.environ["CONFIG"]
    with open(config_file) as file:
        config=yaml.safe_load(file)
    
    return config

config=get_config()
hash_rate=config["hash_rate"]
servers=config["core_servers"]
my_id=f'{config["bind_ip"]}:{config["bind_port"]}'
data_file=config["data"]
my_name=config["id"]
my_public_key=config["public_key"]
print(hash_rate)

#accounts
accounts={}


#constants
royalty={
                "amount":1,
                "sender":"0",
                "receiver":my_public_key,
                "date":time.time(),
                "signature":"0"
        }

first_block={
                "blocks": [
                    {
                        "date": "Mon Apr 14 20:27:33 2025",
                        "prev_hash": "",
                        "hash": "d03bc40b2ee65a463e2cca1c7f17955e7cbbb3c5214b2472c23fcbbcaaa1a78b",
                        "data": [],
                        "key": "",
                        "ver": 1,
                        "hash_rate": 5
                    }
                ]
            }



#tech functions
def write(data, filename):
    data=json.dumps(data)
    data=json.loads(str(data))
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def read(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def send_massage(ip, massage):
    try:
        return requests.get("http://"+ip+massage).text
    except:
        return "error"

def run_mainer():
    p=subprocess.Popen(f"python3 mainer.py {my_id}",
                   stdin=None,
                   stdout=None,
                   stderr=None,
                   shell=True,
                   preexec_fn=os.setsid)
    
    return p

def get_checksum(transaction):
    return hashlib.sha256((str(transaction["amount"])+transaction["receiver"]+str(transaction["date"])).encode()).hexdigest()

def check_transaction(transaction):
    try:
        if transaction["sender"] in accounts:
            if accounts[transaction["sender"]]-transaction["amount"]<0:
                return False

            public_key=rsa.PublicKey.load_pkcs1(transaction["sender"])
            if type(transaction["signature"])==type(""):
                signature=eval(transaction["signature"])
            else:
                signature=transaction["signature"]
            
            checksum=get_checksum(transaction).encode()
            a=rsa.verify(checksum, signature, public_key)
            if a=="SHA-256":
                return True
            else:
                return False
    except:
        return False

    public_key=rsa.PublicKey.load_pkcs1(transaction["sender"])
    signature=eval(transaction["signature"])
    checksum=get_checksum(transaction).encode()
    a=rsa.verify(checksum, signature, public_key)
    if a=="SHA-256":
        return True
    else:
        return False
    '''except:
        return False'''

def inizialization(transaction):
    ans=base64.b64decode(eval(transaction)).decode()
    try:
        ans=eval(ans)
    except:
        ans=str(ans)
    return ans

def inizialization_for_data(transaction):
    ans=base64.b64decode(transaction).decode()
    try:
        ans=eval(ans)
    except:
        ans=str(ans)
    return ans

def encode_data(data):
    return base64.b64encode(str(data).encode())

def connect_transaction_to_account(j):
    if j["receiver"] in accounts:
        accounts[j["receiver"]]+=j["amount"]
    else:
        accounts[j["receiver"]]=j["amount"]
    if j["sender"] in accounts:
        accounts[j["sender"]]-=j["amount"]
    else:
        accounts[j["sender"]]=-j["amount"]
    
def copy_block(i):
    if i.ver>=2:
        return Block(i.date, i.prev_hash, i.hash, [{"amount": j["amount"], "sender": j["sender"], "receiver": j["receiver"], "date": j["date"], "signature": j["signature"]} for j in i.data], i.key, i.ver, i.hash_rate)
    else:
        return Block(i.date, i.prev_hash, i.hash, [{"number": j["number"], "sender": j["sender"], "receiver": j["receiver"], "date": j["date"]} for j in i.data], i.key, i.ver, i.hash_rate)

def convert_blockchain_to_give(blockchain):
    given_blockchain=[copy_block(i) for i in blockchain]
    for i in given_blockchain:
        if type(i.date)==type(0.1):
            i.date=time.ctime(i.date)
        for j in i.data:
            if type(j["date"])==type(0.1):
                j["date"]=time.ctime(j["date"])
    
    return given_blockchain
    


#Blocks and Blockchain
class Block():
    def __init__(self, date, prev_hash, hash, data, key, ver, hash_rate):
        self.date=date
        self.prev_hash=prev_hash
        self.hash=hash
        self.data=data
        self.key=key
        self.ver=ver
        self.hash_rate=hash_rate

class Blockchain():
    def __init__(self):
        #self.blocks=[Block(time.ctime(time.time()), "", hashlib.sha256(((time.ctime(time.time())+hashlib.sha256(str([]).encode()).hexdigest()).encode())).hexdigest(), [], "", 1, hash_rate)]
        self.blocks=read(data_file)["blocks"]
        for i in range(len(self.blocks)):
            self.blocks[i]=Block(self.blocks[i]["date"], self.blocks[i]["prev_hash"], self.blocks[i]["hash"], self.blocks[i]["data"], self.blocks[i]["key"], self.blocks[i]["ver"], self.blocks[i]["hash_rate"])
            if self.blocks[i].ver>=4:
                for j in self.blocks[i].data:
                    connect_transaction_to_account(j)
                
        self.eqeue=[]
        self.transactions=[]
    
    def get_last_block(self):
        return self.blocks[len(self.blocks)-1]
    
    def add_block(self, hash, date, key):
        check_sum=hashlib.sha256(str(self.eqeue).encode()).hexdigest()
        if hash[len(hash)-hash_rate:]==self.get_last_block().hash[:hash_rate] and hashlib.sha256((str(date)+str(self.get_last_block().hash)+str(check_sum)+str(key)).encode()).hexdigest()==hash:
            permission=True
            limit=0
            for i in self.eqeue:
                if i not in self.transactions:
                    if i["sender"]!="0" and not check_transaction(i):
                        permission=False
                        break
                    elif i["sender"]=="0":
                        limit+=i["amount"]
            if permission and limit<=1:
                block=Block(date, self.get_last_block().hash, hash, self.eqeue, key, 4, hash_rate)
                self.blocks.append(block)
                for i in self.eqeue:
                    connect_transaction_to_account(i)
                i=0
                while i<len(self.transactions):
                    if self.transactions[i] in self.eqeue:
                        self.transactions.pop(i)
                    else:
                        i+=1
                self.eqeue=[i for i in self.transactions]
                return True
            else:
                return False
        else:
            return False
    
    def check_blockchain(self):
        j=0
        for i in self.blocks:
            check_sum=hashlib.sha256(str(i.data).encode()).hexdigest()
            if hashlib.sha256((str(i.date)+str(i.prev_hash)+str(check_sum)+str(i.key)).encode()).hexdigest()!=i.hash:
                return False
            if j!=0 and i.prev_hash!=j.hash:
                print(i.__dict__)
                return False
            if j!=0 and i.hash[len(i.hash)-i.hash_rate:]!=j.hash[:i.hash_rate]:
                return False
            limit=0
            if i.ver>=4:
                for l in i.data:
                    if l["sender"]!="0" and not check_transaction(l):
                            print(i.__dict__)
                            return False
                    elif l["sender"]=="0":
                        limit+=l["amount"]
                if limit>1:
                    return False
            j=copy_block(i)

        return True
    
    def save_blockchain(self):
        ans={
            "blocks":[]
        }
        for i in self.blocks:
            ans["blocks"].append(i.__dict__)

        write(ans, data_file)



#data file inizialization
try:
    if read(data_file)["blocks"]==[]:
        write(first_block, data_file)
except:
    write(first_block, data_file)



#audit blockchain and connect to network of servers
ser=Blockchain()
print(ser.check_blockchain())

blocks=read(data_file)["blocks"]
for i in range(len(blocks)):
    blocks[i]=Block(blocks[i]["date"], blocks[i]["prev_hash"], blocks[i]["hash"], blocks[i]["data"], blocks[i]["key"], blocks[i]["ver"], blocks[i]["hash_rate"])

def try_to_connect():
    global hash_rate, servers, blocks, ser
    try:
        a=send_massage(servers[0], "/new_server/"+my_id)
        a=a.split("%")
        for i in eval(a[0]):
            if i!=my_id:
                servers.append(i)
        hash_rate=int(a[1])
        a=eval(send_massage(servers[0], "/get_blockchain/"+ser.get_last_block().hash))
        b={"blocks":a}
        write(b, data_file)
        ser.__init__()
        if ser.check_blockchain():
            b=[i for i in ser.blocks]
            ser.blocks=blocks
            for i in b:
                ser.blocks.append(i)
            ser.save_blockchain()
        else:
            servers.pop(0)
            try_to_connect()
    except:
        servers.pop(0)
        if servers!=[]:
            try_to_connect()
        else:
            ser.blocks=blocks
            ser.save_blockchain()
            print("Error connection")

#sleep(randint(1,10))

if servers!=[]:
    try_to_connect()

for i in servers:
    send_massage(i, "/connect_server/"+my_id)


#run mainer
p=run_mainer()


#client response
amount_of_blocks=0


#FLASK
app=flask.Flask(__name__)

@app.route("/")
def home():
    return "Hello"

@app.route("/get_info")
def prev_block():
    prev_hash=ser.get_last_block().hash
    return prev_hash+" "+str(hash_rate)

@app.route("/new_server/<string:id>")
def new_server(id):
    servers.append(id)
    return str(servers[:len(servers)-1])+"%"+str(hash_rate)

@app.route("/get_blockchain/<string:last_hash>")
def get_blockchain(last_hash):
    index="error"
    for i in ser.blocks:
        if i.hash==last_hash:
            index=ser.blocks.index(i)
            break

    if index=="error":
        return "Error"
    else:
        return str([i.__dict__ for i in ser.blocks[index+1:]])

@app.route("/found_new_block/<string:block>")
def new_block(block):
    global p, amount_of_blocks
    block=block.split()
    ser.eqeue.append(royalty)
    prot_data=encode_data(ser.eqeue)
    if ser.add_block(block[0], float(block[1]), int(block[2])):
        ser.save_blockchain()
        for i in servers:
            send_massage(i, f"/found_new_block_an/{prot_data}  {block[0]}  {block[1]}  {block[2]}")
        
        p=run_mainer()
        amount_of_blocks+=1
    
    return "OK"

@app.route("/found_new_block_an/<string:block>")
def new_block_an(block):
    global p
    a=ser.eqeue
    block=block.split("  ")
    ser.eqeue=inizialization(block[0])
    if ser.add_block(block[1], float(block[2]), int(block[3])):
        ser.save_blockchain()
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        p=run_mainer()
        return "OK"
    else:
        ser.eqeue=a
        return "Error"


@app.route("/connect_server/<string:id>")
def connect_server(id):
    if id not in servers:
        servers.append(id)
        return "OK"
    else:
        return "Error"
    
@app.route("/get_eqeue/<string:name>")
def get_eqeue(name):
    if name=="mainer":
        a=[i for i in ser.eqeue]
        a.append(royalty)
        return str(a).encode()
    else:
        return str(ser.eqeue).encode()

@app.route("/new_client/<string:transaction>")
def new_client(transaction):
    transaction_an=transaction
    transaction=inizialization(transaction)
    if check_transaction(transaction):
        transaction["signature"]=str(transaction["signature"])
        ser.transactions.append(transaction)
        for i in servers:
            send_massage(i, "/new_client_an/"+transaction_an)
    
        return "OK"
    else:
        return "Error"
    
@app.route("/new_client_an/<string:transaction>")
def new_client_an(transaction):
    transaction=inizialization(transaction)
    if check_transaction(transaction):
        transaction["signature"]=str(transaction["signature"])
        ser.transactions.append(transaction)
        return "OK"
    else:
        return "Error"

@app.route("/client_get_blockchain")
def client_page():
    given_blockchain=convert_blockchain_to_give(ser.blocks)
    
    return flask.render_template("/index.html", blockchain=given_blockchain, ip=my_id)

@app.route("/get_block/<string:hash>")
def get_block(hash):
    for i in ser.blocks:
        if i.hash==hash:
            return flask.jsonify(convert_blockchain_to_give([i])[0].__dict__)
    
    return "Error"

@app.route("/client_servers")
def client_servers():
    given_servers=[]
    for i in servers:
        given_servers.append(inizialization_for_data(send_massage(i, "/info_for_client")))
    given_servers.append({"name":my_name, "ip":my_id, "hash_rate":hash_rate})
    return flask.render_template("/servers.html", servers=given_servers)

@app.route("/info_for_client")
def info_for_client():
    return encode_data({"name":my_name, "ip":my_id, "hash_rate":hash_rate})

@app.route("/info_for_client_detail")
def info_for_client_detail():
    k=0
    for i in ser.blocks:
        if i.ver>=3:
            for j in i.data:
                if j["signature"]=="0" and j["receiver"]==my_public_key:
                    k+=1
    return flask.render_template("/server_detail.html", ip=my_id, name=my_name, hash_rate=hash_rate, public_key=my_public_key, amount_of_blocks=amount_of_blocks, amount_of_allblocks=k)

@app.route("/client_accounts")
def client_accounts():
    return flask.render_template("/accounts.html", accounts=accounts, encode_data=encode_data)

@app.route("/client_account/<string:account>")
def client_account(account):
    account=str(inizialization(account))
    ans=[]
    current_acc=0
    for i in ser.blocks:
        if i.ver>=4:
            for j in i.data:
                if j["sender"]==account:
                    current_acc-=j["amount"]
                    ans.append({"date":time.ctime(j["date"]),
                                "amount":-j["amount"],
                                "an_acc":j["receiver"],
                                "current_acc":current_acc})
                elif j["receiver"]==account:
                    current_acc+=j["amount"]
                    ans.append({"date":time.ctime(j["date"]),
                                "amount":j["amount"],
                                "an_acc":j["sender"],
                                "current_acc":current_acc})
    
    return flask.render_template("/account.html", account=account, amount_acc=accounts[account], transactions=ans, ip=my_id, len=len)