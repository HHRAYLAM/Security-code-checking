from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
import io
import requests
import os
import logging
from web3 import Web3
from dotenv import load_dotenv
from utils.pdf_utils import generate_pdf
from contract_interaction import upload_audit_record

# 加载环境变量
load_dotenv()
api = os.getenv('API_TOKEN')
from_address = os.getenv('FROM_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
developer_wallet_address = os.getenv('DEVELOPER_WALLET_ADDRESS')

# 配置 Web3 连接
infura_url = f"https://lineasepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}"
web3 = Web3(Web3.HTTPProvider(infura_url))

# 配置日志
logging.basicConfig(level=logging.DEBUG)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', developer_wallet_address=developer_wallet_address)

@main.route('/upload', methods=['POST'])
def upload_file():
    try:
        # 检查用户是否已经转账
        user_wallet_address = request.form.get('wallet_address')
        if not user_wallet_address or not has_transferred(user_wallet_address):
            flash('Please transfer the required amount to the developer\'s wallet address before using the service.')
            return redirect(url_for('main.index'))
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('main.index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('main.index'))
        
        if file:
            logging.debug("File received: %s", file.filename)
            
            # 使用内存存储文件内容
            file_content = file.read()
            file_stream = io.BytesIO(file_content)
            
            # 调用模型进行代码审核
            audit_result = audit_code(file_stream)
            
            # 确认大模型正确调用
            if isinstance(audit_result, dict):
                logging.debug("Audit result: %s", audit_result)
                
                # 生成 PDF 文件
                pdf = generate_pdf(file.filename, audit_result)
                
                # 上传审计记录到区块链
                code_hash = "示例代码哈希"  # 你可以根据实际情况生成代码哈希
                tx_hash = upload_audit_record(code_hash, from_address, private_key)
                logging.debug("Transaction hash: %s", tx_hash)
                
                # 发送 PDF 文件到客户端
                return send_file(pdf, as_attachment=True, download_name=f"{file.filename}_audit.pdf")
            else:
                logging.error("Audit error: %s", audit_result)
                return jsonify({"error": audit_result}), 500
    except Exception as e:
        logging.exception("An error occurred during file upload")
        return jsonify({"error": str(e)}), 500

def audit_code(file_stream):
    """
    Function to call the Hugging Face model for code auditing.
    """
    API_URL  = "https://api-inference.huggingface.co/models/aiplanet/panda-coder-13B"
    headers = {"Authorization": f"Bearer {api}"}
    
    try:
        # Read file content
        file_content = file_stream.read().decode('utf-8')
        
        # Build payload
        payload = {
            "inputs": f"Please audit the security of the following code and indicate any potential security vulnerabilities or improvement suggestions:\n\n{file_content}"
        }
        
        # Call the Hugging Face API
        response = requests.post(API_URL , headers=headers, json=payload)
        
        logging.debug("Response status code: %s", response.status_code)
        logging.debug("Response text: %s", response.text)
        
        if response.status_code == 200:
            audit_result = response.json()
        else:
            audit_result = f"Error: {response.status_code}, {response.text}"
        
        return audit_result
    except Exception as e:
        logging.exception("An error occurred during audit code")
        return str(e)

def has_transferred(user_wallet_address):
    """
    Function to check if the user has transferred the required amount to the developer's wallet.
    """
    min_transfer_amount = Web3.toWei(0.01, 'ether')  # 设置最小转账金额
    
    # 获取用户的交易历史
    user_transactions = web3.eth.get_block('latest')['transactions']
    
    for tx_hash in user_transactions:
        tx = web3.eth.get_transaction(tx_hash)
        if tx['from'] == user_wallet_address and tx['to'] == developer_wallet_address and tx['value'] >= min_transfer_amount:
            return True
    
    return False