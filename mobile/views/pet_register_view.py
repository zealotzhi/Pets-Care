"""
宠物登记页面视图
"""
import flet as ft
from theme.app_theme import AppTheme, IconConfig


class PetRegisterView(ft.View):
    """宠物登记页面视图"""
    
    def __init__(self, page: ft.Page, app, **kwargs):
        self._page = page
        self.app = app
        self.error_message = ""
        self.is_loading = False
        
        # 创建UI组件
        self.name_field = AppTheme.create_text_field(
            label="宠物名字",
            hint_text="给您的宠物起个名字",
            on_change=self.on_name_change
        )
        self.error_text = ft.Text(
            "",
            color=ft.Colors.ERROR,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )
        self.submit_button = AppTheme.create_primary_button(
            text="完成登记",
            on_click=self.on_submit_click,
            expand=True
        )
        self.loading_indicator = ft.ProgressRing(
            visible=False,
            color=AppTheme.PRIMARY_COLOR
        )
        
        super().__init__(
            route="/pet_register",
            bgcolor=AppTheme.BACKGROUND,
            padding=0,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        # 顶部应用栏
                        ft.AppBar(
                            title=ft.Text("宠物登记"),
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            color=ft.Colors.WHITE,
                            leading=ft.IconButton(
                                icon=IconConfig.ICON_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=self.on_back_click
                            )
                        ),
                        
                        # 滚动内容区域
                        ft.Container(
                            expand=True,
                            content=ft.ListView(
                                expand=True,
                                spacing=AppTheme.SPACING_LARGE,
                                padding=ft.padding.all(AppTheme.SPACING_LARGE),
                                controls=[
                                    # 说明文字
                                    ft.Text(
                                        "只需要一个名字就可以开始",
                                        size=16,
                                        color=AppTheme.TEXT_SECONDARY,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    
                                    # 名字输入卡片
                                    AppTheme.create_card(
                                        content=ft.Container(
                                            padding=ft.padding.all(AppTheme.CARD_PADDING),
                                            content=ft.Column(
                                                spacing=AppTheme.SPACING_MEDIUM,
                                                controls=[
                                                    ft.Text(
                                                        "宠物名字",
                                                        size=18,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=AppTheme.TEXT_PRIMARY,
                                                    ),
                                                    self.name_field
                                                ]
                                            )
                                        )
                                    ),
                                    
                                    # 错误提示
                                    self.error_text,
                                    
                                    # 提交按钮
                                    ft.Container(
                                        padding=ft.padding.symmetric(horizontal=20),
                                        content=self.submit_button
                                    ),
                                    
                                    # 加载指示器
                                    ft.Container(
                                        alignment=ft.alignment.Alignment(0, 0),
                                        content=self.loading_indicator
                                    ),
                                    
                                    # 底部间距
                                    ft.Container(height=20)
                                ]
                            )
                        )
                    ]
                )
            ]
        )
    

    
    def on_name_change(self, e):
        """名字输入变化"""
        self.clear_error()
    
    def on_submit_click(self, e):
        """点击提交按钮"""
        if not self.validate_input():
            return
        
        # 显示加载状态
        self.set_loading(True)
        
        # 获取输入数据
        name = self.name_field.value.strip()
        
        # 模拟API调用
        import asyncio
        from services.api_client import api_client, APIError
        
        async def register_pet():
            try:
                # 模拟网络请求延迟
                await asyncio.sleep(1)
                
                # 调用实际的API（不需要照片）
                try:
                    result = api_client.create_pet(name)
                    
                    self.set_loading(False)
                    self.show_snack_bar("宠物登记成功！", ft.Colors.GREEN)
                    
                    # 延迟后返回主页面
                    await asyncio.sleep(1.5)
                    self.app.navigate_to("/main")
                    
                except APIError as api_error:
                    self.set_loading(False)
                    if api_error.is_validation_error():
                        self.show_error(f"输入验证失败: {api_error.message}")
                    elif api_error.is_connection_error():
                        self.show_error("无法连接到服务器，请检查网络连接")
                    elif api_error.is_timeout_error():
                        self.show_error("请求超时，请稍后重试")
                    else:
                        self.show_error(f"登记失败: {api_error.message}")
                
            except Exception as ex:
                self.set_loading(False)
                self.show_error(f"登记失败: {str(ex)}")
        
        # 启动异步任务
        self._page.run_task(register_pet)
    
    def validate_input(self) -> bool:
        """验证输入"""
        # 只验证名字
        name = self.name_field.value.strip() if self.name_field.value else ""
        if not name:
            self.show_error("请输入宠物名字")
            return False
        
        return True
    
    def show_error(self, message: str):
        """显示错误信息"""
        self.error_message = message
        self.error_text.value = message
        self.error_text.visible = True
        self._page.update()
    
    def clear_error(self):
        """清除错误信息"""
        self.error_message = ""
        self.error_text.value = ""
        self.error_text.visible = False
        self._page.update()
    
    def set_loading(self, loading: bool):
        """设置加载状态"""
        self.is_loading = loading
        self.loading_indicator.visible = loading
        self.submit_button.disabled = loading
        self.submit_button.text = "提交中..." if loading else "完成登记"
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
        self.app.navigate_to("/main")