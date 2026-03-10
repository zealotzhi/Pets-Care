"""
关怀服务相关的API路由
"""
import logging
from flask import Blueprint, request, jsonify

from services.file_storage_service import FileStorageService
from services.ai_proxy_service import AIProxyService, AIServiceError, AIServiceTimeout
from services.care_service import CareService

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
care_bp = Blueprint('care', __name__, url_prefix='/api/care')

# 初始化服务
file_storage_service = FileStorageService()
ai_proxy_service = AIProxyService(
    api_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key='sk-a2dd336e0bf349ffa8a8131649bad650',
    timeout=30
)
care_service = CareService(file_storage_service, ai_proxy_service)


@care_bp.route('/advice', methods=['POST'])
def get_care_advice():
    """
    获取AI关怀建议
    
    请求体:
        {
            "petId": "宠物ID",
            "situation": "当前情况描述"
        }
    
    响应:
        {
            "id": "建议ID",
            "petId": "宠物ID",
            "situation": "情况描述",
            "advice": "AI建议内容",
            "urgency": "紧急程度 (low/medium/high/emergency)",
            "recommendations": ["建议1", "建议2"],
            "suggestedActions": [
                {
                    "type": "hospital/funeral",
                    "description": "行动描述"
                }
            ],
            "createdAt": "创建时间"
        }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'message': '请求体不能为空',
                'code': 400
            }), 400
        
        pet_id = data.get('petId')
        situation = data.get('situation')
        
        # 验证必填字段
        if not pet_id:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'petId',
                'message': '宠物ID不能为空',
                'code': 400
            }), 400
        
        if not situation:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'situation',
                'message': '情况描述不能为空',
                'code': 400
            }), 400
        
        # 生成关怀建议
        result = care_service.generate_care_advice(
            pet_id=pet_id,
            situation=situation
        )
        
        return jsonify(result), 201
        
    except FileNotFoundError as e:
        logger.error(f"Pet not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '宠物不存在',
            'code': 404
        }), 404
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': 'VALIDATION_ERROR',
            'message': str(e),
            'code': 400
        }), 400
        
    except AIServiceTimeout:
        logger.error("AI service timeout")
        return jsonify({
            'error': 'AI_TIMEOUT',
            'message': 'AI服务超时，请稍后重试',
            'code': 504
        }), 504
        
    except AIServiceError as e:
        logger.error(f"AI service error: {str(e)}")
        return jsonify({
            'error': 'AI_ERROR',
            'message': 'AI服务暂时不可用，建议联系专业医生',
            'code': 503
        }), 503
        
    except Exception as e:
        logger.error(f"Failed to generate care advice: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '生成关怀建议失败',
            'code': 500
        }), 500


@care_bp.route('/advice/<advice_id>', methods=['GET'])
def get_advice_by_id(advice_id):
    """
    根据ID获取关怀建议
    
    路径参数:
        advice_id: 建议ID
    
    响应:
        {
            "id": "建议ID",
            "petId": "宠物ID",
            "situation": "情况描述",
            "advice": "AI建议内容",
            "urgency": "紧急程度",
            "recommendations": [...],
            "suggestedActions": [...],
            "createdAt": "创建时间"
        }
    """
    try:
        # 获取建议
        advice = care_service.get_care_advice(advice_id)
        
        return jsonify(advice), 200
        
    except FileNotFoundError as e:
        logger.error(f"Advice not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '关怀建议不存在',
            'code': 404
        }), 404
        
    except Exception as e:
        logger.error(f"Failed to get advice: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '获取关怀建议失败',
            'code': 500
        }), 500


@care_bp.route('/history/<pet_id>', methods=['GET'])
def get_care_history(pet_id):
    """
    获取宠物的关怀建议历史
    
    路径参数:
        pet_id: 宠物ID
    
    响应:
        {
            "petId": "宠物ID",
            "history": [
                {
                    "id": "建议ID",
                    "situation": "情况描述",
                    "advice": "AI建议内容",
                    "urgency": "紧急程度",
                    "createdAt": "创建时间"
                },
                ...
            ]
        }
    """
    try:
        # 获取关怀历史
        history = care_service.get_pet_care_history(pet_id)
        
        return jsonify({
            'petId': pet_id,
            'history': history
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get care history: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '获取关怀历史失败',
            'code': 500
        }), 500


@care_bp.route('/hospitals', methods=['GET'])
def get_nearby_hospitals():
    """
    获取附近的宠物医院
    
    查询参数:
        latitude: 纬度
        longitude: 经度
    
    响应:
        {
            "hospitals": [
                {
                    "id": "医院ID",
                    "type": "hospital",
                    "name": "医院名称",
                    "address": "地址",
                    "phone": "电话",
                    "distance": 距离(km),
                    "rating": 评分,
                    "openHours": "营业时间"
                },
                ...
            ]
        }
    
    注意: 此端点当前返回模拟数据，实际实现需要对接第三方服务
    """
    try:
        # 获取查询参数
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        
        # 验证参数
        if latitude is None or longitude is None:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'message': '纬度和经度不能为空',
                'code': 400
            }), 400
        
        # TODO: 实际实现需要调用第三方服务API
        # 当前返回模拟数据
        hospitals = [
            {
                'id': 'hospital_001',
                'type': 'hospital',
                'name': '爱宠动物医院',
                'address': '北京市朝阳区XX路XX号',
                'phone': '010-12345678',
                'distance': 1.5,
                'rating': 4.5,
                'openHours': '09:00-21:00',
                'services': ['急诊', '手术', '体检']
            },
            {
                'id': 'hospital_002',
                'type': 'hospital',
                'name': '宠物健康中心',
                'address': '北京市海淀区YY路YY号',
                'phone': '010-87654321',
                'distance': 2.3,
                'rating': 4.2,
                'openHours': '08:00-20:00',
                'services': ['体检', '疫苗', '美容']
            }
        ]
        
        return jsonify({
            'hospitals': hospitals
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get hospitals: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '获取医院列表失败',
            'code': 500
        }), 500


@care_bp.route('/funeral-services', methods=['GET'])
def get_funeral_services():
    """
    获取殡葬服务提供商
    
    查询参数:
        latitude: 纬度
        longitude: 经度
    
    响应:
        {
            "services": [
                {
                    "id": "服务ID",
                    "type": "funeral",
                    "name": "服务名称",
                    "address": "地址",
                    "phone": "电话",
                    "distance": 距离(km),
                    "rating": 评分,
                    "services": ["火化", "安葬", "纪念品"]
                },
                ...
            ]
        }
    
    注意: 此端点当前返回模拟数据，实际实现需要对接第三方服务
    """
    try:
        # 获取查询参数
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        
        # 验证参数
        if latitude is None or longitude is None:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'message': '纬度和经度不能为空',
                'code': 400
            }), 400
        
        # TODO: 实际实现需要调用第三方服务API
        # 当前返回模拟数据
        services = [
            {
                'id': 'funeral_001',
                'type': 'funeral',
                'name': '宠物天堂殡葬服务',
                'address': '北京市昌平区ZZ路ZZ号',
                'phone': '010-11112222',
                'distance': 5.2,
                'rating': 4.8,
                'services': ['火化', '安葬', '纪念品', '告别仪式']
            },
            {
                'id': 'funeral_002',
                'type': 'funeral',
                'name': '彩虹桥宠物殡葬',
                'address': '北京市顺义区AA路AA号',
                'phone': '010-33334444',
                'distance': 8.7,
                'rating': 4.6,
                'services': ['火化', '骨灰盒', '纪念照']
            }
        ]
        
        return jsonify({
            'services': services
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get funeral services: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '获取殡葬服务列表失败',
            'code': 500
        }), 500
