"""
文件存储服务
负责管理宠物信息、照片、视频等文件的存储和检索
"""
import os
import json
import uuid
import shutil
from typing import Dict, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class FileStorageService:
    """文件存储服务类"""
    
    def __init__(self, base_path: str = 'data'):
        """
        初始化文件存储服务
        
        Args:
            base_path: 数据存储的基础路径
        """
        self.base_path = base_path
        self._ensure_base_directories()
    
    def _ensure_base_directories(self):
        """确保基础目录结构存在"""
        directories = [
            self.base_path,
            os.path.join(self.base_path, 'pets'),
            os.path.join(self.base_path, 'care'),
            os.path.join(self.base_path, 'logs')
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _ensure_pet_directory(self, pet_id: str):
        """确保宠物目录存在"""
        pet_dir = os.path.join(self.base_path, 'pets', pet_id)
        checkups_dir = os.path.join(pet_dir, 'checkups')
        os.makedirs(pet_dir, exist_ok=True)
        os.makedirs(checkups_dir, exist_ok=True)
        return pet_dir
    
    def _ensure_checkup_directory(self, pet_id: str, session_id: str):
        """确保体检会话目录存在"""
        session_dir = os.path.join(
            self.base_path, 'pets', pet_id, 'checkups', session_id
        )
        media_dir = os.path.join(session_dir, 'media')
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(media_dir, exist_ok=True)
        return session_dir
    
    def save_pet_photo(self, pet_id: str, photo_file: FileStorage) -> str:
        """
        保存宠物照片并返回文件路径
        
        Args:
            pet_id: 宠物ID
            photo_file: 照片文件对象
            
        Returns:
            str: 保存后的文件路径
            
        Raises:
            ValueError: 如果文件类型不支持
            IOError: 如果文件保存失败
        """
        if not photo_file:
            raise ValueError("照片文件不能为空")
        
        # 验证文件类型
        filename = secure_filename(photo_file.filename)
        if not self._is_valid_image(filename):
            raise ValueError("不支持的图片格式，请上传 jpg, jpeg, png 或 gif 文件")
        
        # 确保目录存在
        pet_dir = self._ensure_pet_directory(pet_id)
        
        # 保存文件
        file_ext = os.path.splitext(filename)[1]
        file_path = os.path.join(pet_dir, f'photo{file_ext}')
        
        try:
            photo_file.save(file_path)
            return file_path
        except Exception as e:
            raise IOError(f"保存照片失败: {str(e)}")
    
    def save_checkup_media(
        self, 
        session_id: str, 
        pet_id: str,
        media_file: FileStorage
    ) -> str:
        """
        保存体检媒体文件并返回文件路径
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            media_file: 媒体文件对象
            
        Returns:
            str: 保存后的文件路径
            
        Raises:
            ValueError: 如果文件类型不支持
            IOError: 如果文件保存失败
        """
        if not media_file:
            raise ValueError("媒体文件不能为空")
        
        # 验证文件类型
        filename = secure_filename(media_file.filename)
        if not self._is_valid_media(filename):
            raise ValueError("不支持的媒体格式")
        
        # 确保目录存在
        session_dir = self._ensure_checkup_directory(pet_id, session_id)
        media_dir = os.path.join(session_dir, 'media')
        
        # 生成唯一文件名
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f'{uuid.uuid4().hex}{file_ext}'
        file_path = os.path.join(media_dir, unique_filename)
        
        try:
            media_file.save(file_path)
            return file_path
        except Exception as e:
            raise IOError(f"保存媒体文件失败: {str(e)}")
    
    def save_pet_metadata(self, pet_id: str, metadata: Dict) -> None:
        """
        保存宠物元数据到JSON文件
        
        Args:
            pet_id: 宠物ID
            metadata: 宠物元数据字典
            
        Raises:
            IOError: 如果文件保存失败
        """
        pet_dir = self._ensure_pet_directory(pet_id)
        metadata_path = os.path.join(pet_dir, 'metadata.json')
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"保存宠物元数据失败: {str(e)}")
    
    def load_pet_metadata(self, pet_id: str) -> Dict:
        """
        从JSON文件加载宠物元数据
        
        Args:
            pet_id: 宠物ID
            
        Returns:
            Dict: 宠物元数据字典
            
        Raises:
            FileNotFoundError: 如果文件不存在
            IOError: 如果文件读取失败
        """
        metadata_path = os.path.join(
            self.base_path, 'pets', pet_id, 'metadata.json'
        )
        
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"宠物 {pet_id} 的元数据不存在")
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"加载宠物元数据失败: {str(e)}")
    
    def save_checkup_session(self, session_id: str, pet_id: str, session_data: Dict) -> None:
        """
        保存体检会话数据
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            session_data: 体检会话数据字典
            
        Raises:
            IOError: 如果文件保存失败
        """
        session_dir = self._ensure_checkup_directory(pet_id, session_id)
        session_path = os.path.join(session_dir, 'session.json')
        
        try:
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"保存体检会话数据失败: {str(e)}")
    
    def load_checkup_session(self, session_id: str, pet_id: str) -> Dict:
        """
        加载体检会话数据
        
        Args:
            session_id: 体检会话ID
            pet_id: 宠物ID
            
        Returns:
            Dict: 体检会话数据字典
            
        Raises:
            FileNotFoundError: 如果文件不存在
            IOError: 如果文件读取失败
        """
        session_path = os.path.join(
            self.base_path, 'pets', pet_id, 'checkups', session_id, 'session.json'
        )
        
        if not os.path.exists(session_path):
            raise FileNotFoundError(f"体检会话 {session_id} 的数据不存在")
        
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"加载体检会话数据失败: {str(e)}")
    
    def delete_pet_files(self, pet_id: str) -> None:
        """
        删除宠物相关的所有文件
        
        Args:
            pet_id: 宠物ID
            
        Raises:
            IOError: 如果删除失败
        """
        pet_dir = os.path.join(self.base_path, 'pets', pet_id)
        
        if not os.path.exists(pet_dir):
            return  # 目录不存在，无需删除
        
        try:
            shutil.rmtree(pet_dir)
        except Exception as e:
            raise IOError(f"删除宠物文件失败: {str(e)}")
    
    def _is_valid_image(self, filename: str) -> bool:
        """验证是否为有效的图片文件"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        ext = os.path.splitext(filename)[1].lower()
        return ext in allowed_extensions
    
    def _is_valid_media(self, filename: str) -> bool:
        """验证是否为有效的媒体文件（图片或视频）"""
        allowed_extensions = {
            '.jpg', '.jpeg', '.png', '.gif',  # 图片
            '.mp4', '.mov', '.avi', '.mkv'     # 视频
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext in allowed_extensions
