from web3 import Web3
import json
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 连接到 Linea Sepolia 测试网络
infura_url = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}"
web3 = Web3(Web3.HTTPProvider(infura_url))

# 检查连接是否成功
if not web3.isConnected():
    raise Exception("Failed to connect to the network")

# 加载合约
with open('contracts/AuditContract.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract_address = os.getenv('CONTRACT_ADDRESS')
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


# 定义节流时间间隔（单位：秒）
throttle_interval = 10
last_request_time = 0

def upload_audit_record(code_hash, from_address, private_key):
    global last_request_time
    
    current_time = time.time()
    
    if current_time - last_request_time < throttle_interval:
        # 如果距离上次请求时间不足节流时间间隔，等待剩余时间
        time.sleep(throttle_interval - (current_time - last_request_time))
    
    # 执行请求操作
    nonce = web3.eth.getTransactionCount(from_address)
    txn = contract.functions.uploadAuditRecord(code_hash).buildTransaction({
        'chainId': 59141,  # Linea Sepolia 测试网络的链ID
        'gas': 2000000,
        'gasPrice': web3.toWei('10', 'gwei'),
        'nonce': nonce,
    })
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    
    # 更新上次请求时间
    last_request_time = time.time()
    
    return web3.toHex(tx_hash)