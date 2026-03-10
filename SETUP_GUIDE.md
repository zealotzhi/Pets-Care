# 项目设置指南

## 前置要求

- Python 3.9 或更高版本
- pip (Python包管理器)
- Git

## Windows快速设置

### 方式一：使用自动化脚本

1. **设置后端**
   ```cmd
   setup_backend.bat
   ```

2. **设置移动端**
   ```cmd
   setup_mobile.bat
   ```

### 方式二：手动设置

#### 后端设置

1. 进入后端目录：
   ```cmd
   cd backend
   ```

2. 创建虚拟环境：
   ```cmd
   python -m venv venv
   ```

3. 激活虚拟环境：
   ```cmd
   venv\Scripts\activate
   ```

4. 安装依赖：
   ```cmd
   pip install -r requirements.txt
   ```

5. 创建数据目录：
   ```cmd
   mkdir data
   mkdir data\pets
   mkdir data\care
   mkdir data\logs
   ```

6. 配置环境变量：
   ```cmd
   copy .env.example .env
   ```
   然后编辑 `.env` 文件，填入实际配置值。

7. 运行后端服务：
   ```cmd
   python app.py
   ```

#### 移动端设置

1. 进入移动端目录：
   ```cmd
   cd mobile
   ```

2. 创建虚拟环境：
   ```cmd
   python -m venv venv
   ```

3. 激活虚拟环境：
   ```cmd
   venv\Scripts\activate
   ```

4. 安装依赖：
   ```cmd
   pip install -r requirements.txt
   ```

5. 运行移动端应用：
   ```cmd
   python main.py
   ```

## Linux/Mac设置

### 后端设置

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p data/pets data/care data/logs
cp .env.example .env
# 编辑 .env 文件
python app.py
```

### 移动端设置

```bash
cd mobile
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 验证安装

### 验证后端

1. 激活后端虚拟环境
2. 运行测试：
   ```cmd
   pytest
   ```

### 验证移动端

1. 激活移动端虚拟环境
2. 运行测试：
   ```cmd
   pytest
   ```

## 常见问题

### 问题：pip install 失败

**解决方案**：
- 确保Python版本 >= 3.9
- 尝试升级pip：`python -m pip install --upgrade pip`
- 如果是网络问题，使用国内镜像：
  ```cmd
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 问题：Kivy安装失败

**解决方案**：
- Windows用户可能需要安装Visual C++ Build Tools
- 参考Kivy官方文档：https://kivy.org/doc/stable/gettingstarted/installation.html

### 问题：虚拟环境激活失败

**解决方案**：
- Windows PowerShell可能需要修改执行策略：
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 下一步

设置完成后，请参考以下文档继续开发：

- [需求文档](.kiro/specs/pet-end-of-life-care-app/requirements.md)
- [设计文档](.kiro/specs/pet-end-of-life-care-app/design.md)
- [任务列表](.kiro/specs/pet-end-of-life-care-app/tasks.md)
