"""
AI代理服务
负责统一管理所有AI模型调用，确保服务质量和安全性
使用Trend Micro AI Endpoint API
"""
import os
import json
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timezone

# 配置日志
logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """AI服务调用失败"""
    pass


class AIServiceTimeout(AIServiceError):
    """AI服务超时"""
    pass


class AIProxyService:
    """AI代理服务类"""
    
    def __init__(self, api_url: str = None, api_key: str = None, timeout: int = 30):
        """
        初始化AI代理服务
        
        Args:
            api_url: AI API的URL地址
            api_key: AI API的密钥
            timeout: 请求超时时间（秒）
        """
        # 使用Trend Micro AI Endpoint API
        self.api_url = api_url or os.environ.get('AI_API_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.api_key = api_key or os.environ.get('AI_API_KEY', 'sk-a2dd336e0bf349ffa8a8131649bad650')
        # self.api_url = api_url or os.environ.get('AI_API_URL', 'https://api.rdsec.trendmicro.com/prod/aiendpoint/v1')
        # self.api_key = api_key or os.environ.get('AI_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiQUktMTc2ODgxMDA1NzM4OCIsInJvbGVzIjpbIjM1Il0sInVzZXJfaWQiOjY4NCwidXNlcm5hbWUiOiJaaGlfWmhhbmciLCJyb2xlX25hbWVzIjpbIlJPUC1haWVuZHBvaW50LVVzZXIiXSwidG9rZW5fdHlwZSI6ImFjY2VzcyIsImV4cCI6MTc3NjU4NjA2MSwianRpIjoiZWQ1NDc2ZjItZjUwZC0xMWYwLTg2ZjYtZWExZWRhODUzNjJmIiwidmVyc2lvbiI6IjIwMjQtMTEtMDEifQ.VMbTPyYn6CBWggI-n00qkJKWQ0TE7NWTqkp7Y8tOBXE')
        self.timeout = timeout
        self.model = "qwen-plus"
        # self.model = "gpt-4o"  # 使用GPT-4o模型
        
        # 日志目录
        self.log_dir = 'data/logs'
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _log_ai_call(self, method: str, request_data: Dict, response_data: Dict = None, error: str = None):
        """
        记录AI调用日志
        
        Args:
            method: 调用的方法名
            request_data: 请求数据
            response_data: 响应数据
            error: 错误信息（如果有）
        """
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'method': method,
            'request': request_data,
            'response': response_data,
            'error': error
        }
        
        log_file = os.path.join(self.log_dir, 'ai_calls.log')
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write AI call log: {str(e)}")
    
    def _make_openai_call(self, messages: List[Dict], system_prompt: str = None) -> Dict:
        """
        执行OpenAI兼容的API调用
        
        Args:
            messages: 消息列表
            system_prompt: 系统提示词（可选）
            
        Returns:
            Dict: API响应数据
            
        Raises:
            AIServiceTimeout: 如果请求超时
            AIServiceError: 如果请求失败
        """
        url = f"{self.api_url}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        # 构建消息列表
        formatted_messages = []
        
        # 检查 messages 中是否已经有系统消息
        has_system_message = any(msg.get('role') == 'system' for msg in messages)
        
        # 只有在没有系统消息且提供了 system_prompt 时才添加
        if system_prompt and not has_system_message:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        formatted_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # 检查响应状态
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 408 or response.status_code == 504:
                raise AIServiceTimeout(f"AI服务超时: {response.status_code}")
            else:
                error_text = response.text
                try:
                    error_json = response.json()
                    error_message = error_json.get('error', {}).get('message', error_text)
                except:
                    error_message = error_text
                raise AIServiceError(f"AI服务返回错误: {response.status_code} - {error_message}")
                
        except requests.exceptions.Timeout:
            raise AIServiceTimeout("AI服务请求超时")
        except requests.exceptions.ConnectionError as e:
            raise AIServiceError(f"无法连接到AI服务: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"AI服务请求失败: {str(e)}")
    
    def _extract_response_content(self, response: Dict) -> str:
        """
        从OpenAI响应中提取内容
        
        Args:
            response: OpenAI API响应
            
        Returns:
            str: 提取的内容
        """
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError):
            raise AIServiceError("AI响应格式错误")
    
    def analyze_conversation(
        self, 
        conversation_history: List[Dict],
        media_paths: List[str] = None
    ) -> Dict:
        """
        分析对话历史并生成AI回复
        
        Args:
            conversation_history: 对话历史列表，每个元素包含 role 和 content
            media_paths: 媒体文件路径列表（可选）
            
        Returns:
            Dict: AI回复，包含 content 和可能的 suggestions
            
        Raises:
            AIServiceTimeout: 如果请求超时
            AIServiceError: 如果请求失败
        """
        system_prompt = """你是一位专业的宠物医生助手，正在进行宠物健康咨询。请根据对话历史：

1. 提供专业、温暖的回复
2. 询问相关的健康问题以获得更多信息
3. 如果发现严重症状，建议及时就医
4. 保持关怀和同理心的语调

请以JSON格式回复，包含以下字段：
- content: 你的回复内容
- suggestions: 建议的后续问题列表（最多3个）
- next_question: 下一个重要问题（可选）

示例格式：
{
  "content": "我理解您的担心...",
  "suggestions": ["宠物的食欲如何？", "有没有其他症状？"],
  "next_question": "请描述一下宠物的精神状态"
}"""
        
        try:
            # 调用AI API
            response = self._make_openai_call(conversation_history, system_prompt)
            content = self._extract_response_content(response)
            
            # 尝试解析JSON响应
            try:
                # 首先尝试直接解析
                parsed_content = json.loads(content)
                result = {
                    'content': parsed_content.get('content', content),
                    'suggestions': parsed_content.get('suggestions', []),
                    'next_question': parsed_content.get('next_question', '')
                }
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        json_str = json_match.group(0)
                        parsed_content = json.loads(json_str)
                        result = {
                            'content': parsed_content.get('content', content),
                            'suggestions': parsed_content.get('suggestions', []),
                            'next_question': parsed_content.get('next_question', '')
                        }
                    except json.JSONDecodeError:
                        # 如果还是失败，直接使用内容
                        result = {
                            'content': content,
                            'suggestions': [],
                            'next_question': ''
                        }
                else:
                    # 如果没有找到JSON，直接使用内容
                    result = {
                        'content': content,
                        'suggestions': [],
                        'next_question': ''
                    }
            
            # 记录成功的调用
            self._log_ai_call('analyze_conversation', {
                'conversation_history': conversation_history,
                'media_paths': media_paths
            }, result)
            
            return result
            
        except (AIServiceTimeout, AIServiceError) as e:
            # 记录错误
            self._log_ai_call('analyze_conversation', {
                'conversation_history': conversation_history,
                'media_paths': media_paths
            }, error=str(e))
            raise
    
    def diagnose_checkup(
        self, 
        pet_data: Dict,
        checkup_records: List[Dict],
        media_paths: List[str] = None
    ) -> Dict:
        """
        基于体检数据生成诊断报告
        
        Args:
            pet_data: 宠物基本信息
            checkup_records: 体检记录列表
            media_paths: 媒体文件路径列表（可选）
            
        Returns:
            Dict: 诊断报告，包含健康状态、发现、建议等
            
        Raises:
            AIServiceTimeout: 如果请求超时
            AIServiceError: 如果请求失败
        """
        system_prompt = """你是一位专业的宠物医生，正在分析宠物的体检数据。请根据提供的宠物信息和体检记录：

1. 评估宠物的整体健康状态
2. 识别任何异常或需要关注的问题
3. 提供专业的医疗建议
4. 评估情况的紧急程度

请以JSON格式回复，包含以下字段：
- health_status: 健康状态 (healthy/attention/serious/end-of-life)
- summary: 总体评估摘要
- findings: 主要发现列表
- ai_analysis: 详细分析对象
- recommendations: 建议列表
- urgency: 紧急程度 (low/medium/high/emergency)

示例格式：
{
  "health_status": "attention",
  "summary": "宠物整体状况良好，但需要关注...",
  "findings": ["发现1", "发现2"],
  "ai_analysis": {"详细分析": "内容"},
  "recommendations": ["建议1", "建议2"],
  "urgency": "medium"
}"""
        
        # 构建用户消息
        pet_info = f"""宠物信息：
- 名字：{pet_data.get('name', '未知')}
- 品种：{pet_data.get('breed', '未知')}
- 年龄：{pet_data.get('age', '未知')}岁
- 体重：{pet_data.get('weight', '未知')}kg
- 性别：{pet_data.get('gender', '未知')}
- 当前健康状态：{pet_data.get('health_status', '未知')}

体检记录："""
        
        for i, record in enumerate(checkup_records, 1):
            pet_info += f"""
记录{i}：
- 类别：{record.get('category', '未知')}
- 描述：{record.get('description', '无描述')}
- 严重程度：{record.get('severity', 0)}/5
"""
        
        messages = [{"role": "user", "content": pet_info}]
        
        try:
            # 调用AI API
            response = self._make_openai_call(messages, system_prompt)
            content = self._extract_response_content(response)
            
            # 尝试解析JSON响应
            try:
                parsed_content = json.loads(content)
                result = {
                    'healthStatus': parsed_content.get('health_status', 'unknown'),
                    'summary': parsed_content.get('summary', ''),
                    'findings': parsed_content.get('findings', []),
                    'aiAnalysis': parsed_content.get('ai_analysis', {}),
                    'recommendations': parsed_content.get('recommendations', []),
                    'urgency': parsed_content.get('urgency', 'low')
                }
            except json.JSONDecodeError:
                # 如果不是JSON格式，创建基本结构
                result = {
                    'healthStatus': 'unknown',
                    'summary': content,
                    'findings': [],
                    'aiAnalysis': {'raw_response': content},
                    'recommendations': [],
                    'urgency': 'low'
                }
            
            # 记录成功的调用
            self._log_ai_call('diagnose_checkup', {
                'pet_data': pet_data,
                'checkup_records': checkup_records,
                'media_paths': media_paths
            }, result)
            
            return result
            
        except (AIServiceTimeout, AIServiceError) as e:
            # 记录错误
            self._log_ai_call('diagnose_checkup', {
                'pet_data': pet_data,
                'checkup_records': checkup_records,
                'media_paths': media_paths
            }, error=str(e))
            raise
    
    def generate_care_advice(
        self, 
        pet_data: Dict,
        situation: str
    ) -> Dict:
        """
        生成关怀建议
        
        Args:
            pet_data: 宠物基本信息
            situation: 当前情况描述
            
        Returns:
            Dict: 关怀建议，包含建议内容、紧急程度等
            
        Raises:
            AIServiceTimeout: 如果请求超时
            AIServiceError: 如果请求失败
        """
        system_prompt = """你是一位专业的宠物关怀顾问，专门为宠物主人提供情感支持和实用建议。请根据宠物信息和当前情况：

1. 提供温暖、同理心的关怀建议
2. 给出实用的行动建议
3. 评估情况的紧急程度
4. 如果需要，建议寻求专业帮助

请以JSON格式回复，包含以下字段：
- advice: 主要关怀建议内容
- urgency: 紧急程度 (low/medium/high/emergency)
- recommendations: 具体建议列表
- suggested_actions: 建议的行动列表，每个包含type和description

示例格式：
{
  "advice": "我理解您现在的心情...",
  "urgency": "medium",
  "recommendations": ["建议1", "建议2"],
  "suggested_actions": [
    {"type": "hospital", "description": "联系附近的宠物医院"},
    {"type": "funeral", "description": "了解宠物殡葬服务"}
  ]
}"""
        
        # 构建用户消息
        user_message = f"""宠物信息：
- 名字：{pet_data.get('name', '未知')}
- 品种：{pet_data.get('breed', '未知')}
- 年龄：{pet_data.get('age', '未知')}岁
- 体重：{pet_data.get('weight', '未知')}kg
- 性别：{pet_data.get('gender', '未知')}
- 健康状态：{pet_data.get('health_status', '未知')}

当前情况：
{situation}

请为这种情况提供专业的关怀建议。"""
        
        messages = [{"role": "user", "content": user_message}]
        
        try:
            # 调用AI API
            response = self._make_openai_call(messages, system_prompt)
            content = self._extract_response_content(response)
            
            # 尝试解析JSON响应
            try:
                parsed_content = json.loads(content)
                result = {
                    'advice': parsed_content.get('advice', content),
                    'urgency': parsed_content.get('urgency', 'low'),
                    'recommendations': parsed_content.get('recommendations', []),
                    'suggestedActions': parsed_content.get('suggested_actions', [])
                }
            except json.JSONDecodeError:
                # 如果不是JSON格式，创建基本结构
                result = {
                    'advice': content,
                    'urgency': 'low',
                    'recommendations': [],
                    'suggestedActions': []
                }
            
            # 记录成功的调用
            self._log_ai_call('generate_care_advice', {
                'pet_data': pet_data,
                'situation': situation
            }, result)
            
            return result
            
        except (AIServiceTimeout, AIServiceError) as e:
            # 记录错误
            self._log_ai_call('generate_care_advice', {
                'pet_data': pet_data,
                'situation': situation
            }, error=str(e))
            raise
    
    def analyze_media(self, media_path: str, media_type: str) -> Dict:
        """
        分析图片或视频内容
        
        Args:
            media_path: 媒体文件路径
            media_type: 媒体类型（'image' 或 'video'）
            
        Returns:
            Dict: 分析结果，包含发现和描述
            
        Raises:
            AIServiceTimeout: 如果请求超时
            AIServiceError: 如果请求失败
            ValueError: 如果媒体类型无效
        """
        if media_type not in ['image', 'video']:
            raise ValueError(f"无效的媒体类型: {media_type}")
        
        # 检查文件是否存在
        if not os.path.exists(media_path):
            raise FileNotFoundError(f"媒体文件不存在: {media_path}")
        
        # 注意：当前的GPT-4o模型主要支持图片分析
        # 视频分析可能需要额外的处理
        if media_type == 'video':
            logger.warning("视频分析功能当前受限，建议使用图片")
            return {
                'findings': '视频分析功能当前不可用，请上传图片进行分析',
                'description': '建议截取视频关键帧作为图片上传',
                'concerns': ['视频分析功能受限']
            }
        
        system_prompt = """你是一位专业的宠物医生，正在分析宠物的照片。请仔细观察图片中的宠物：

1. 描述你在图片中看到的内容
2. 识别任何可能的健康问题或异常
3. 提供专业的观察结果
4. 如果发现问题，建议进一步的检查

请以JSON格式回复，包含以下字段：
- findings: 主要发现和观察结果
- description: 对图片内容的详细描述
- concerns: 需要关注的问题列表

示例格式：
{
  "findings": "从图片中可以看到...",
  "description": "图片显示一只...",
  "concerns": ["需要关注的问题1", "需要关注的问题2"]
}"""
        
        try:
            # 对于图片分析，我们需要将图片编码为base64
            # 注意：这里简化处理，实际实现可能需要更复杂的图片处理
            import base64
            
            with open(media_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请分析这张宠物照片，提供专业的医学观察。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }]
            
            # 调用AI API
            response = self._make_openai_call(messages, system_prompt)
            content = self._extract_response_content(response)
            
            # 尝试解析JSON响应
            try:
                parsed_content = json.loads(content)
                result = {
                    'findings': parsed_content.get('findings', content),
                    'description': parsed_content.get('description', ''),
                    'concerns': parsed_content.get('concerns', [])
                }
            except json.JSONDecodeError:
                # 如果不是JSON格式，创建基本结构
                result = {
                    'findings': content,
                    'description': content,
                    'concerns': []
                }
            
            # 记录成功的调用
            self._log_ai_call('analyze_media', {
                'media_path': media_path,
                'media_type': media_type
            }, result)
            
            return result
            
        except (AIServiceTimeout, AIServiceError) as e:
            # 记录错误
            self._log_ai_call('analyze_media', {
                'media_path': media_path,
                'media_type': media_type
            }, error=str(e))
            raise
        except Exception as e:
            # 处理其他错误（如文件读取错误）
            error_msg = f"媒体分析失败: {str(e)}"
            self._log_ai_call('analyze_media', {
                'media_path': media_path,
                'media_type': media_type
            }, error=error_msg)
            raise AIServiceError(error_msg)
