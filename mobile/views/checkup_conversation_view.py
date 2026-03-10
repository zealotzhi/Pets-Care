"""
对话式体检页面视图
"""
import flet as ft
import asyncio
from theme.app_theme import AppTheme, IconConfig
from services.api_client import api_client, APIError


class CheckupConversationView(ft.View):
    """对话式体检页面视图"""
    
    def __init__(self, page: ft.Page, app, pet_id=None, **kwargs):
        self._page = page
        self.app = app
        self.pet_id = pet_id
        self.session_id = None
        self.conversation_history = []
        self.is_loading = False
        self.has_pets = False  # 标记用户是否有宠物
        self.waiting_for_pet_info = False  # 标记是否在等待宠物信息输入
        self.selected_image = None  # 选中的图片文件
        self.image_preview = None  # 图片预览组件
        
        # 创建UI组件
        self.messages_container = ft.ListView(
            expand=True,
            spacing=AppTheme.SPACING_MEDIUM,
            padding=ft.padding.all(AppTheme.SPACING_MEDIUM),
            auto_scroll=True
        )
        
        self.message_input = ft.TextField(
            hint_text="描述您宠物的症状或问题...",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            border_radius=AppTheme.INPUT_RADIUS
        )
        
        self.send_button = ft.IconButton(
            icon=IconConfig.ICON_SEND,
            icon_color=AppTheme.PRIMARY_COLOR,
            on_click=self.on_send_message,
            disabled=False
        )
        
        self.loading_indicator = ft.ProgressRing(
            visible=False,
            color=AppTheme.PRIMARY_COLOR,
            width=20,
            height=20
        )
        
        # 文件选择器 - 使用替代方案
        self.file_picker = None
        
        # 相机按钮
        self.camera_button = ft.IconButton(
            icon=IconConfig.ICON_CAMERA,
            icon_color=AppTheme.PRIMARY_COLOR,
            on_click=self.on_camera_click,
            tooltip="拍照"
        )
        
        # 相册按钮
        self.gallery_button = ft.IconButton(
            icon=ft.icons.Icons.PHOTO_LIBRARY,
            icon_color=AppTheme.PRIMARY_COLOR,
            on_click=self.on_gallery_click,
            tooltip="选择照片"
        )
        
        # 图片预览容器
        self.image_preview_container = ft.Container(
            visible=False,
            margin=ft.margin.only(bottom=AppTheme.SPACING_SMALL),
            content=ft.Column(
                spacing=AppTheme.SPACING_SMALL,
                controls=[]
            )
        )
        
        super().__init__(
            route="/checkup_conversation",
            bgcolor=AppTheme.BACKGROUND,
            padding=0,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        # 顶部应用栏
                        ft.AppBar(
                            title=ft.Text("AI智能体检"),
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            color=ft.Colors.WHITE,
                            leading=ft.IconButton(
                                icon=IconConfig.ICON_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=self.on_back_click
                            ),
                            actions=[
                                ft.IconButton(
                                    icon=IconConfig.ICON_REFRESH,
                                    icon_color=ft.Colors.WHITE,
                                    on_click=self.on_restart_conversation,
                                    tooltip="重新开始对话"
                                )
                            ]
                        ),
                        
                        # 对话消息区域
                        ft.Container(
                            expand=True,
                            content=self.messages_container
                        ),
                        
                        # 输入区域
                        ft.Container(
                            padding=ft.padding.all(AppTheme.SPACING_MEDIUM),
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Column(
                                spacing=AppTheme.SPACING_SMALL,
                                controls=[
                                    # 图片预览区域
                                    self.image_preview_container,
                                    
                                    # 输入行
                                    ft.Row(
                                        spacing=AppTheme.SPACING_SMALL,
                                        controls=[
                                            self.message_input,
                                            self.camera_button,
                                            self.gallery_button,
                                            self.loading_indicator,
                                            self.send_button
                                        ]
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )
        
        # 不添加FilePicker到overlay，使用替代方案
        # self.file_picker.on_result = self.on_file_picked
        # self._page.overlay.append(self.file_picker)
        
        # 启动对话会话
        self.initialize_conversation()
    
    def initialize_conversation(self):
        """初始化对话 - 检查是否有宠物"""
        async def check_pets_and_start():
            try:
                self.set_loading(True)
                
                # 检查用户是否有宠物
                pets_response = api_client.get_pet_list()
                pets = pets_response.get('pets', [])
                
                if pets:
                    # 有宠物，让用户选择要体检的宠物
                    self.has_pets = True
                    if not self.pet_id:
                        # 如果有多个宠物，显示选择界面
                        if len(pets) > 1:
                            self.show_pet_selection(pets)
                            self.set_loading(False)
                            return
                        else:
                            # 只有一个宠物，直接使用
                            self.pet_id = pets[0]['id']
                    
                    # 启动正常的对话会话
                    await self.start_normal_conversation()
                else:
                    # 没有宠物，显示引导消息
                    self.has_pets = False
                    self.waiting_for_pet_info = True
                    self.show_no_pet_guidance()
                
                self.set_loading(False)
                
            except APIError as e:
                self.set_loading(False)
                if e.is_connection_error():
                    error_msg = "无法连接到服务器，请检查网络连接"
                else:
                    error_msg = f"初始化失败: {e.message}"
                
                self.add_message("系统", error_msg, is_error=True)
            except Exception as e:
                self.set_loading(False)
                self.add_message("系统", f"初始化异常: {str(e)}", is_error=True)
        
        # 启动异步任务
        self._page.run_task(check_pets_and_start)
    
    def show_pet_selection(self, pets: list):
        """显示宠物选择界面"""
        selection_card = AppTheme.create_card(
            content=ft.Container(
                padding=ft.padding.all(AppTheme.CARD_PADDING),
                content=ft.Column(
                    spacing=AppTheme.SPACING_MEDIUM,
                    controls=[
                        ft.Text(
                            "选择要体检的宠物",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            "请选择您想要进行AI体检的宠物：",
                            size=14,
                            color=AppTheme.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Column(
                            spacing=AppTheme.SPACING_SMALL,
                            controls=[
                                ft.Container(
                                    content=ft.ListTile(
                                        leading=ft.Icon(
                                            IconConfig.ICON_PET,
                                            color=AppTheme.PRIMARY_COLOR,
                                            size=32
                                        ),
                                        title=ft.Text(
                                            pet['name'],
                                            size=16,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        subtitle=ft.Text(
                                            f"{pet.get('breed', '未知品种')} • {pet.get('age', '未知')}岁",
                                            size=14,
                                            color=AppTheme.TEXT_SECONDARY
                                        ),
                                        trailing=ft.Icon(
                                            IconConfig.ICON_BACK,
                                            color=AppTheme.TEXT_HINT
                                        ),
                                        on_click=lambda e, pet_id=pet['id']: self.on_pet_selected(pet_id)
                                    ),
                                    border=ft.border.all(1, AppTheme.DIVIDER),
                                    border_radius=AppTheme.CARD_RADIUS,
                                    margin=ft.margin.symmetric(vertical=2)
                                )
                                for pet in pets
                            ]
                        ),
                        ft.Divider(color=AppTheme.DIVIDER),
                        ft.TextButton(
                            content=ft.Text("为其他宠物体检"),
                            on_click=self.on_other_pet_click,
                            style=ft.ButtonStyle(
                                color=AppTheme.PRIMARY_COLOR
                            )
                        )
                    ]
                )
            )
        )
        
        # 添加到消息容器
        self.messages_container.controls.append(selection_card)
        self._page.update()
    
    def on_pet_selected(self, pet_id: str):
        """用户选择了宠物"""
        self.pet_id = pet_id
        
        # 清空消息容器
        self.messages_container.controls.clear()
        self._page.update()
        
        # 启动对话会话
        async def start_selected_conversation():
            try:
                self.set_loading(True)
                await self.start_normal_conversation()
                self.set_loading(False)
            except Exception as e:
                self.set_loading(False)
                self.add_message("系统", f"启动对话失败: {str(e)}", is_error=True)
        
        self._page.run_task(start_selected_conversation)
    
    def on_other_pet_click(self, e):
        """用户选择为其他宠物体检"""
        # 清空消息容器
        self.messages_container.controls.clear()
        self._page.update()
        
        # 显示没有宠物的引导消息
        self.has_pets = False
        self.waiting_for_pet_info = True
        self.show_no_pet_guidance()
    
    def show_no_pet_guidance(self):
        """显示没有宠物时的引导消息"""
        guidance_msg = (
            "您好！我是AI宠物医生助手。\n\n"
            "我注意到您还没有登记宠物信息。为了更好地为您服务，"
            "请简单说明您的宠物品种、年龄以及目前的症状。\n\n"
            "例如：\"英短14岁经常拉肚子\" 或 \"金毛2岁最近不爱吃饭\""
        )
        
        self.add_message("AI医生", guidance_msg, is_ai=True)
        
        # 更新输入框提示
        self.message_input.hint_text = "请描述您的宠物品种、年龄和症状..."
        self._page.update()
    
    async def start_normal_conversation(self):
        """启动正常的对话会话（有宠物的情况）"""
        try:
            # 创建对话式体检会话
            response = api_client.create_conversation_session(self.pet_id)
            self.session_id = response.get('sessionId')
            
            # 显示初始消息
            initial_message = response.get('initialMessage', {})
            if initial_message.get('content'):
                self.add_message("AI医生", initial_message['content'], is_ai=True)
            else:
                # 默认欢迎消息
                welcome_msg = "您好！我是AI宠物医生助手。请告诉我您的宠物最近有什么症状或您担心的问题，我会帮您进行初步的健康评估。"
                self.add_message("AI医生", welcome_msg, is_ai=True)
            
        except APIError as e:
            if e.is_connection_error():
                error_msg = "无法连接到AI服务，请检查网络连接"
            else:
                error_msg = f"启动对话失败: {e.message}"
            
            self.add_message("系统", error_msg, is_error=True)
        except Exception as e:
            self.add_message("系统", f"启动对话异常: {str(e)}", is_error=True)
    
    def add_message(self, sender: str, content: str, is_ai: bool = False, is_error: bool = False):
        """添加消息到对话列表"""
        # 确定消息样式
        if is_error:
            bg_color = ft.Colors.RED_50
            text_color = ft.Colors.RED_700
            sender_color = ft.Colors.RED_700
        elif is_ai:
            bg_color = ft.Colors.BLUE_50
            text_color = AppTheme.TEXT_PRIMARY
            sender_color = AppTheme.PRIMARY_COLOR
        else:
            bg_color = AppTheme.CARD_BACKGROUND
            text_color = AppTheme.TEXT_PRIMARY
            sender_color = AppTheme.TEXT_SECONDARY
        
        # 创建消息卡片
        message_card = AppTheme.create_card(
            content=ft.Container(
                padding=ft.padding.all(AppTheme.CARD_PADDING),
                bgcolor=bg_color,
                content=ft.Column(
                    spacing=AppTheme.SPACING_SMALL,
                    controls=[
                        ft.Text(
                            sender,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=sender_color
                        ),
                        ft.Text(
                            content,
                            size=16,
                            color=text_color,
                            selectable=True
                        )
                    ]
                )
            )
        )
        
        # 添加到消息容器
        self.messages_container.controls.append(message_card)
        self._page.update()
        
        # 滚动到底部
        try:
            if hasattr(self.messages_container, 'scroll_to'):
                # 使用update来触发滚动，而不是直接调用scroll_to
                self._page.update()
        except Exception:
            pass  # 忽略滚动错误
    
    def on_send_message(self, e):
        """发送消息"""
        message = self.message_input.value.strip()
        
        # 检查是否有消息
        if not message or self.is_loading:
            return
        
        # 清空输入框
        self.message_input.value = ""
        self._page.update()
        
        # 添加用户消息
        self.add_message("您", message)
        
        # 根据状态处理消息
        if self.waiting_for_pet_info:
            # 处理宠物信息输入
            self.process_pet_info_input(message)
        else:
            # 正常发送到AI
            self.send_to_ai(message)
    
    def process_pet_info_input(self, message: str):
        """处理宠物信息输入"""
        async def handle_pet_info():
            try:
                self.set_loading(True)
                
                # 从用户输入中提取宠物信息
                pet_info = self.extract_pet_info(message)
                
                # 创建一个临时宠物用于对话
                temp_pet = api_client.create_pet(
                    name=pet_info.get('name', '临时宠物'),
                    breed=pet_info.get('breed'),
                    age=pet_info.get('age')
                )
                
                self.pet_id = temp_pet['id']
                
                # 创建对话会话
                response = api_client.create_conversation_session(self.pet_id)
                self.session_id = response.get('sessionId')
                
                # 构造包含症状的首次消息
                symptom_message = pet_info.get('symptoms', message)
                
                # 发送到AI进行分析（不包含图片）
                ai_response = api_client.send_checkup_message(
                    session_id=self.session_id,
                    pet_id=self.pet_id,
                    message=f"症状描述：{symptom_message}",
                    media_file=None
                )
                
                # 显示AI回复
                ai_content = ai_response.get('content', '抱歉，我现在无法回复。')
                self.add_message("AI医生", ai_content, is_ai=True)
                
                # 显示建议问题（如果有）
                suggestions = ai_response.get('suggestions', [])
                if suggestions:
                    self.add_suggestions(suggestions)
                
                # 更新状态
                self.waiting_for_pet_info = False
                self.message_input.hint_text = "继续描述症状或提问..."
                
                # 提示用户这是临时创建的宠物
                self.add_temp_pet_notice(temp_pet['name'])
                
                self.set_loading(False)
                
            except APIError as e:
                self.set_loading(False)
                if e.is_timeout_error():
                    error_msg = "AI分析超时，请稍后重试"
                elif e.is_connection_error():
                    error_msg = "网络连接失败，请检查网络"
                else:
                    error_msg = f"AI分析失败: {e.message}"
                
                self.add_message("系统", error_msg, is_error=True)
            except Exception as e:
                self.set_loading(False)
                self.add_message("系统", f"处理宠物信息异常: {str(e)}", is_error=True)
        
        # 启动异步任务
        self._page.run_task(handle_pet_info)
    
    def extract_pet_info(self, message: str):
        """从用户输入中提取宠物信息"""
        # 简单的信息提取逻辑
        info = {
            'name': '我的宠物',
            'breed': None,
            'age': None,
            'symptoms': message
        }
        
        # 尝试提取品种信息
        breeds = ['英短', '美短', '金毛', '拉布拉多', '泰迪', '比熊', '博美', '柯基', '哈士奇', '萨摩耶']
        for breed in breeds:
            if breed in message:
                info['breed'] = breed
                break
        
        # 尝试提取年龄信息
        import re
        age_match = re.search(r'(\d+)岁', message)
        if age_match:
            info['age'] = int(age_match.group(1))
        
        return info
    
    def add_temp_pet_notice(self, pet_name: str):
        """添加临时宠物创建通知"""
        notice_card = AppTheme.create_card(
            content=ft.Container(
                padding=ft.padding.all(AppTheme.CARD_PADDING),
                bgcolor=ft.Colors.GREEN_50,
                content=ft.Column(
                    spacing=AppTheme.SPACING_SMALL,
                    controls=[
                        ft.Text(
                            "✅ 已为您创建临时宠物档案",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.ACCENT_COLOR
                        ),
                        ft.Text(
                            f"宠物名称：{pet_name}\n"
                            "您可以继续与AI医生对话。如需保存宠物信息，建议完善宠物档案。",
                            size=14,
                            color=AppTheme.TEXT_PRIMARY
                        ),
                        ft.Row(
                            spacing=AppTheme.SPACING_SMALL,
                            controls=[
                                ft.ElevatedButton(
                                    content=ft.Text("完善宠物档案"),
                                    on_click=lambda e: self.app.navigate_to("/pet_detail", pet_id=self.pet_id, edit_mode=True, return_to_ai=True),
                                    bgcolor=AppTheme.ACCENT_COLOR,
                                    color=ft.Colors.WHITE,
                                    scale=0.9
                                ),
                                ft.TextButton(
                                    content=ft.Text("继续对话"),
                                    on_click=lambda e: None,
                                    scale=0.9
                                )
                            ]
                        )
                    ]
                )
            )
        )
        
        # 添加到消息容器
        self.messages_container.controls.append(notice_card)
        self._page.update()
    

    
    def send_to_ai(self, message: str):
        """发送消息到AI"""
        async def process_message():
            try:
                self.set_loading(True)
                
                if not self.session_id:
                    self.add_message("系统", "会话未初始化，请重新开始", is_error=True)
                    self.set_loading(False)
                    return
                
                # 发送消息到AI（不包含图片）
                response = api_client.send_checkup_message(
                    session_id=self.session_id,
                    pet_id=self.pet_id,
                    message=message,
                    media_file=None
                )
                
                # 显示AI回复
                ai_content = response.get('content', '抱歉，我现在无法回复。')
                self.add_message("AI医生", ai_content, is_ai=True)
                
                # 显示建议问题（如果有）
                suggestions = response.get('suggestions', [])
                if suggestions:
                    self.add_suggestions(suggestions)
                
                self.set_loading(False)
                
            except APIError as e:
                self.set_loading(False)
                if e.is_timeout_error():
                    error_msg = "AI分析超时，请稍后重试"
                elif e.is_connection_error():
                    error_msg = "网络连接失败，请检查网络"
                else:
                    error_msg = f"AI分析失败: {e.message}"
                
                self.add_message("系统", error_msg, is_error=True)
            except Exception as e:
                self.set_loading(False)
                self.add_message("系统", f"发送消息异常: {str(e)}", is_error=True)
        
        # 启动异步任务
        self._page.run_task(process_message)
    
    def add_suggestions(self, suggestions: list):
        """添加建议问题"""
        if not suggestions:
            return
        
        suggestion_buttons = []
        for suggestion in suggestions[:3]:  # 最多显示3个建议
            btn = ft.OutlinedButton(
                content=ft.Text(suggestion),
                on_click=lambda e, text=suggestion: self.on_suggestion_click(text),
                style=ft.ButtonStyle(
                    color=AppTheme.PRIMARY_COLOR,
                    side=ft.BorderSide(color=AppTheme.PRIMARY_COLOR, width=1)
                )
            )
            suggestion_buttons.append(btn)
        
        # 创建建议卡片
        suggestion_card = AppTheme.create_card(
            content=ft.Container(
                padding=ft.padding.all(AppTheme.CARD_PADDING),
                bgcolor=ft.Colors.GREEN_50,
                content=ft.Column(
                    spacing=AppTheme.SPACING_SMALL,
                    controls=[
                        ft.Text(
                            "💡 建议问题",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.ACCENT_COLOR
                        ),
                        ft.Row(
                            spacing=AppTheme.SPACING_SMALL,
                            wrap=True,
                            controls=suggestion_buttons
                        )
                    ]
                )
            )
        )
        
        # 添加到消息容器
        self.messages_container.controls.append(suggestion_card)
        self._page.update()
    
    def on_suggestion_click(self, suggestion_text: str):
        """点击建议问题"""
        self.message_input.value = suggestion_text
        self._page.update()
        self.on_send_message(None)
    
    def set_loading(self, loading: bool):
        """设置加载状态"""
        self.is_loading = loading
        self.loading_indicator.visible = loading
        self.send_button.disabled = loading
        self._page.update()
    
    def on_restart_conversation(self, e):
        """重新开始对话"""
        # 清空消息
        self.messages_container.controls.clear()
        self.session_id = None
        self.conversation_history.clear()
        self.waiting_for_pet_info = False
        self._page.update()
        
        # 重新初始化对话
        self.initialize_conversation()
    
    def on_back_click(self, e):
        """点击返回按钮"""
        # 返回到主页面的体检tab
        self.app.navigate_to("/main")
    
    def on_camera_click(self, e):
        """点击相机按钮"""
        # 显示提示信息
        self.add_message("系统", "图片上传功能暂时不可用，请使用文字描述症状", is_error=True)
    
    def on_gallery_click(self, e):
        """点击相册按钮"""
        # 显示提示信息
        self.add_message("系统", "图片上传功能暂时不可用，请使用文字描述症状", is_error=True)
    
    def on_file_picked(self, e):
        """文件选择完成"""
        # 暂时不可用
        pass
    
    def show_image_preview(self, file):
        """显示图片预览"""
        # 暂时不可用
        pass
    
    def remove_image_preview(self, e):
        """删除图片预览"""
        # 暂时不可用
        pass