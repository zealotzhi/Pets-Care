"""
体检管理服务
负责管理虚拟体检会话和记录
"""
import os
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from werkzeug.datastructures import FileStorage

from .file_storage_service import FileStorageService
from .ai_proxy_service import AIProxyService, AIServiceError, AIServiceTimeout


class CheckupService:
    """体检管理服务类"""
    
    def __init__(
        self, 
        file_storage_service: FileStorageService,
        ai_proxy_service: AIProxyService
    ):
        """
        初始化体检服务
        
        Args:
            file_storage_service: 文件存储服务实例
            ai_proxy_service: AI代理服务实例
        """
        self.file_storage = file_storage_service
        self.ai_proxy = ai_proxy_service
    
    def create_conversation_session(self, pet_id: str) -> Dict:
        """
        创建对话式体检会话
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            Dict: 创建的会话信息，包含初始AI问候
            
        Raises:
            FileNotFoundError: 如果宠物不存在
            AIServiceError: 如果AI服务调用失败
        """
        # 验证宠物是否存在
        pet_metadata = self.file_storage.load_pet_metadata(pet_id)
        
        # 生成唯一的会话ID
        session_id = str(uuid.uuid4())
        
        # 创建初始会话数据
        session_data = {
            'id': session_id,
            'petId': pet_id,
            'type': 'conversation',
            'status': 'in-progress',
            'startedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'completedAt': None,
            'messages': []
        }
        
        # 生成初始AI问候
        try:
            initial_prompt = self._generate_initial_prompt(pet_metadata)
            ai_response = self.ai_proxy.analyze_conversation(
                conversation_history=[{
                    'role': 'system',
                    'content': initial_prompt
                }],
                media_paths=[]
            )
            
            # 添加AI的初始消息
            initial_message = {
                'id': str(uuid.uuid4()),
                'role': 'ai',
                'content': ai_response.get('content', '你好！我是AI医生，让我们开始体检吧。请描述一下宠物最近的状况。'),
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            session_data['messages'].append(initial_message)
            
        except (AIServiceError, AIServiceTimeout) as e:
            # 如果AI服务失败，使用默认问候
            initial_message = {
                'id': str(uuid.uuid4()),
                'role': 'ai',
                'content': f'你好！我是AI医生，让我们开始为{pet_metadata.get("name", "您的宠物")}进行体检。请描述一下最近的进食、排泄、活动和精神状态。',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            session_data['messages'].append(initial_message)
        
        # 保存会话数据
        self.file_storage.save_checkup_session(session_id, pet_id, session_data)
        
        return {
            'sessionId': session_id,
            'petId': pet_id,
            'status': 'in-progress',
            'initialMessage': initial_message
        }
    
    def process_conversation_message(
        self, 
        session_id: str,
        pet_id: str,
        message: str, 
        media_file: Optional[FileStorage] = None
    ) -> Dict:
        """
        处理对话消息并获取AI回复
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            message: 用户消息内容
            media_file: 可选的媒体文件
            
        Returns:
            Dict: AI回复消息
            
        Raises:
            FileNotFoundError: 如果会话不存在
            ValueError: 如果会话已完成
            AIServiceError: 如果AI服务调用失败
        """
        # 加载会话数据
        session_data = self.file_storage.load_checkup_session(session_id, pet_id)
        
        # 检查会话状态
        if session_data.get('status') == 'completed':
            raise ValueError("体检会话已完成，无法继续对话")
        
        # 处理媒体文件
        media_path = None
        if media_file:
            media_path = self.file_storage.save_checkup_media(
                session_id, pet_id, media_file
            )
        
        # 添加用户消息
        user_message = {
            'id': str(uuid.uuid4()),
            'role': 'user',
            'content': message,
            'mediaPath': media_path,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        session_data['messages'].append(user_message)
        
        # 准备对话历史
        conversation_history = []
        media_paths = []
        
        for msg in session_data['messages']:
            # 将 'ai' 角色转换为 'assistant'
            role = 'assistant' if msg['role'] == 'ai' else msg['role']
            conversation_history.append({
                'role': role,
                'content': msg['content']
            })
            if msg.get('mediaPath'):
                media_paths.append(msg['mediaPath'])
        
        # 调用AI分析对话
        try:
            ai_response = self.ai_proxy.analyze_conversation(
                conversation_history=conversation_history,
                media_paths=media_paths
            )
            
            # 添加AI回复消息
            ai_message = {
                'id': str(uuid.uuid4()),
                'role': 'ai',
                'content': ai_response.get('content', ''),
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            session_data['messages'].append(ai_message)
            
            # 保存更新后的会话数据
            self.file_storage.save_checkup_session(session_id, pet_id, session_data)
            
            return {
                'messageId': ai_message['id'],
                'content': ai_message['content'],
                'timestamp': ai_message['timestamp'],
                'suggestions': ai_response.get('suggestions', [])
            }
            
        except (AIServiceError, AIServiceTimeout) as e:
            # AI服务失败时返回更详细的错误信息
            error_content = f"AI分析遇到问题: {str(e)}。不过我仍然可以为您提供一些基本建议。"
            
            # 根据用户输入提供基本建议
            user_content = message.lower()
            basic_advice = self._generate_basic_advice(user_content)
            
            error_message = {
                'id': str(uuid.uuid4()),
                'role': 'ai',
                'content': f"{error_content}\n\n{basic_advice}",
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            session_data['messages'].append(error_message)
            self.file_storage.save_checkup_session(session_id, pet_id, session_data)
            
            # 返回错误消息而不是抛出异常
            return {
                'messageId': error_message['id'],
                'content': error_message['content'],
                'timestamp': error_message['timestamp'],
                'suggestions': ['建议尽快就医', '观察宠物状态', '记录症状变化'],
                'error': str(e)
            }
    
    def complete_checkup(self, session_id: str, pet_id: str) -> Dict:
        """
        完成体检并生成报告
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            
        Returns:
            Dict: 体检报告
            
        Raises:
            FileNotFoundError: 如果会话不存在
            ValueError: 如果会话已完成
            AIServiceError: 如果AI服务调用失败
        """
        # 加载会话数据
        session_data = self.file_storage.load_checkup_session(session_id, pet_id)
        
        # 检查会话状态
        if session_data.get('status') == 'completed':
            raise ValueError("体检会话已完成")
        
        # 加载宠物数据
        pet_data = self.file_storage.load_pet_metadata(pet_id)
        
        # 从对话中提取体检记录
        checkup_records = self._extract_checkup_records_from_conversation(
            session_data['messages']
        )
        
        # 收集所有媒体文件路径
        media_paths = []
        for msg in session_data['messages']:
            if msg.get('mediaPath'):
                media_paths.append(msg['mediaPath'])
        
        # 调用AI生成诊断报告
        try:
            diagnosis = self.ai_proxy.diagnose_checkup(
                pet_data=pet_data,
                checkup_records=checkup_records,
                media_paths=media_paths
            )
            
            # 构建完整的体检报告
            report = {
                'sessionId': session_id,
                'petId': pet_id,
                'generatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'healthStatus': diagnosis.get('healthStatus', 'unknown'),
                'summary': diagnosis.get('summary', ''),
                'findings': diagnosis.get('findings', []),
                'aiAnalysis': diagnosis.get('aiAnalysis', {}),
                'recommendations': diagnosis.get('recommendations', []),
                'urgency': diagnosis.get('urgency', 'low')
            }
            
            # 保存报告
            self._save_checkup_report(session_id, pet_id, report)
            
            # 更新会话状态
            session_data['status'] = 'completed'
            session_data['completedAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            self.file_storage.save_checkup_session(session_id, pet_id, session_data)
            
            # 更新宠物的健康状态和最后体检时间
            self._update_pet_health_status(pet_id, report['healthStatus'], session_id)
            
            return report
            
        except (AIServiceError, AIServiceTimeout) as e:
            raise AIServiceError(f"生成体检报告失败: {str(e)}")
    
    def _generate_initial_prompt(self, pet_metadata: Dict) -> str:
        """生成初始AI提示"""
        pet_name = pet_metadata.get('name', '宠物')
        pet_info = []
        
        if pet_metadata.get('breed'):
            pet_info.append(f"品种：{pet_metadata['breed']}")
        if pet_metadata.get('age'):
            pet_info.append(f"年龄：{pet_metadata['age']}岁")
        if pet_metadata.get('gender'):
            gender_text = '公' if pet_metadata['gender'] == 'male' else '母'
            pet_info.append(f"性别：{gender_text}")
        
        info_text = '，'.join(pet_info) if pet_info else ''
        
        prompt = f"""你是一位专业的宠物医生，正在为名叫{pet_name}的宠物进行虚拟体检。
{info_text}

请用温暖、专业的语气与宠物主人对话，引导他们描述宠物的健康状况。
重点询问：进食、饮水、排泄、活动、精神状态、身体状况等方面。
如果主人提供照片或视频，请仔细分析并给出专业意见。"""
        
        return prompt
    
    def _extract_checkup_records_from_conversation(
        self, 
        messages: List[Dict]
    ) -> List[Dict]:
        """从对话中提取体检记录"""
        records = []
        
        # 简单提取：将用户的每条消息作为一条记录
        for msg in messages:
            if msg['role'] == 'user':
                records.append({
                    'category': 'conversation',
                    'description': msg['content'],
                    'severity': 3,  # 默认中等严重程度
                    'mediaPaths': [msg['mediaPath']] if msg.get('mediaPath') else []
                })
        
        return records
    
    def _save_checkup_report(
        self, 
        session_id: str, 
        pet_id: str, 
        report: Dict
    ) -> None:
        """保存体检报告"""
        session_dir = os.path.join(
            self.file_storage.base_path, 
            'pets', 
            pet_id, 
            'checkups', 
            session_id
        )
        report_path = os.path.join(session_dir, 'report.json')
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"保存体检报告失败: {str(e)}")
    
    def _generate_basic_advice(self, user_input: str) -> str:
        """根据用户输入生成基本建议"""
        advice_map = {
            '拉肚子': '建议：1) 暂时禁食12-24小时，但要保证充足饮水；2) 观察是否有血便或其他症状；3) 如果持续超过24小时请及时就医。',
            '呕吐': '建议：1) 暂时禁食4-6小时；2) 少量多次给水；3) 观察呕吐物颜色和频率；4) 如果持续呕吐请立即就医。',
            '不吃饭': '建议：1) 检查食物是否新鲜；2) 尝试更换食物或加热食物；3) 观察是否有其他症状；4) 超过24小时不进食请就医。',
            '咳嗽': '建议：1) 保持环境湿润；2) 避免刺激性气味；3) 观察咳嗽频率和是否有痰；4) 持续咳嗽请及时就医。',
            '发烧': '建议：1) 立即就医，发烧可能是严重疾病的征象；2) 在就医前保持宠物安静；3) 不要自行给药。',
            '精神不振': '建议：1) 观察食欲和饮水情况；2) 检查是否有其他症状；3) 提供安静舒适的环境；4) 如果持续请就医。'
        }
        
        for keyword, advice in advice_map.items():
            if keyword in user_input:
                return advice
        
        return '建议：1) 仔细观察宠物的症状变化；2) 记录症状的时间和严重程度；3) 如果症状持续或加重，请及时联系专业兽医。'
    
    def _update_pet_health_status(
        self, 
        pet_id: str, 
        health_status: str,
        session_id: str
    ) -> None:
        """更新宠物健康状态"""
        pet_metadata = self.file_storage.load_pet_metadata(pet_id)
        
        # 更新健康状态
        pet_metadata['healthStatus'] = health_status
        pet_metadata['lastCheckupAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # 添加到体检历史
        if 'checkupHistory' not in pet_metadata:
            pet_metadata['checkupHistory'] = []
        
        if session_id not in pet_metadata['checkupHistory']:
            pet_metadata['checkupHistory'].append(session_id)
        
        # 保存更新
        self.file_storage.save_pet_metadata(pet_id, pet_metadata)
    
    def create_scheduled_session(self, pet_id: str) -> Dict:
        """
        创建定期体检会话
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            Dict: 创建的会话信息
            
        Raises:
            FileNotFoundError: 如果宠物不存在
        """
        # 验证宠物是否存在
        pet_metadata = self.file_storage.load_pet_metadata(pet_id)
        
        # 生成唯一的会话ID
        session_id = str(uuid.uuid4())
        
        # 创建初始会话数据
        session_data = {
            'id': session_id,
            'petId': pet_id,
            'type': 'scheduled',
            'status': 'in-progress',
            'startedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'completedAt': None,
            'records': []
        }
        
        # 保存会话数据
        self.file_storage.save_checkup_session(session_id, pet_id, session_data)
        
        return {
            'sessionId': session_id,
            'petId': pet_id,
            'status': 'in-progress',
            'categories': ['feeding', 'drinking', 'excretion', 'activity', 'behavior', 'body']
        }
    
    def save_checkup_record(
        self, 
        session_id: str,
        pet_id: str,
        record: Dict
    ) -> None:
        """
        保存体检记录
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            record: 体检记录，包含 category, description, severity, media_files
            
        Raises:
            FileNotFoundError: 如果会话不存在
            ValueError: 如果会话已完成或记录数据无效
        """
        # 加载会话数据
        session_data = self.file_storage.load_checkup_session(session_id, pet_id)
        
        # 检查会话状态
        if session_data.get('status') == 'completed':
            raise ValueError("体检会话已完成，无法添加记录")
        
        # 验证记录数据
        required_fields = ['category', 'description', 'severity']
        for field in required_fields:
            if field not in record:
                raise ValueError(f"缺少必填字段: {field}")
        
        # 验证类别
        valid_categories = ['feeding', 'drinking', 'excretion', 'activity', 'behavior', 'body']
        if record['category'] not in valid_categories:
            raise ValueError(f"无效的体检类别: {record['category']}")
        
        # 验证严重程度
        if not isinstance(record['severity'], int) or record['severity'] < 1 or record['severity'] > 5:
            raise ValueError("严重程度必须是1-5之间的整数")
        
        # 处理媒体文件
        media_paths = []
        if 'media_files' in record and record['media_files']:
            for media_file in record['media_files']:
                media_path = self.file_storage.save_checkup_media(
                    session_id, pet_id, media_file
                )
                media_paths.append(media_path)
        
        # 构建记录对象
        checkup_record = {
            'id': str(uuid.uuid4()),
            'category': record['category'],
            'description': record['description'],
            'severity': record['severity'],
            'mediaPaths': media_paths,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # 添加到会话记录
        session_data['records'].append(checkup_record)
        
        # 保存更新后的会话数据
        self.file_storage.save_checkup_session(session_id, pet_id, session_data)
    
    def complete_scheduled_checkup(self, session_id: str, pet_id: str) -> Dict:
        """
        完成定期体检并生成报告
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            
        Returns:
            Dict: 体检报告
            
        Raises:
            FileNotFoundError: 如果会话不存在
            ValueError: 如果会话已完成或没有记录
            AIServiceError: 如果AI服务调用失败
        """
        # 加载会话数据
        session_data = self.file_storage.load_checkup_session(session_id, pet_id)
        
        # 检查会话状态
        if session_data.get('status') == 'completed':
            raise ValueError("体检会话已完成")
        
        # 检查是否有记录
        if not session_data.get('records'):
            raise ValueError("体检会话没有任何记录，无法生成报告")
        
        # 加载宠物数据
        pet_data = self.file_storage.load_pet_metadata(pet_id)
        
        # 收集所有媒体文件路径
        media_paths = []
        for record in session_data['records']:
            if record.get('mediaPaths'):
                media_paths.extend(record['mediaPaths'])
        
        # 调用AI生成诊断报告
        try:
            diagnosis = self.ai_proxy.diagnose_checkup(
                pet_data=pet_data,
                checkup_records=session_data['records'],
                media_paths=media_paths
            )
            
            # 构建完整的体检报告
            report = {
                'sessionId': session_id,
                'petId': pet_id,
                'generatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'healthStatus': diagnosis.get('healthStatus', 'unknown'),
                'summary': diagnosis.get('summary', ''),
                'findings': diagnosis.get('findings', []),
                'aiAnalysis': diagnosis.get('aiAnalysis', {}),
                'recommendations': diagnosis.get('recommendations', []),
                'urgency': diagnosis.get('urgency', 'low')
            }
            
            # 保存报告
            self._save_checkup_report(session_id, pet_id, report)
            
            # 更新会话状态
            session_data['status'] = 'completed'
            session_data['completedAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            self.file_storage.save_checkup_session(session_id, pet_id, session_data)
            
            # 更新宠物的健康状态和最后体检时间
            self._update_pet_health_status(pet_id, report['healthStatus'], session_id)
            
            return report
            
        except (AIServiceError, AIServiceTimeout) as e:
            raise AIServiceError(f"生成体检报告失败: {str(e)}")
    
    def get_checkup_report(self, session_id: str, pet_id: str) -> Dict:
        """
        获取体检报告
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            
        Returns:
            Dict: 体检报告
            
        Raises:
            FileNotFoundError: 如果报告不存在
        """
        report_path = os.path.join(
            self.file_storage.base_path,
            'pets',
            pet_id,
            'checkups',
            session_id,
            'report.json'
        )
        
        if not os.path.exists(report_path):
            raise FileNotFoundError(f"体检报告不存在")
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"加载体检报告失败: {str(e)}")
