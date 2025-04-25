import time
import hashlib
import requests
import sys

parent_server=sys.argv[1]
date=time.ctime(time.time())
date_out=time.time()
a=requests.get(f"http://{parent_server}/get_info")
a=a.text.split()
prev_hash=a[0]
hash_rate=int(a[1])
data=eval(requests.get(f"http://{parent_server}/get_eqeue/mainer").text.encode())

ans=prev_hash[:hash_rate]
run=True
check_sum=hashlib.sha256(str(data).encode()).hexdigest()
i=0
while run:
    if hashlib.sha256((str(date)+str(prev_hash)+str(check_sum)+str(i)).encode()).hexdigest()[64-hash_rate:]==ans:
        res=str(hashlib.sha256((str(date)+str(prev_hash)+str(check_sum)+str(i)).encode()).hexdigest())+" "+str(date_out)+" "+str(i)
        a=requests.get(f"http://{parent_server}/found_new_block/"+res)
        run=False
    i+=1