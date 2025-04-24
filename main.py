import hashlib
import time
import json
hash_rate=5

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


date=time.ctime(time.time())
ser=Blockchain()

while True:
    ans=ser.get_last_block().hash[:hash_rate]
    prev_hash=ser.get_last_block().hash
    run=True
    ser.eqeue.append({
        "number":1,
        "sender":"0",
        "receiver":"Tim",
        "data":time.ctime(time.time())
        })
    check_sum=hashlib.sha256(str(ser.eqeue).encode()).hexdigest()
    i=0
    while run:
        if hashlib.sha256((str(date)+str(prev_hash)+str(check_sum)+str(i)).encode()).hexdigest()[64-hash_rate:]==ans:
            ser.add_block(hashlib.sha256((str(date)+str(prev_hash)+str(check_sum)+str(i)).encode()).hexdigest(), date, i)
            ser.save_blockchain()
            print(len(ser.blocks), ser.check_blockchain())
            run=False
        i+=1
    date=time.ctime(time.time())