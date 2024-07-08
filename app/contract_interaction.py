from web3 import Web3
import json
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 定义节流时间间隔（单位：秒）
throttle_interval = 10
last_request_time = 0

def load_contract(network):
    """
    Load contract based on the specified network.
    
    :param network: str - The network to connect to ('local', 'sepolia', etc.)
    :return: tuple - (web3 instance, contract instance)
    """
    if network == 'local':
        rpc_url = "http://127.0.0.1:7545"
        chain_id = 5777  # Ganache's default chain ID
    elif network == 'sepolia':
        rpc_url = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}"
        chain_id = 59141  # Linea Sepolia's chain ID
    else:
        raise ValueError("Unsupported network")

    web3 = Web3(Web3.HTTPProvider(rpc_url))

    # 检查连接是否成功
    if not web3.isConnected():
        raise Exception(f"Failed to connect to the {network} network")

    # 加载合约
    with open('build/AuditContract.json') as f:
        contract_json = json.load(f)
        contract_abi = contract_json['abi']
        contract_address = os.getenv('CONTRACT_ADDRESS')

    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    
    return web3, contract, chain_id

def upload_audit_record(network, code_hash, from_address, private_key):
    global last_request_time
    
    web3, contract, chain_id = load_contract(network)
    
    current_time = time.time()
    
    if current_time - last_request_time < throttle_interval:
        # 如果距离上次请求时间不足节流时间间隔，等待剩余时间
        time.sleep(throttle_interval - (current_time - last_request_time))
    
    # 执行请求操作
    nonce = web3.eth.getTransactionCount(from_address)
    txn = contract.functions.uploadAuditRecord(code_hash).buildTransaction({
        'chainId': chain_id,
        'gas': 2000000,
        'gasPrice': web3.toWei('10', 'gwei'),
        'nonce': nonce,
    })
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    
    # 更新上次请求时间
    last_request_time = time.time()
    
    return web3.toHex(tx_hash)



# 示例用法
if __name__ == "__main__":
    # 替换为您的实际参数
    NETWORK = 'local'  # 或 'sepolia'
    CODE_HASH = 'example_code_hash'
    FROM_ADDRESS = os.getenv('FROM_ADDRESS')
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')

    try:
        tx_hash = upload_audit_record(NETWORK, CODE_HASH, FROM_ADDRESS, PRIVATE_KEY)
        print(f"Transaction hash: {tx_hash}")
    except Exception as e:
        print(f"An error occurred: {e}")