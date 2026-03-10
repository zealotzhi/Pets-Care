"""
宠物管理API路由
"""
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest

from services import FileStorageService, PetService


# 创建蓝图
pet_bp = Blueprint('pets', __name__, url_prefix='/api/pets')

# 初始化服务
file_storage_service = FileStorageService()
pet_service = PetService(file_storage_service)


@pet_bp.route('', methods=['POST'])
def create_pet():
    """
    创建宠物
    
    POST /api/pets
    
    支持两种格式：
    1. multipart/form-data (带照片)
    2. application/json (仅基本信息)
    
    Form Data / JSON:
        name: 宠物名字 (required)
        photo: 宠物照片文件 (optional, 仅multipart)
        breed: 品种 (optional)
        age: 年龄 (optional)
        weight: 体重 (optional)
        gender: 性别 (optional)
    
    Returns:
        201: 创建成功，返回宠物信息
        400: 请求参数错误
        500: 服务器错误
    """
    try:
        # 检查请求类型
        is_multipart = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_multipart:
            # multipart/form-data 请求（可能包含照片）
            name = request.form.get('name')
            photo_file = request.files.get('photo')
            
            # 获取可选字段
            optional_fields = {}
            if request.form.get('breed'):
                optional_fields['breed'] = request.form.get('breed')
            if request.form.get('age'):
                try:
                    optional_fields['age'] = int(request.form.get('age'))
                except ValueError:
                    return jsonify({
                        'error': 'VALIDATION_ERROR',
                        'field': 'age',
                        'message': '年龄必须是数字'
                    }), 400
            if request.form.get('weight'):
                try:
                    optional_fields['weight'] = float(request.form.get('weight'))
                except ValueError:
                    return jsonify({
                        'error': 'VALIDATION_ERROR',
                        'field': 'weight',
                        'message': '体重必须是数字'
                    }), 400
            if request.form.get('gender'):
                gender = request.form.get('gender')
                if gender not in ['male', 'female']:
                    return jsonify({
                        'error': 'VALIDATION_ERROR',
                        'field': 'gender',
                        'message': '性别必须是 male 或 female'
                    }), 400
                optional_fields['gender'] = gender
        else:
            # JSON 请求（仅基本信息）
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'VALIDATION_ERROR',
                    'message': '请求体不能为空'
                }), 400
            
            name = data.get('name')
            photo_file = None
            
            # 获取可选字段
            optional_fields = {}
            if data.get('breed'):
                optional_fields['breed'] = data.get('breed')
            if data.get('age'):
                if not isinstance(data.get('age'), int):
                    return jsonify({
                        'error': 'VALIDATION_ERROR',
                        'field': 'age',
                        'message': '年龄必须是数字'
                    }), 400
                optional_fields['age'] = data.get('age')
            if data.get('weight'):
                if not isinstance(data.get('weight'), (int, float)):
                    return jsonify({
                        'error': 'VALIDATION_ERROR',
                        'field': 'weight',
                        'message': '体重必须是数字'
                    }), 400
                optional_fields['weight'] = data.get('weight')
            if data.get('gender'):
                gender = data.get('gender')
                if gender not in ['male', 'female']:
                    return jsonify({
                        'error': 'VALIDATION_ERROR',
                        'field': 'gender',
                        'message': '性别必须是 male 或 female'
                    }), 400
                optional_fields['gender'] = gender
        
        # 验证必填字段
        if not name:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'name',
                'message': '宠物名字不能为空'
            }), 400
        
        # 照片现在是可选的
        
        # 创建宠物
        pet = pet_service.create_pet(name, photo_file, **optional_fields)
        
        return jsonify(pet), 201
        
    except ValueError as e:
        return jsonify({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except IOError as e:
        return jsonify({
            'error': 'FILE_SYSTEM_ERROR',
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '创建宠物失败，请稍后重试'
        }), 500


@pet_bp.route('', methods=['GET'])
def get_pet_list():
    """
    获取宠物列表
    
    GET /api/pets
    
    Returns:
        200: 成功，返回宠物列表
        500: 服务器错误
    """
    try:
        pets = pet_service.get_pet_list()
        return jsonify({
            'pets': pets,
            'total': len(pets)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '获取宠物列表失败，请稍后重试'
        }), 500


@pet_bp.route('/<pet_id>', methods=['GET'])
def get_pet_detail(pet_id):
    """
    获取宠物详情
    
    GET /api/pets/{pet_id}
    
    Args:
        pet_id: 宠物ID
    
    Returns:
        200: 成功，返回宠物详情
        404: 宠物不存在
        500: 服务器错误
    """
    try:
        pet = pet_service.get_pet_detail(pet_id)
        return jsonify(pet), 200
        
    except FileNotFoundError:
        return jsonify({
            'error': 'NOT_FOUND',
            'message': f'宠物 {pet_id} 不存在'
        }), 404
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '获取宠物详情失败，请稍后重试'
        }), 500


