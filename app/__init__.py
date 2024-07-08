from flask import Flask
from app.views import main as main_blueprint
import database  

def create_app():
    app = Flask(__name__)
    
    # 设置一个密钥用于加密会话数据
    app.secret_key = 'your_secret_key'
    
    # 注册蓝图
    app.register_blueprint(main_blueprint)
    
    # 初始化数据库
    with app.app_context():
        database.init_db()  # 调用 init_db 函数
    
    return app