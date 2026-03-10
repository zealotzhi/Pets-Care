"""
宠物详情页面视图
"""
import flet as ft
import asyncio
from theme.app_theme import AppTheme, IconConfig
from services.api_client import api_client, APIError


class PetDetailView(ft.View):
    """宠物详情页面视图"""
    
    def __init__(self, page: ft.Page, app, pet_id=None, edit_mode=False, return_to_ai=False, **kwargs):
        self._page = page
        self.app = app
        self.pet_id = pet_id
        self.pet_data = None
        self.is_loading = False
        self.is_editing = edit_mode  # 支持直接进入编辑模式
        self.return_to_ai = return_to_ai  # 是否需要返回AI对话
        self.initial_edit_mode = edit_mode  # 记录初始编辑模式
        
        # 创建表单字段
        self.name_field = AppTheme.create_text_field(
            label="宠物名字",
            hint_text="给您的宠物起个名字"
        )
        
        self.breed_field = AppTheme.create_text_field(
            label="品种",
            hint_text="例如：英短、金毛、泰迪"
        )
        
        self.age_field = AppTheme.create_text_field(
            label="年龄",
            hint_text="请输入数字（岁）",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.weight_field = AppTheme.create_text_field(
            label="体重",
            hint_text="请输入数字（公斤）",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.gender_dropdown = ft.Dropdown(
            label="性别",
            hint_text="请选择性别",
            options=[
                ft.dropdown.Option("male", "公"),
                ft.dropdown.Option("female", "母")
            ],
            border_radius=AppTheme.INPUT_RADIUS,
            bgcolor=ft.Colors.WHITE
        )
        
        self.health_status_dropdown = ft.Dropdown(
            label="健康状态",
            hint_text="请选择健康状态",
            options=[
                ft.dropdown.Option("healthy", "健康"),
                ft.dropdown.Option("attention", "需要关注"),
                ft.dropdown.Option("serious", "严重"),
                ft.dropdown.Option("end-of-life", "临终关怀")
            ],
            border_radius=AppTheme.INPUT_RADIUS,
            bgcolor=ft.Colors.WHITE
        )
        
        # 创建UI组件
        self.loading_indicator = ft.ProgressRing(
            visible=False,
            color=AppTheme.PRIMARY_COLOR
        )
        
        self.error_text = ft.Text(
            "",
            color=ft.Colors.ERROR,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )
        
        self.edit_button = ft.IconButton(
            icon=IconConfig.ICON_EDIT,
            icon_color=ft.Colors.WHITE,
            on_click=self.on_edit_click,
            tooltip="编辑宠物信息",
            visible=not self.initial_edit_mode  # 如果直接进入编辑模式，隐藏编辑按钮
        )
        
        self.save_button = ft.ElevatedButton(
            content=ft.Text("保存"),
            on_click=self.on_save_click,
            bgcolor=AppTheme.PRIMARY_COLOR,
            color=ft.Colors.WHITE,
            visible=self.initial_edit_mode  # 如果直接进入编辑模式，显示保存按钮
        )
        
        self.cancel_button = ft.TextButton(
            content=ft.Text("取消"),
            on_click=self.on_cancel_click,
            visible=self.initial_edit_mode  # 如果直接进入编辑模式，显示取消按钮
        )
        
        # 创建信息显示区域
        self.info_container = ft.Container(
            expand=True,
            content=ft.ListView(
                expand=True,
                spacing=AppTheme.SPACING_MEDIUM,
                padding=ft.padding.all(AppTheme.SPACING_LARGE),
                controls=[]
            )
        )
        
        super().__init__(
            route="/pet_detail",
            bgcolor=AppTheme.BACKGROUND,
            padding=0,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        # 顶部应用栏
                        ft.AppBar(
                            title=ft.Text("宠物详情"),
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            color=ft.Colors.WHITE,
                            leading=ft.IconButton(
                                icon=IconConfig.ICON_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=self.on_back_click
                            ),
                            actions=[self.edit_button]
                        ),
                        
                        # 内容区域
                        self.info_container,
                        
                        # 底部按钮区域
                        ft.Container(
                            padding=ft.padding.all(AppTheme.SPACING_MEDIUM),
                            content=ft.Row(
                                spacing=AppTheme.SPACING_MEDIUM,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    self.loading_indicator,
                                    self.save_button,
                                    self.cancel_button
                                ]
                            )
                        )
                    ]
                )
            ]
        )
        
        # 加载宠物数据
        if self.pet_id:
            self.load_pet_data()
    
    def load_pet_data(self):
        """加载宠物数据"""
        async def load_data():
            try:
                self.set_loading(True)
                
                # 获取宠物详情
                self.pet_data = api_client.get_pet_detail(self.pet_id)
                
                # 更新显示
                self.update_display()
                
                self.set_loading(False)
                
            except APIError as e:
                self.set_loading(False)
                if e.is_not_found_error():
                    self.show_error("宠物不存在")
                elif e.is_connection_error():
                    self.show_error("无法连接到服务器，请检查网络连接")
                else:
                    self.show_error(f"加载失败: {e.message}")
            except Exception as e:
                self.set_loading(False)
                self.show_error(f"加载异常: {str(e)}")
        
        # 启动异步任务
        self._page.run_task(load_data)
    
    def update_display(self):
        """更新显示内容"""
        if not self.pet_data:
            return
        
        if self.is_editing:
            self.show_edit_form()
        else:
            self.show_pet_info()
    
    def show_pet_info(self):
        """显示宠物信息"""
        controls = []
        
        # 宠物头像区域
        avatar_section = AppTheme.create_card(
            content=ft.Container(
                padding=ft.padding.all(AppTheme.CARD_PADDING),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=AppTheme.SPACING_MEDIUM,
                    controls=[
                        ft.Container(
                            width=120,
                            height=120,
                            border_radius=60,
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            content=ft.Icon(
                                IconConfig.ICON_PET,
                                size=60,
                                color=ft.Colors.WHITE
                            ),
                            alignment=ft.alignment.Alignment(0, 0)
                        ),
                        ft.Text(
                            self.pet_data.get('name', '未知'),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER
                        )
                    ]
                )
            )
        )
        controls.append(avatar_section)
        
        # 基本信息卡片
        basic_info = self.create_info_card(
            "基本信息",
            [
                ("品种", self.pet_data.get('breed') or '未设置'),
                ("年龄", f"{self.pet_data.get('age', '未知')}岁" if self.pet_data.get('age') else '未设置'),
                ("体重", f"{self.pet_data.get('weight', '未知')}公斤" if self.pet_data.get('weight') else '未设置'),
                ("性别", "公" if self.pet_data.get('gender') == 'male' else "母" if self.pet_data.get('gender') == 'female' else '未设置')
            ]
        )
        controls.append(basic_info)
        
        # 健康状态卡片
        health_status_map = {
            'healthy': '健康',
            'attention': '需要关注',
            'serious': '严重',
            'end-of-life': '临终关怀'
        }
        health_status = health_status_map.get(self.pet_data.get('healthStatus'), '未知')
        
        health_info = self.create_info_card(
            "健康状态",
            [
                ("当前状态", health_status),
                ("最后体检", self.format_date(self.pet_data.get('lastCheckupAt')) or '未进行'),
                ("创建时间", self.format_date(self.pet_data.get('createdAt')) or '未知')
            ]
        )
        controls.append(health_info)
        
        # 体检历史卡片
        checkup_history = self.pet_data.get('checkupHistory', [])
        history_info = self.create_info_card(
            "体检历史",
            [
                ("体检次数", f"{len(checkup_history)}次"),
                ("最近体检", self.format_date(self.pet_data.get('lastCheckupAt')) or '暂无记录')
            ]
        )
        controls.append(history_info)
        
        # 更新容器内容
        self.info_container.content.controls = controls
        self._page.update()
    
    def show_edit_form(self):
        """显示编辑表单"""
        # 填充表单数据
        self.name_field.value = self.pet_data.get('name', '')
        self.breed_field.value = self.pet_data.get('breed', '')
        self.age_field.value = str(self.pet_data.get('age', '')) if self.pet_data.get('age') else ''
        self.weight_field.value = str(self.pet_data.get('weight', '')) if self.pet_data.get('weight') else ''
        self.gender_dropdown.value = self.pet_data.get('gender')
        self.health_status_dropdown.value = self.pet_data.get('healthStatus', 'healthy')
        
        # 创建表单控件
        controls = [
            # 基本信息表单
            AppTheme.create_card(
                content=ft.Container(
                    padding=ft.padding.all(AppTheme.CARD_PADDING),
                    content=ft.Column(
                        spacing=AppTheme.SPACING_MEDIUM,
                        controls=[
                            ft.Text(
                                "编辑宠物信息",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_PRIMARY
                            ),
                            self.name_field,
                            self.breed_field,
                            ft.Row(
                                spacing=AppTheme.SPACING_MEDIUM,
                                controls=[
                                    ft.Container(
                                        expand=1,
                                        content=self.age_field
                                    ),
                                    ft.Container(
                                        expand=1,
                                        content=self.weight_field
                                    )
                                ]
                            ),
                            self.gender_dropdown,
                            self.health_status_dropdown
                        ]
                    )
                )
            ),
            
            # 错误提示
            self.error_text
        ]
        
        # 更新容器内容
        self.info_container.content.controls = controls
        self._page.update()
    
    def create_info_card(self, title: str, items: list):
        """创建信息卡片"""
        info_items = []
        for label, value in items:
            info_items.append(
                ft.Row(
                    spacing=AppTheme.SPACING_MEDIUM,
                    controls=[
                        ft.Container(
                            width=80,
                            content=ft.Text(
                                label,
                                size=14,
                                color=AppTheme.TEXT_SECONDARY,
                                weight=ft.FontWeight.BOLD
                            )
                        ),
                        ft.Text(
                            str(value),
                            size=14,
                            color=AppTheme.TEXT_PRIMARY,
                            expand=True
                        )
                    ]
                )
            )
        
        return AppTheme.create_card(
            content=ft.Container(
                padding=ft.padding.all(AppTheme.CARD_PADDING),
                content=ft.Column(
                    spacing=AppTheme.SPACING_SMALL,
                    controls=[
                        ft.Text(
                            title,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY
                        ),
                        ft.Divider(color=AppTheme.DIVIDER),
                        *info_items
                    ]
                )
            )
        )
    
    def format_date(self, date_str: str) -> str:
        """格式化日期"""
        if not date_str:
            return None
        
        try:
            from datetime import datetime
            # 解析ISO格式日期
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y年%m月%d日 %H:%M')
        except:
            return date_str
    
    def on_edit_click(self, e):
        """点击编辑按钮"""
        self.is_editing = True
        self.edit_button.visible = False
        self.save_button.visible = True
        self.cancel_button.visible = True
        self.update_display()
        self._page.update()
    
    def on_save_click(self, e):
        """点击保存按钮"""
        if not self.validate_form():
            return
        
        # 保存数据
        self.save_pet_data()
    
    def on_cancel_click(self, e):
        """点击取消按钮"""
        if self.return_to_ai:
            # 如果是从AI对话进入的，直接返回AI对话
            self.app.navigate_to("/checkup_conversation", pet_id=self.pet_id)
        else:
            # 否则切换到查看模式
            self.is_editing = False
            self.edit_button.visible = True
            self.save_button.visible = False
            self.cancel_button.visible = False
            self.clear_error()
            self.update_display()
            self._page.update()
    
    def validate_form(self) -> bool:
        """验证表单"""
        # 验证必填字段
        if not self.name_field.value or not self.name_field.value.strip():
            self.show_error("宠物名字不能为空")
            return False
        
        # 验证年龄
        if self.age_field.value:
            try:
                age = int(self.age_field.value)
                if age < 0 or age > 30:
                    self.show_error("年龄必须在0-30岁之间")
                    return False
            except ValueError:
                self.show_error("年龄必须是数字")
                return False
        
        # 验证体重
        if self.weight_field.value:
            try:
                weight = float(self.weight_field.value)
                if weight < 0 or weight > 200:
                    self.show_error("体重必须在0-200公斤之间")
                    return False
            except ValueError:
                self.show_error("体重必须是数字")
                return False
        
        return True
    
    def save_pet_data(self):
        """保存宠物数据"""
        async def save_data():
            try:
                self.set_loading(True)
                
                # 准备更新数据
                updates = {
                    'name': self.name_field.value.strip(),
                    'breed': self.breed_field.value.strip() if self.breed_field.value else None,
                    'gender': self.gender_dropdown.value,
                    'healthStatus': self.health_status_dropdown.value
                }
                
                # 处理年龄
                if self.age_field.value:
                    updates['age'] = int(self.age_field.value)
                else:
                    updates['age'] = None
                
                # 处理体重
                if self.weight_field.value:
                    updates['weight'] = float(self.weight_field.value)
                else:
                    updates['weight'] = None
                
                # 调用API更新
                self.pet_data = api_client.update_pet(self.pet_id, updates)
                
                # 切换到查看模式
                self.is_editing = False
                self.edit_button.visible = True
                self.save_button.visible = False
                self.cancel_button.visible = False
                
                # 更新显示
                self.update_display()
                
                # 显示成功消息
                self.show_snack_bar("宠物信息保存成功！", ft.Colors.GREEN)
                
                self.set_loading(False)
                
                # 如果需要返回AI对话，延迟1秒后自动返回
                if self.return_to_ai:
                    await asyncio.sleep(1.5)  # 让用户看到成功消息
                    self.app.navigate_to("/checkup_conversation", pet_id=self.pet_id)
                
            except APIError as e:
                self.set_loading(False)
                if e.is_validation_error():
                    self.show_error(f"输入验证失败: {e.message}")
                elif e.is_connection_error():
                    self.show_error("无法连接到服务器，请检查网络连接")
                else:
                    self.show_error(f"保存失败: {e.message}")
            except Exception as e:
                self.set_loading(False)
                self.show_error(f"保存异常: {str(e)}")
        
        # 启动异步任务
        self._page.run_task(save_data)
    
    def set_loading(self, loading: bool):
        """设置加载状态"""
        self.is_loading = loading
        self.loading_indicator.visible = loading
        self.save_button.disabled = loading
        self._page.update()
    
    def show_error(self, message: str):
        """显示错误信息"""
        self.error_text.value = message
        self.error_text.visible = True
        self._page.update()
    
    def clear_error(self):
        """清除错误信息"""
        self.error_text.value = ""
        self.error_text.visible = False
        self._page.update()
    
    def show_snack_bar(self, message: str, color: str):
        """显示提示消息"""
        self._page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        self._page.snack_bar.open = True
        self._page.update()
    
    def on_back_click(self, e):
        """点击返回按钮"""
        if self.return_to_ai:
            # 如果是从AI对话进入的，返回AI对话页面
            self.app.navigate_to("/checkup_conversation", pet_id=self.pet_id)
        else:
            # 否则返回主页面
            self.app.navigate_to("/main")