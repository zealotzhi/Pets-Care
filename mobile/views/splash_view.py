"""
启动页面视图
"""
import flet as ft
import asyncio
from theme.app_theme import AppTheme


class SplashView(ft.View):
    """启动页面视图"""
    
    def __init__(self, page: ft.Page, app, **kwargs):
        self._page = page
        self.app = app
        
        super().__init__(
            route="/splash",
            bgcolor=AppTheme.BACKGROUND,
            padding=ft.padding.all(40),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=AppTheme.SPACING_LARGE,
                    controls=[
                        # Logo区域
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=AppTheme.SPACING_MEDIUM,
                            controls=[
                                # Logo图标（使用emoji）
                                ft.Text(
                                    "🐾❤️",
                                    size=80,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                
                                # 应用名称
                                ft.Text(
                                    "宠物关怀",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    color=AppTheme.TEXT_PRIMARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                
                                # 英文名称
                                ft.Text(
                                    "Pet Care",
                                    size=18,
                                    color=AppTheme.TEXT_SECONDARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ]
                        ),
                        
                        # 间距
                        ft.Container(height=40),
                        
                        # 标语
                        ft.Text(
                            "陪伴每一个珍贵的时刻",
                            size=16,
                            color=AppTheme.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        
                        # 间距
                        ft.Container(height=20),
                        
                        # 版本信息
                        ft.Text(
                            "v1.0.0",
                            size=12,
                            color=AppTheme.TEXT_HINT,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        
                        # 底部标语
                        ft.Text(
                            "用爱守护，用心关怀",
                            size=14,
                            color=AppTheme.TEXT_HINT,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ]
                )
            ]
        )
        
        # 启动自动跳转定时器
        self.start_auto_navigation()
    
    def start_auto_navigation(self):
        """启动自动导航定时器"""
        async def auto_navigate():
            await asyncio.sleep(3)  # 等待3秒
            self.app.navigate_to("/main")
        
        # 在页面加载后启动定时器
        self._page.run_task(auto_navigate)