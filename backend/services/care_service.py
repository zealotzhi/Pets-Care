"""
关怀服务
负责提供AI关怀建议和第三方服务对接
"""
import os
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .file_storage_service import FileStorageService
from .ai_proxy_service import AIProxyService, AIServiceError, AIServiceTimeout


class CareService:
    """关怀服务类"""
    
    def __init__(
        self, 
        file_storage_service: FileStorageService,
        ai_proxy_service: AIProxyService
    ):
        """
        初始化关怀服务
        
        Args:
            file_storage_service: 文件存储服务实例
            ai_proxy_service: AI代理服务实例
        """
        self.file_storage = file_storage_service
        self.ai_proxy = ai_proxy_service
        
        # 关怀建议存储目录
        self.care_dir = os.path.join(self.file_storage.base_path, 'care')
        os.makedirs(self.care_dir, exist_ok=True)
    
    def generate_care_advice(
        self, 
        pet_id: str,
        situation: str
    ) -> Dict:
        """
        生成关怀建议
        
        Args:
            pet_id: 宠物ID
            situation: 当前情况描述
            
        Returns:
            Dict: 关怀建议，包含建议内容、紧急程度、推荐行动等
            
        Raises:
            FileNotFoundError: 如果宠物不存在
            ValueError: 如果情况描述为空
            AIServiceError: 如果AI服务调用失败
        """
        # 验证输入
        if not situation or not situation.strip():
            raise ValueError("情况描述不能为空")
        
        # 加载宠物数据
        pet_data = self.file_storage.load_pet_metadata(pet_id)
        
        # 调用AI生成关怀建议
        try:
            ai_response = self.ai_proxy.generate_care_advice(
                pet_data=pet_data,
                situation=situation
            )
            
            # 生成唯一的建议ID
            advice_id = str(uuid.uuid4())
            
            # 构建完整的关怀建议对象
            care_advice = {
                'id': advice_id,
                'petId': pet_id,
                'situation': situation,
                'advice': ai_response.get('advice', ''),
                'urgency': ai_response.get('urgency', 'low'),
                'recommendations': ai_response.get('recommendations', []),
                'suggestedActions': ai_response.get('suggestedActions', []),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # 保存关怀建议到文件
            self._save_care_advice(advice_id, care_advice)
            
            return care_advice
            
        except (AIServiceError, AIServiceTimeout) as e:
            raise AIServiceError(f"生成关怀建议失败: {str(e)}")
    
    def _save_care_advice(self, advice_id: str, care_advice: Dict) -> None:
        """
        保存关怀建议到文件
        
        Args:
            advice_id: 建议ID
            care_advice: 关怀建议数据
            
        Raises:
            IOError: 如果保存失败
        """
        advice_path = os.path.join(self.care_dir, f'{advice_id}.json')
        
        try:
            with open(advice_path, 'w', encoding='utf-8') as f:
                json.dump(care_advice, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"保存关怀建议失败: {str(e)}")
    
    def get_care_advice(self, advice_id: str) -> Dict:
        """
        获取关怀建议
        
        Args:
            advice_id: 建议ID
            
        Returns:
            Dict: 关怀建议数据
            
        Raises:
            FileNotFoundError: 如果建议不存在
        """
        advice_path = os.path.join(self.care_dir, f'{advice_id}.json')
        
        if not os.path.exists(advice_path):
            raise FileNotFoundError(f"关怀建议不存在: {advice_id}")
        
        try:
            with open(advice_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"加载关怀建议失败: {str(e)}")
    
    def get_pet_care_history(self, pet_id: str) -> List[Dict]:
        """
        获取宠物的关怀建议历史
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            List[Dict]: 关怀建议列表，按时间倒序排列
        """
        care_history = []
        
        # 遍历关怀目录中的所有文件
        if not os.path.exists(self.care_dir):
            return care_history
        
        for filename in os.listdir(self.care_dir):
            if filename.endswith('.json'):
                try:
                    advice_path = os.path.join(self.care_dir, filename)
                    with open(advice_path, 'r', encoding='utf-8') as f:
                        advice = json.load(f)
                        
                    # 只返回该宠物的建议
                    if advice.get('petId') == pet_id:
                        care_history.append(advice)
                        
                except Exception:
                    # 跳过无法读取的文件
                    continue
        
        # 按创建时间倒序排列
        care_history.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return care_history
