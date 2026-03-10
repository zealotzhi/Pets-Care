"""
宠物管理服务
负责处理宠物的CRUD操作
"""
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from werkzeug.datastructures import FileStorage

from .file_storage_service import FileStorageService


class PetService:
    """宠物管理服务类"""
    
    def __init__(self, file_storage_service: FileStorageService):
        """
        初始化宠物服务
        
        Args:
            file_storage_service: 文件存储服务实例
        """
        self.file_storage = file_storage_service
    
    def create_pet(self, name: str, photo_file: FileStorage = None, **kwargs) -> Dict:
        """
        创建新宠物记录
        
        Args:
            name: 宠物名字
            photo_file: 宠物照片文件
            **kwargs: 其他可选字段（breed, age, weight, gender等）
            
        Returns:
            Dict: 创建的宠物信息
            
        Raises:
            ValueError: 如果必填字段缺失或无效
            IOError: 如果文件操作失败
        """
        # 验证必填字段
        if not name or not name.strip():
            raise ValueError("宠物名字不能为空")
        
        # 生成唯一的宠物ID
        pet_id = str(uuid.uuid4())
        
        # 保存照片（如果提供）
        photo_path = None
        if photo_file:
            photo_path = self.file_storage.save_pet_photo(pet_id, photo_file)
        
        # 构建宠物元数据
        metadata = {
            'id': pet_id,
            'name': name.strip(),
            'photoPath': photo_path,
            'breed': kwargs.get('breed'),
            'age': kwargs.get('age'),
            'weight': kwargs.get('weight'),
            'gender': kwargs.get('gender'),
            'healthStatus': kwargs.get('healthStatus', 'healthy'),
            'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'lastCheckupAt': None,
            'checkupHistory': []
        }
        
        # 保存元数据
        self.file_storage.save_pet_metadata(pet_id, metadata)
        
        return metadata
    
    def get_pet_list(self) -> List[Dict]:
        """
        获取所有宠物列表
        
        Returns:
            List[Dict]: 宠物信息列表
        """
        pets = []
        pets_dir = os.path.join(self.file_storage.base_path, 'pets')
        
        # 确保目录存在
        if not os.path.exists(pets_dir):
            return pets
        
        # 遍历所有宠物目录
        for pet_id in os.listdir(pets_dir):
            pet_path = os.path.join(pets_dir, pet_id)
            
            # 跳过非目录项
            if not os.path.isdir(pet_path):
                continue
            
            try:
                # 加载宠物元数据
                metadata = self.file_storage.load_pet_metadata(pet_id)
                pets.append(metadata)
            except Exception as e:
                # 记录错误但继续处理其他宠物
                print(f"加载宠物 {pet_id} 失败: {str(e)}")
                continue
        
        # 按创建时间倒序排序
        pets.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return pets
    
    def get_pet_detail(self, pet_id: str) -> Dict:
        """
        获取宠物详细信息
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            Dict: 宠物详细信息
            
        Raises:
            FileNotFoundError: 如果宠物不存在
            IOError: 如果读取失败
        """
        return self.file_storage.load_pet_metadata(pet_id)
    
    def update_pet(self, pet_id: str, updates: Dict) -> Dict:
        """
        更新宠物信息
        
        Args:
            pet_id: 宠物ID
            updates: 要更新的字段字典
            
        Returns:
            Dict: 更新后的宠物信息
            
        Raises:
            FileNotFoundError: 如果宠物不存在
            IOError: 如果操作失败
        """
        # 加载现有元数据
        metadata = self.file_storage.load_pet_metadata(pet_id)
        
        # 更新允许修改的字段
        updatable_fields = ['name', 'breed', 'age', 'weight', 'gender', 'healthStatus']
        for field in updatable_fields:
            if field in updates:
                # 特殊处理name字段，不允许为空
                if field == 'name':
                    if not updates[field] or not updates[field].strip():
                        raise ValueError("宠物名字不能为空")
                    metadata[field] = updates[field].strip()
                else:
                    metadata[field] = updates[field]
        
        # 保存更新后的元数据
        self.file_storage.save_pet_metadata(pet_id, metadata)
        
        return metadata
    
    def delete_pet(self, pet_id: str) -> None:
        """
        删除宠物记录
        
        Args:
            pet_id: 宠物ID
            
        Raises:
            FileNotFoundError: 如果宠物不存在
            IOError: 如果删除失败
        """
        # 先检查宠物是否存在
        self.file_storage.load_pet_metadata(pet_id)
        
        # 删除所有相关文件
        self.file_storage.delete_pet_files(pet_id)
    
    def update_last_checkup(self, pet_id: str, checkup_session_id: str) -> None:
        """
        更新宠物的最后体检时间和历史记录
        
        Args:
            pet_id: 宠物ID
            checkup_session_id: 体检会话ID
            
        Raises:
            FileNotFoundError: 如果宠物不存在
            IOError: 如果操作失败
        """
        metadata = self.file_storage.load_pet_metadata(pet_id)
        
        # 更新最后体检时间
        metadata['lastCheckupAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # 添加到体检历史
        if 'checkupHistory' not in metadata:
            metadata['checkupHistory'] = []
        
        if checkup_session_id not in metadata['checkupHistory']:
            metadata['checkupHistory'].append(checkup_session_id)
        
        # 保存更新
        self.file_storage.save_pet_metadata(pet_id, metadata)