@pet_bp.route('/<pet_id>', methods=['PUT'])
def update_pet(pet_id):
    """
    更新宠物信息
    
    PUT /api/pets/{pet_id}
    
    Args:
        pet_id: 宠物ID
    
    JSON Body:
        name: 宠物名字 (optional)
        breed: 品种 (optional)
        age: 年龄 (optional)
        weight: 体重 (optional)
        gender: 性别 (optional)
        healthStatus: 健康状态 (optional)
    
    Returns:
        200: 更新成功，返回更新后的宠物信息
        400: 请求参数错误
        404: 宠物不存在
        500: 服务器错误
    """
    try:
        # 获取JSON数据
        updates = request.get_json()
        
        if not updates:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'message': '请提供要更新的字段'
            }), 400
        
        # 验证字段类型
        if 'age' in updates:
            if not isinstance(updates['age'], (int, type(None))):
                return jsonify({
                    'error': 'VALIDATION_ERROR',
                    'field': 'age',
                    'message': '年龄必须是数字'
                }), 400
        
        if 'weight' in updates:
            if not isinstance(updates['weight'], (int, float, type(None))):
                return jsonify({
                    'error': 'VALIDATION_ERROR',
                    'field': 'weight',
                    'message': '体重必须是数字'
                }), 400
        
        if 'gender' in updates:
            if updates['gender'] not in ['male', 'female', None]:
                return jsonify({
                    'error': 'VALIDATION_ERROR',
                    'field': 'gender',
                    'message': '性别必须是 male 或 female'
                }), 400
        
        if 'healthStatus' in updates:
            valid_statuses = ['healthy', 'attention', 'serious', 'end-of-life']
            if updates['healthStatus'] not in valid_statuses:
                return jsonify({
                    'error': 'VALIDATION_ERROR',
                    'field': 'healthStatus',
                    'message': f'健康状态必须是 {", ".join(valid_statuses)} 之一'
                }), 400
        
        # 更新宠物
        pet = pet_service.update_pet(pet_id, updates)
        
        return jsonify(pet), 200
        
    except FileNotFoundError:
        return jsonify({
            'error': 'NOT_FOUND',
            'message': f'宠物 {pet_id} 不存在'
        }), 404
    except ValueError as e:
        return jsonify({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except IOError as e:
        return jsonify({
            'error': 'FILE_SYSTEM_ERROR',
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '更新宠物信息失败，请稍后重试'
        }), 500


@pet_bp.route('/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    """
    删除宠物
    
    DELETE /api/pets/{pet_id}
    
    Args:
        pet_id: 宠物ID
    
    Returns:
        204: 删除成功
        404: 宠物不存在
        500: 服务器错误
    """
    try:
        pet_service.delete_pet(pet_id)
        return '', 204
        
    except FileNotFoundError:
        return jsonify({
            'error': 'NOT_FOUND',
            'message': f'宠物 {pet_id} 不存在'
        }), 404
    except IOError as e:
        return jsonify({
            'error': 'FILE_SYSTEM_ERROR',
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '删除宠物失败，请稍后重试'
        }), 500
