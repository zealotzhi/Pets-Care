"""
宠物列表页面视图 - 简化版本
"""
import flet as ft
import asyncio
from theme.app_theme import AppTheme, IconConfig
from services.api_client import api_client, APIError


class PetListView(ft.View):
    """宠物列表页面视图"""
    
    def __init__(self, page: ft.Page, app, **kwargs):
        self._page = page
        self.app = app
        self.pets = []
        
        # 创建内容列表
        self.content_column = ft.Column(
            expand=True,
            spacing=AppTheme.SPACING_MEDIUM,
            controls=[
                ft.Text("正在加载宠物列表...", text_align=ft.TextAlign.CENTER)
            ]
        )
        
        super().__init__(
            route="/pet_list",
            bgcolor=AppTheme.BACKGROUND,
            padding=0,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        # 顶部应用栏
                        ft.AppBar(
                            title=ft.Text("我的宠物"),
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            color=ft.Colors.WHITE,
                            actions=[
                                ft.IconButton(
                                    icon=IconConfig.ICON_REFRESH,
                                    icon_color=ft.Colors.WHITE,
                                    on_click=self.on_refresh_click,
                                    tooltip="刷新"
                                ),
                                ft.IconButton(
                                    icon=IconConfig.ICON_ADD,
                                    icon_color=ft.Colors.WHITE,
                                    on_click=self.on_add_pet_click,
                                    tooltip="添加宠物"
                                )
                            ]
                        ),
                        
                        # 内容区域
                        ft.Container(
                            expand=True,
                            padding=ft.padding.all(AppTheme.SPACING_MEDIUM),
                            content=self.content_column
                        )
                    ]
                )
            ]
        )
        
        # 立即加载宠物列表
        print("PetListView初始化完成，开始加载宠物...")
        self.load_pets_sync()
    
    def load_pets_sync(self):
        """同步加载宠物列表"""
        try:
            print("开始同步加载宠物...")
            
            # 显示加载状态
            self.content_column.controls = [
                ft.Container(
                    alignment=ft.alignment.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.ProgressRing(color=AppTheme.PRIMARY_COLOR),
                            ft.Text("正在加载宠物列表...", color=AppTheme.TEXT_SECONDARY)
                        ]
                    )
                )
            ]
            self._page.update()
            
            # 获取宠物列表
            response = api_client.get_pet_list()
            self.pets = response.get('pets', [])
            print(f"同步获取到 {len(self.pets)} 只宠物")
            
            # 更新显示
            self.update_pet_display()
            
        except Exception as e:
            print(f"同步加载失败: {e}")
            self.show_error_sync(f"加载失败: {str(e)}")
    
    def update_pet_display(self):
        """更新宠物显示"""
        print(f"更新宠物显示，数量: {len(self.pets)}")
        
        if not self.pets:
            # 显示空状态
            self.content_column.controls = [
                ft.Container(
                    alignment=ft.alignment.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=AppTheme.SPACING_LARGE,
                        controls=[
                            ft.Icon(
                                IconConfig.ICON_PET,
                                size=80,
                                color=AppTheme.TEXT_HINT
                            ),
                            ft.Text(
                                "还没有宠物",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_SECONDARY
                            ),
                            ft.Text(
                                "点击右上角 + 号添加您的第一只宠物",
                                size=16,
                                color=AppTheme.TEXT_HINT,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.ElevatedButton(
                                content=ft.Text("添加宠物"),
                                on_click=self.on_add_pet_click,
                                bgcolor=AppTheme.PRIMARY_COLOR,
                                color=ft.Colors.WHITE
                            )
                        ]
                    )
                )
            ]
        else:
            # 显示宠物列表
            pet_cards = []
            for i, pet in enumerate(self.pets):
                print(f"创建宠物卡片 {i+1}: {pet.get('name', '未知')}")
                card = self.create_simple_pet_card(pet)
                pet_cards.append(card)
            
            self.content_column.controls = pet_cards
        
        self._page.update()
        print("宠物显示更新完成")
    
    def create_simple_pet_card(self, pet: dict):
        """创建简单的宠物卡片"""
        name = pet.get('name', '未知宠物')
        breed = pet.get('breed', '未知品种')
        age = pet.get('age')
        age_text = f"{age}岁" if age else "年龄未知"
        
        return ft.Card(
            elevation=3,
            content=ft.Container(
                padding=ft.padding.all(16),
                content=ft.Row(
                    controls=[
                        # 宠物头像
                        ft.Container(
                            width=50,
                            height=50,
                            border_radius=25,
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            content=ft.Icon(
                                IconConfig.ICON_PET,
                                size=25,
                                color=ft.Colors.WHITE
                            ),
                            alignment=ft.alignment.Alignment(0, 0)
                        ),
                        
                        # 宠物信息
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        name,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppTheme.TEXT_PRIMARY
                                    ),
                                    ft.Text(
                                        f"{breed} • {age_text}",
                                        size=14,
                                        color=AppTheme.TEXT_SECONDARY
                                    )
                                ]
                            )
                        ),
                        
                        # 操作按钮
                        ft.IconButton(
                            icon=IconConfig.ICON_EDIT,
                            icon_color=AppTheme.PRIMARY_COLOR,
                            on_click=lambda e, pet_id=pet['id']: self.on_pet_detail_click(pet_id),
                            tooltip="查看详情"
                        )
                    ]
                ),
                on_click=lambda e, pet_id=pet['id']: self.on_pet_detail_click(pet_id)
            )
        )
    
    def show_error_sync(self, message: str):
        """同步显示错误"""
        self.content_column.controls = [
            ft.Container(
                alignment=ft.alignment.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.icons.Icons.ERROR, size=64, color=ft.Colors.RED),
                        ft.Text(message, color=ft.Colors.RED, text_align=ft.TextAlign.CENTER),
                        ft.ElevatedButton(
                            content=ft.Text("重试"),
                            on_click=lambda e: self.load_pets_sync(),
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            color=ft.Colors.WHITE
                        )
                    ]
                )
            )
        ]
        self._page.update()
    
    def on_add_pet_click(self, e):
        """点击添加宠物按钮"""
        print("点击添加宠物")
        self.app.navigate_to("/pet_register")
    
    def on_refresh_click(self, e):
        """点击刷新按钮"""
        print("点击刷新")
        self.load_pets_sync()
    
    def on_pet_detail_click(self, pet_id: str):
        """点击宠物详情"""
        print(f"点击宠物详情: {pet_id}")
        self.app.navigate_to("/pet_detail", pet_id=pet_id)