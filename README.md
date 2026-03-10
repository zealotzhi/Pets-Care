# 宠物临终关怀App

一款面向iOS和Android平台的移动应用，为宠物主人提供便捷的宠物健康管理和临终关怀服务。

## 项目结构

```
pet-end-of-life-care-app/
├── backend/                 # 后端服务
│   ├── app.py              # Flask应用主入口
│   ├── config.py           # 配置文件
│   ├── requirements.txt    # Python依赖
│   ├── services/           # 服务层
│   ├── routes/             # 路由层
│   └── utils/              # 工具函数
├── mobile/                 # 移动端应用
│   ├── main.py            # Kivy应用主入口
│   ├── requirements.txt   # Python依赖
│   ├── buildozer.spec     # Android打包配置
│   ├── managers/          # 管理器层
│   ├── screens/           # 屏幕组件
│   └── utils/             # 工具函数
├── data/                  # 数据存储目录
└── README.md
```

## 技术栈

### 后端
- Python 3.9+
- Flask (Web框架)
- Flask-CORS (跨域支持)
- Pillow (图片处理)
- OpenCV (视频处理)

### 移动端
- Python 3.9+
- Kivy (跨平台UI框架)
- KivyMD (Material Design组件)
- Plyer (跨平台通知)

## 快速开始

### 后端设置

1. 创建虚拟环境：
```bash
cd backend
python -m venv venv
```

2. 激活虚拟环境：
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

5. 运行后端服务：
```bash
python app.py
```

### 移动端设置

1. 创建虚拟环境：
```bash
cd mobile
python -m venv venv
```

2. 激活虚拟环境：
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行移动端应用（开发模式）：
```bash
python main.py
```

### Android打包

```bash
cd mobile
buildozer android debug
```

## 开发指南

详细的开发文档请参考：
- [需求文档](.kiro/specs/pet-end-of-life-care-app/requirements.md)
- [设计文档](.kiro/specs/pet-end-of-life-care-app/design.md)
- [任务列表](.kiro/specs/pet-end-of-life-care-app/tasks.md)

## 许可证

MIT License
