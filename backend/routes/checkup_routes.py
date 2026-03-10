"""
体检相关的API路由
"""
import logging
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest

from services.file_storage_service import FileStorageService
from services.ai_proxy_service import AIProxyService, AIServiceError, AIServiceTimeout
from services.checkup_service import CheckupService

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
checkup_bp = Blueprint('checkup', __name__, url_prefix='/api/checkups')

# 初始化服务
file_storage_service = FileStorageService()
ai_proxy_service = AIProxyService(
    api_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
    api_key='sk-a2dd336e0bf349ffa8a8131649bad650',
    timeout=30
)
checkup_service = CheckupService(file_storage_service, ai_proxy_service)


@checkup_bp.route('/conversation', methods=['POST'])
def create_conversation_session():
    """
    创建对话式体检会话
    
    请求体:
        {
            "petId": "宠物ID"
        }
    
    响应:
        {
            "sessionId": "会话ID",
            "petId": "宠物ID",
            "status": "in-progress",
            "initialMessage": {
                "id": "消息ID",
                "role": "ai",
                "content": "初始问候内容",
                "timestamp": "时间戳"
            }
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
        
        # 验证必填字段
        if not pet_id:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'petId',
                'message': '宠物ID不能为空',
                'code': 400
            }), 400
        
        # 创建会话
        result = checkup_service.create_conversation_session(pet_id)
        
        return jsonify(result), 201
        
    except FileNotFoundError as e:
        logger.error(f"Pet not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '宠物不存在',
            'code': 404
        }), 404
        
    except (AIServiceError, AIServiceTimeout) as e:
        logger.error(f"AI service error: {str(e)}")
        # 即使AI服务失败，会话也已创建，返回成功
        return jsonify({
            'error': 'AI_SERVICE_WARNING',
            'message': 'AI服务暂时不可用，使用默认问候',
            'code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to create conversation session: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '创建体检会话失败',
            'code': 500
        }), 500


@checkup_bp.route('/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """
    发送对话消息
    
    路径参数:
        session_id: 会话ID
    
    请求体 (multipart/form-data):
        petId: 宠物ID
        message: 消息内容
        media: 媒体文件（可选）
    
    响应:
        {
            "messageId": "消息ID",
            "content": "AI回复内容",
            "timestamp": "时间戳",
            "suggestions": ["建议1", "建议2"]
        }
    """
    try:
        # 获取表单数据
        pet_id = request.form.get('petId')
        message = request.form.get('message')
        media_file = request.files.get('media')
        
        # 验证必填字段
        if not pet_id:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'petId',
                'message': '宠物ID不能为空',
                'code': 400
            }), 400
        
        if not message:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'message',
                'message': '消息内容不能为空',
                'code': 400
            }), 400
        
        # 处理消息
        result = checkup_service.process_conversation_message(
            session_id=session_id,
            pet_id=pet_id,
            message=message,
            media_file=media_file
        )
        
        return jsonify(result), 200
        
    except FileNotFoundError as e:
        logger.error(f"Session or pet not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '体检会话或宠物不存在',
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
            'message': 'AI分析超时，请稍后重试',
            'code': 504
        }), 504
        
    except AIServiceError as e:
        logger.error(f"AI service error: {str(e)}")
        return jsonify({
            'error': 'AI_ERROR',
            'message': 'AI服务暂时不可用，请稍后重试',
            'code': 503
        }), 503
        
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '处理消息失败',
            'code': 500
        }), 500


@checkup_bp.route('/<session_id>/complete', methods=['POST'])
def complete_checkup(session_id):
    """
    完成体检并生成报告
    
    路径参数:
        session_id: 会话ID
    
    请求体:
        {
            "petId": "宠物ID"
        }
    
    响应:
        {
            "sessionId": "会话ID",
            "petId": "宠物ID",
            "generatedAt": "生成时间",
            "healthStatus": "健康状态",
            "summary": "摘要",
            "findings": [...],
            "aiAnalysis": {...},
            "recommendations": [...],
            "urgency": "紧急程度"
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
        
        # 验证必填字段
        if not pet_id:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'petId',
                'message': '宠物ID不能为空',
                'code': 400
            }), 400
        
        # 加载会话数据以确定类型
        session_data = checkup_service.file_storage.load_checkup_session(session_id, pet_id)
        session_type = session_data.get('type', 'conversation')
        
        # 根据类型调用不同的完成方法
        if session_type == 'scheduled':
            report = checkup_service.complete_scheduled_checkup(session_id, pet_id)
        else:
            report = checkup_service.complete_checkup(session_id, pet_id)
        
        return jsonify(report), 200
        
    except FileNotFoundError as e:
        logger.error(f"Session or pet not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '体检会话或宠物不存在',
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
            'message': 'AI诊断超时，请稍后重试',
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
        logger.error(f"Failed to complete checkup: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '完成体检失败',
            'code': 500
        }), 500


