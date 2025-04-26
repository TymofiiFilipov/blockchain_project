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



#constants
royalty={
                "number":1,
                "sender":"0",
                "receiver":my_name,
                "date":time.ctime(time.time())
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
    return requests.get("http://"+ip+massage).text

def run_mainer():
    p=subprocess.Popen(f"python3 mainer.py {my_id}",
                   stdin=None,
                   stdout=None,
                   stderr=None,
                   shell=True)
    
    return p



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
        self.eqeue=[]
    
    def get_last_block(self):
        return self.blocks[len(self.blocks)-1]
    
    def add_block(self, hash, date, key):
        check_sum=hashlib.sha256(str(self.eqeue).encode()).hexdigest()
        if hash[len(hash)-hash_rate:]==self.get_last_block().hash[:hash_rate] and hashlib.sha256((str(date)+str(self.get_last_block().hash)+str(check_sum)+str(key)).encode()).hexdigest()==hash:
            block=Block(date, self.get_last_block().hash, hash, self.eqeue, key, 1, hash_rate)
            self.blocks.append(block)
            self.eqeue=[]
            return True
        else:
            return False
    
    def check_blockchain(self):
        j=0
        for i in self.blocks:
            check_sum=hashlib.sha256(str(i.data).encode()).hexdigest()
            if hashlib.sha256((str(i.date)+str(i.prev_hash)+str(check_sum)+str(i.key)).encode()).hexdigest()!=i.hash:
                return False
            if j!=0 and i.prev_hash!=j.hash:
                return False
            if j!=0 and i.hash[len(i.hash)-i.hash_rate:]!=j.hash[:i.hash_rate]:
                return False
            j=i
        
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

if servers!=[] and my_id!="127.0.0.1:5000":
    try_to_connect()

for i in servers:
    try:
        a=send_massage(i, "/connect_server/"+my_id)
    except:
        pass



#run mainer
p=run_mainer()



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
        return str([i.__dict__ for i in ser.blocks[index:]])

@app.route("/found_new_block/<string:block>")
def new_block(block):
    block=block.split()
    ser.eqeue.append(royalty)
    prot_data=ser.eqeue
    if ser.add_block(block[0], time.ctime(float(block[1])), int(block[2])):
        ser.save_blockchain()
        for i in servers:
            a=send_massage(i, f"/found_new_block_an/{prot_data}  {block[0]}  {block[1]}  {block[2]}")

    ser.eqeue=[]

    p=run_mainer()
    
    return "OK"

@app.route("/found_new_block_an/<string:block>")
def new_block_an(block):
    global p
    a=ser.eqeue
    block=block.split("  ")
    ser.eqeue=eval(block[0])
    if ser.add_block(block[1], time.ctime(float(block[2])), int(block[3])):
        ser.save_blockchain()
        subprocess.Popen.kill(p)
        run_mainer()
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