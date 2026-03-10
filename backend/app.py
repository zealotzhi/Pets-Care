"""
宠物临终关怀App - 后端服务主入口
"""
from flask import Flask
from flask_cors import CORS

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    CORS(app)
    
    # 配置
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['UPLOAD_FOLDER'] = 'data'
    
    # 注册蓝图
    from routes import pet_bp, checkup_bp, care_bp
    app.register_blueprint(pet_bp)
    app.register_blueprint(checkup_bp)
    app.register_blueprint(care_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