@checkup_bp.route('/<session_id>/report', methods=['GET'])
def get_checkup_report(session_id):
    """
    获取体检报告
    
    路径参数:
        session_id: 会话ID
    
    查询参数:
        petId: 宠物ID
    
    响应:
        {
            "sessionId": "会话ID",
            "petId": "宠物ID",
            "generatedAt": "生成时间",
            "healthStatus": "健康状态",
            "summary": "摘要",
            "findings": [...],
            "aiAnalysis": {...},
            "recommendations": [...],
            "urgency": "紧急程度"
        }
    """
    try:
        # 获取查询参数
        pet_id = request.args.get('petId')
        
        # 验证必填字段
        if not pet_id:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'petId',
                'message': '宠物ID不能为空',
                'code': 400
            }), 400
        
        # 获取报告
        report = checkup_service.get_checkup_report(session_id, pet_id)
        
        return jsonify(report), 200
        
    except FileNotFoundError as e:
        logger.error(f"Report not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '体检报告不存在',
            'code': 404
        }), 404
        
    except Exception as e:
        logger.error(f"Failed to get report: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '获取体检报告失败',
            'code': 500
        }), 500


@checkup_bp.route('/scheduled', methods=['POST'])
def create_scheduled_session():
    """
    创建定期体检会话
    
    请求体:
        {
            "petId": "宠物ID"
        }
    
    响应:
        {
            "sessionId": "会话ID",
            "petId": "宠物ID",
            "status": "in-progress",
            "categories": ["feeding", "drinking", "excretion", "activity", "behavior", "body"]
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
        
        # 验证必填字段
        if not pet_id:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'petId',
                'message': '宠物ID不能为空',
                'code': 400
            }), 400
        
        # 创建会话
        result = checkup_service.create_scheduled_session(pet_id)
        
        return jsonify(result), 201
        
    except FileNotFoundError as e:
        logger.error(f"Pet not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '宠物不存在',
            'code': 404
        }), 404
        
    except Exception as e:
        logger.error(f"Failed to create scheduled session: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '创建定期体检会话失败',
            'code': 500
        }), 500


@checkup_bp.route('/<session_id>/records', methods=['POST'])
def submit_checkup_record(session_id):
    """
    提交体检记录
    
    路径参数:
        session_id: 会话ID
    
    请求体 (multipart/form-data):
        petId: 宠物ID
        category: 体检类别 (feeding/drinking/excretion/activity/behavior/body)
        description: 描述
        severity: 严重程度 (1-5)
        media: 媒体文件（可选，可多个）
    
    响应:
        {
            "message": "体检记录已保存",
            "recordId": "记录ID"
        }
    """
    try:
        # 获取表单数据
        pet_id = request.form.get('petId')
        category = request.form.get('category')
        description = request.form.get('description')
        severity = request.form.get('severity')
        
        # 验证必填字段
        if not pet_id:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'petId',
                'message': '宠物ID不能为空',
                'code': 400
            }), 400
        
        if not category:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'category',
                'message': '体检类别不能为空',
                'code': 400
            }), 400
        
        if not description:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'description',
                'message': '描述不能为空',
                'code': 400
            }), 400
        
        if not severity:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'severity',
                'message': '严重程度不能为空',
                'code': 400
            }), 400
        
        # 转换严重程度为整数
        try:
            severity = int(severity)
        except ValueError:
            return jsonify({
                'error': 'VALIDATION_ERROR',
                'field': 'severity',
                'message': '严重程度必须是整数',
                'code': 400
            }), 400
        
        # 获取媒体文件（可能有多个）
        media_files = request.files.getlist('media')
        
        # 构建记录对象
        record = {
            'category': category,
            'description': description,
            'severity': severity,
            'media_files': media_files if media_files else []
        }
        
        # 保存记录
        checkup_service.save_checkup_record(session_id, pet_id, record)
        
        return jsonify({
            'message': '体检记录已保存',
            'sessionId': session_id
        }), 201
        
    except FileNotFoundError as e:
        logger.error(f"Session or pet not found: {str(e)}")
        return jsonify({
            'error': 'NOT_FOUND',
            'message': '体检会话或宠物不存在',
            'code': 404
        }), 404
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': 'VALIDATION_ERROR',
            'message': str(e),
            'code': 400
        }), 400
        
    except Exception as e:
        logger.error(f"Failed to save checkup record: {str(e)}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': '保存体检记录失败',
            'code': 500
        }), 500
