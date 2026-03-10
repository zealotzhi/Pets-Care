"""
体检报告页面视图
"""
import flet as ft
from theme.app_theme import AppTheme, IconConfig


class CheckupReportView(ft.View):
    """体检报告页面视图"""
    
    def __init__(self, page: ft.Page, app, session_id=None, **kwargs):
        self._page = page
        self.app = app
        self.session_id = session_id
        
        super().__init__(
            route="/checkup_report",
            bgcolor=AppTheme.BACKGROUND,
            padding=0,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        # 顶部应用栏
                        ft.AppBar(
                            title=ft.Text("体检报告"),
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            color=ft.Colors.WHITE,
                            leading=ft.IconButton(
                                icon=IconConfig.ICON_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=self.on_back_click
                            )
                        ),
                        
                        # 报告内容
                        ft.Container(
                            expand=True,
                            padding=ft.padding.all(AppTheme.SPACING_LARGE),
                            content=ft.Column(
                                expand=True,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        "体检报告页面",
                                        size=20,
                                        color=AppTheme.TEXT_PRIMARY,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Text(
                                        "这里将显示AI生成的体检报告",
                                        color=AppTheme.TEXT_SECONDARY,
                                        text_align=ft.TextAlign.CENTER,
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )
    
    def on_back_click(self, e):
        """点击返回按钮"""
        # 返回到AI对话页面
        self.app.navigate_to("/checkup_conversation")