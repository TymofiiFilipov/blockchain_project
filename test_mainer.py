import subprocess
import hashlib
import time
import json
import flask
import requests
hash_rate=6
servers=["127.0.0.1:5001"]
my_id="127.0.0.1:5000"

def write(data, filename):
    data=json.dumps(data)
    data=json.loads(str(data))
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def read(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

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
        self.blocks=read("data.json")["blocks"]
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

        write(ans, "data.json")


ser=Blockchain()

def try_to_connect():
    global hash_rate, servers
    try:
        a=requests.get("http://"+servers[0]+"/new_server/"+my_id)
        a=a.text.split("%")
        for i in eval(a[0]):
            if i!=my_id:
                servers.append(i)
        hash_rate=int(a[1])
        b=eval(a[2])
        write(b, "data.json")
        ser.__init__()
        if not ser.check_blockchain():
            print(1)
            servers.pop(0)
            try_to_connect()
    except:
        servers.pop(0)
        if servers!=[]:
            try_to_connect()
        else:
            print("Error connection")

if servers!=[]:
    try_to_connect()

for i in servers:
    try:
        a=requests.get("http://"+i+"/connect_server/"+my_id)
    except:
        pass

p=subprocess.Popen("python3 test_main.py",
                   stdin=None,
                   stdout=None,
                   stderr=None,
                   shell=True)



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
    return str(servers[:len(servers)-1])+"%"+str(hash_rate)+"%"+str(read("data.json"))

@app.route("/found_new_block/<string:block>")
def new_block(block):
    block=block.split()
    ser.eqeue.append({
        "number":1,
        "sender":"0",
        "receiver":"Tim",
        "date":time.ctime(float(block[1]))
    })
    prot_data=ser.eqeue
    if ser.add_block(block[0], time.ctime(float(block[1])), int(block[2])):
        ser.save_blockchain()
        for i in servers:
            a=requests.get("http://"+i+"/found_new_block_an/"+str(prot_data)+"  "+block[0]+"  "+block[1]+"  "+block[2])
    else:
        ser.eqeue=[]

    p=subprocess.Popen("python3 test_main.py",
                    stdin=None,
                    stdout=None,
                    stderr=None,
                    shell=True)
    
    return "OK"

@app.route("/found_new_block_an/<string:block>")
def new_block_an(block):
    a=ser.eqeue
    block=block.split("  ")
    ser.eqeue=eval(block[0])
    print(ser.eqeue)
    if ser.add_block(block[1], time.ctime(float(block[2])), int(block[3])):
        ser.save_blockchain()
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