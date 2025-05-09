var prev_block_id=0;
var main_block=document.getElementById("main_block");
var hash=document.getElementById("hash");
var prev_hash=document.getElementById("prev_hash");
var key=document.getElementById("key");
var hash_rate=document.getElementById("hash_rate");
var version=document.getElementById("version");
var header=document.getElementById("header");
var date=document.getElementById("date");
var list_transactions=document.getElementById("list_transactions");

main_block.style.visibility = 'hidden';

function get_block(block_id, ip) {
    if (prev_block_id!=0) {
        let block=document.getElementById(prev_block_id);
        block.classList=document.getElementById(block_id).classList;
    }
    else {
      main_block.style.visibility = 'visible';
    }
    let block=document.getElementById(block_id);
    block.classList.add("active");
    prev_block_id=block_id;
    header.innerText="Блок №"+String(Number(block_id.slice(6))+1);
    let block_hash=document.getElementById(block_id+"_hash");
    block_hash=block_hash.innerText;
    block_hash=block_hash.slice(5);
    let content=http_get_request("get_block/"+block_hash, ip);
    content=JSON.parse(content);
    hash.innerText=content.hash;
    prev_hash.innerText=content.prev_hash;
    key.innerText=content.key;
    hash_rate.innerText=content.hash_rate;
    version.innerText=content.ver;
    date.innerText=content.date;

    list_transactions.innerHTML="";
    console.log(content.data)
    for (i=0; i<content.data.length; i++) {
      let transaction=document.createElement('a');
      transaction.className="list-group-item list-group-item-action py-3 lh-sm";
      list_transactions.append(transaction);
      let date=document.createElement('h1');
      date.className="modal-title fs-5";
      date.style="margin-bottom: 5px;";
      date.innerText=content.data[i].date;
      let amount=document.createElement('div');
      amount.className="col-10 mb-1 small";
      if (content.ver==1) {
        amount.innerText="Кількість "+String(content.data[i].number);
      }
      else {
        amount.innerText="Кількість "+String(content.data[i].amount);
      }

      let sender=document.createElement('div');
      sender.className="col-10 mb-1 small";
      sender.innerText="Надсилач "+String(content.data[i].sender);
      let receiver=document.createElement('div');
      receiver.className="col-10 mb-1 small";
      receiver.innerText="Отримувач "+String(content.data[i].receiver);
      let signature=document.createElement('div');
      signature.className="col-10 mb-1 small";
      signature.innerText="Підпис "+String(content.data[i].signature);
      transaction.append(date);
      transaction.append(amount);
      transaction.append(sender);
      transaction.append(receiver);
      if (content.ver!=1) {
        transaction.append(signature); 
      }
    }
}

function http_get_request(adress, ip) {
    var xmlHttp = new XMLHttpRequest();
    let url="http://"+ip+"/"+adress;
    xmlHttp.open( "GET", url, false );
    xmlHttp.send(null);
    return xmlHttp.responseText;
}