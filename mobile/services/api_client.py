"""
API客户端 - 处理与后端的通信
"""
import requests
import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            
            # 记录请求日志
            logger.info(f"{method} {url} - Status: {response.status_code}")
            
            # 检查响应状态
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise APIError(
                        status_code=response.status_code,
                        error_type=error_data.get('error', 'UNKNOWN_ERROR'),
                        message=error_data.get('message', 'Unknown error'),
                        field=error_data.get('field')
                    )
                except json.JSONDecodeError:
                    raise APIError(
                        status_code=response.status_code,
                        error_type='HTTP_ERROR',
                        message=f'HTTP {response.status_code}: {response.reason}'
                    )
            
            # 返回JSON响应
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise APIError(
                status_code=0,
                error_type='CONNECTION_ERROR',
                message='无法连接到服务器，请检查网络连接'
            )
        except requests.exceptions.Timeout:
            raise APIError(
                status_code=0,
                error_type='TIMEOUT_ERROR',
                message='请求超时，请稍后重试'
            )
        except requests.exceptions.RequestException as e:
            raise APIError(
                status_code=0,
                error_type='REQUEST_ERROR',
                message=f'请求失败: {str(e)}'
            )
    
    # ========== 宠物管理API ==========
    
    def create_pet(self, name: str, photo_file=None, **optional_fields) -> Dict[str, Any]:
        """创建宠物"""
        # 准备数据
        data = {'name': name}
        data.update(optional_fields)
        
        # 如果有照片，使用multipart/form-data
        if photo_file:
            files = {'photo': photo_file}
            
            # 临时移除Content-Type头，让requests自动设置multipart
            headers = self.session.headers.copy()
            if 'Content-Type' in self.session.headers:
                del self.session.headers['Content-Type']
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/pets",
                    files=files,
                    data=data,
                    timeout=30
                )
            finally:
                # 恢复原来的headers
                self.session.headers.update(headers)
        else:
            # 没有照片，使用JSON
            response = self.session.post(
                f"{self.base_url}/api/pets",
                json=data,
                timeout=30
            )
        
        if response.status_code >= 400:
            try:
                error_data = response.json()
                raise APIError(
                    status_code=response.status_code,
                    error_type=error_data.get('error', 'UNKNOWN_ERROR'),
                    message=error_data.get('message', 'Unknown error'),
                    field=error_data.get('field')
                )
            except json.JSONDecodeError:
                raise APIError(
                    status_code=response.status_code,
                    error_type='HTTP_ERROR',
                    message=f'HTTP {response.status_code}: {response.reason}'
                )
        
        return response.json()
    
    def get_pet_list(self) -> Dict[str, Any]:
        """获取宠物列表"""
        return self._make_request('GET', '/api/pets')
    
    def get_pet_detail(self, pet_id: str) -> Dict[str, Any]:
        """获取宠物详情"""
        return self._make_request('GET', f'/api/pets/{pet_id}')
    
    def update_pet(self, pet_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新宠物信息"""
        return self._make_request('PUT', f'/api/pets/{pet_id}', json=updates)
    
    def delete_pet(self, pet_id: str) -> None:
        """删除宠物"""
        self._make_request('DELETE', f'/api/pets/{pet_id}')
    
    # ========== 体检API ==========
    
    def create_conversation_session(self, pet_id: str) -> Dict[str, Any]:
        """创建对话式体检会话"""
        return self._make_request('POST', '/api/checkups/conversation', json={'petId': pet_id})
    
    def send_checkup_message(self, session_id: str, pet_id: str, message: str, media_file=None) -> Dict[str, Any]:
        """发送体检对话消息"""
        # 准备multipart/form-data
        data = {
            'petId': pet_id,
            'message': message
        }
        
        files = {}
        if media_file:
            files['media'] = media_file
        
        # 临时移除Content-Type头
        headers = self.session.headers.copy()
        if 'Content-Type' in self.session.headers:
            del self.session.headers['Content-Type']
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/checkups/{session_id}/messages",
                data=data,
                files=files if files else None,
                timeout=30
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise APIError(
                        status_code=response.status_code,
                        error_type=error_data.get('error', 'UNKNOWN_ERROR'),
                        message=error_data.get('message', 'Unknown error'),
                        field=error_data.get('field')
                    )
                except json.JSONDecodeError:
                    raise APIError(
                        status_code=response.status_code,
                        error_type='HTTP_ERROR',
                        message=f'HTTP {response.status_code}: {response.reason}'
                    )
            
            return response.json()
            
        finally:
            # 恢复原来的headers
            self.session.headers.update(headers)
    
    def complete_checkup(self, session_id: str, pet_id: str) -> Dict[str, Any]:
        """完成体检并生成报告"""
        return self._make_request('POST', f'/api/checkups/{session_id}/complete', json={'petId': pet_id})
    
    def get_checkup_report(self, session_id: str, pet_id: str) -> Dict[str, Any]:
        """获取体检报告"""
        return self._make_request('GET', f'/api/checkups/{session_id}/report', params={'petId': pet_id})
    
    def create_scheduled_session(self, pet_id: str) -> Dict[str, Any]:
        """创建定期体检会话"""
        return self._make_request('POST', '/api/checkups/scheduled', json={'petId': pet_id})
    
    def submit_checkup_record(self, session_id: str, pet_id: str, category: str, 
                            description: str, severity: int, media_files: List = None) -> Dict[str, Any]:
        """提交体检记录"""
        data = {
            'petId': pet_id,
            'category': category,
            'description': description,
            'severity': str(severity)
        }
        
        files = {}
        if media_files:
            files['media'] = media_files
        
        # 临时移除Content-Type头
        headers = self.session.headers.copy()
        if 'Content-Type' in self.session.headers:
            del self.session.headers['Content-Type']
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/checkups/{session_id}/records",
                data=data,
                files=files if files else None,
                timeout=30
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise APIError(
                        status_code=response.status_code,
                        error_type=error_data.get('error', 'UNKNOWN_ERROR'),
                        message=error_data.get('message', 'Unknown error'),
                        field=error_data.get('field')
                    )
                except json.JSONDecodeError:
                    raise APIError(
                        status_code=response.status_code,
                        error_type='HTTP_ERROR',
                        message=f'HTTP {response.status_code}: {response.reason}'
                    )
            
            return response.json()
            
        finally:
            # 恢复原来的headers
            self.session.headers.update(headers)
    
    # ========== 关怀服务API ==========
    
    def get_care_advice(self, pet_id: str, situation: str) -> Dict[str, Any]:
        """获取AI关怀建议"""
        return self._make_request('POST', '/api/care/advice', json={
            'petId': pet_id,
            'situation': situation
        })
    
    def get_advice_by_id(self, advice_id: str) -> Dict[str, Any]:
        """根据ID获取关怀建议"""
        return self._make_request('GET', f'/api/care/advice/{advice_id}')
    
    def get_care_history(self, pet_id: str) -> Dict[str, Any]:
        """获取宠物的关怀建议历史"""
        return self._make_request('GET', f'/api/care/history/{pet_id}')
    
    def get_nearby_hospitals(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """获取附近的宠物医院"""
        return self._make_request('GET', '/api/care/hospitals', params={
            'latitude': latitude,
            'longitude': longitude
        })
    
    def get_funeral_services(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """获取殡葬服务提供商"""
        return self._make_request('GET', '/api/care/funeral-services', params={
            'latitude': latitude,
            'longitude': longitude
        })


class APIError(Exception):
    """API错误异常"""
    
    def __init__(self, status_code: int, error_type: str, message: str, field: Optional[str] = None):
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.field = field
        super().__init__(self.message)
    
    def __str__(self):
        if self.field:
            return f"{self.message} (字段: {self.field})"
        return self.message
    
    def is_validation_error(self) -> bool:
        """是否为验证错误"""
        return self.error_type == 'VALIDATION_ERROR'
    
    def is_not_found_error(self) -> bool:
        """是否为资源不存在错误"""
        return self.error_type == 'NOT_FOUND'
    
    def is_connection_error(self) -> bool:
        """是否为连接错误"""
        return self.error_type == 'CONNECTION_ERROR'
    
    def is_timeout_error(self) -> bool:
        """是否为超时错误"""
        return self.error_type == 'TIMEOUT_ERROR'


# 全局API客户端实例
api_client = APIClient()