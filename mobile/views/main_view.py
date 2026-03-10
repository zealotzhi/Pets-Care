"""
主页面视图 - 包含底部导航
"""
import flet as ft
from theme.app_theme import AppTheme, IconConfig
from .pet_list_view import PetListView


class MainView(ft.View):
    """主页面视图"""
    
    def __init__(self, page: ft.Page, app, **kwargs):
        self._page = page
        self.app = app
        self.current_tab = 0
        
        # 创建底部导航栏
        self.navigation_bar = ft.NavigationBar(
            selected_index=0,
            on_change=self.on_tab_change,
            destinations=[
                ft.NavigationBarDestination(
                    icon=IconConfig.ICON_PET,
                    label="宠物"
                ),
                ft.NavigationBarDestination(
                    icon=IconConfig.ICON_CHECKUP,
                    label="体检"
                ),
                ft.NavigationBarDestination(
                    icon=IconConfig.ICON_CARE,
                    label="关怀"
                ),
            ]
        )
        
        # 创建内容区域
        self.content_area = ft.Container(
            expand=True,
            content=self.create_pet_tab_content()
        )
        
        super().__init__(
            route="/main",
            bgcolor=AppTheme.BACKGROUND,
            padding=0,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        self.content_area,
                        self.navigation_bar
                    ]
                )
            ]
        )
    
    def on_tab_change(self, e):
        """处理Tab切换"""
        self.current_tab = e.control.selected_index
        
        if self.current_tab == 0:
            # 宠物Tab
            self.content_area.content = self.create_pet_tab_content()
        elif self.current_tab == 1:
            # 体检Tab
            self.content_area.content = self.create_checkup_tab_content()
        elif self.current_tab == 2:
            # 关怀Tab
            self.content_area.content = self.create_care_tab_content()
        
        self._page.update()
    
    def create_pet_tab_content(self):
        """创建宠物Tab内容"""
        return ft.Column(
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
                            icon=IconConfig.ICON_ADD,
                            icon_color=ft.Colors.WHITE,
                            on_click=self.on_add_pet_click
                        )
                    ]
                ),
                
                # 宠物列表内容
                ft.Container(
                    expand=True,
                    padding=ft.padding.all(AppTheme.SPACING_LARGE),
                    content=self.create_pet_list_content()
                )
            ]
        )
    
    def create_pet_list_content(self):
        """创建宠物列表内容"""
        try:
            from services.api_client import api_client, APIError
            
            print("MainView: 开始加载宠物列表...")
            
            # 尝试获取宠物列表
            try:
                response = api_client.get_pet_list()
                pets = response.get('pets', [])
                print(f"MainView: 获取到 {len(pets)} 只宠物")
                
                if not pets:
                    print("MainView: 没有宠物，显示空状态")
                    return ft.Container(
                        expand=True,
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
                
                # 创建宠物卡片列表
                print("MainView: 创建宠物卡片...")
                pet_cards = []
                for i, pet in enumerate(pets):
                    print(f"MainView: 创建宠物卡片 {i+1}: {pet.get('name', '未知')}")
                    pet_card = self.create_simple_pet_card(pet)
                    pet_cards.append(pet_card)
                
                return ft.ListView(
                    expand=True,
                    spacing=AppTheme.SPACING_MEDIUM,
                    controls=pet_cards
                )
                
            except APIError as e:
                print(f"MainView: API错误 - {e}")
                if e.is_connection_error():
                    return ft.Container(
                        expand=True,
                        alignment=ft.alignment.Alignment(0, 0),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    IconConfig.ICON_ERROR,
                                    size=64,
                                    color=AppTheme.TEXT_HINT
                                ),
                                ft.Text(
                                    "无法连接到服务器",
                                    size=18,
                                    color=AppTheme.TEXT_PRIMARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "请检查网络连接或稍后重试",
                                    color=AppTheme.TEXT_SECONDARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Text("重试"),
                                    on_click=lambda e: self.refresh_pet_list(),
                                    bgcolor=AppTheme.PRIMARY_COLOR,
                                    color=ft.Colors.WHITE
                                )
                            ]
                        )
                    )
                else:
                    return ft.Container(
                        expand=True,
                        alignment=ft.alignment.Alignment(0, 0),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    IconConfig.ICON_ERROR,
                                    size=64,
                                    color=AppTheme.TEXT_HINT
                                ),
                                ft.Text(
                                    f"加载失败: {e.message}",
                                    color=AppTheme.TEXT_SECONDARY,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Text("重试"),
                                    on_click=lambda e: self.refresh_pet_list(),
                                    bgcolor=AppTheme.PRIMARY_COLOR,
                                    color=ft.Colors.WHITE
                                )
                            ]
                        )
                    )
                    
        except Exception as e:
            print(f"MainView: 未知错误 - {e}")
            return ft.Container(
                expand=True,
                alignment=ft.alignment.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=AppTheme.SPACING_LARGE,
                    controls=[
                        ft.Icon(
                            IconConfig.ICON_ERROR,
                            size=64,
                            color=AppTheme.TEXT_HINT
                        ),
                        ft.Text(
                            f"加载异常: {str(e)}",
                            color=AppTheme.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text("重试"),
                            on_click=lambda e: self.refresh_pet_list(),
                            bgcolor=AppTheme.PRIMARY_COLOR,
                            color=ft.Colors.WHITE
                        )
                    ]
                )
            )
    
    def create_pet_card(self, pet: dict):
        """创建宠物卡片"""
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
    
    def create_simple_pet_card(self, pet: dict):
        """创建简单的宠物卡片 - 包含编辑和删除功能"""
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
                        
                        # 操作按钮组
                        ft.Row(
                            spacing=AppTheme.SPACING_SMALL,
                            controls=[
                                # 编辑按钮
                                ft.IconButton(
                                    icon=IconConfig.ICON_EDIT,
                                    icon_color=AppTheme.PRIMARY_COLOR,
                                    on_click=lambda e, pet_id=pet['id']: self.on_pet_detail_click(pet_id),
                                    tooltip="编辑宠物"
                                ),
                                # 删除按钮
                                ft.IconButton(
                                    icon=IconConfig.ICON_DELETE,
                                    icon_color=AppTheme.WARNING_COLOR,
                                    on_click=lambda e, pet_id=pet['id'], pet_name=name: self.on_pet_delete_click(pet_id, pet_name),
                                    tooltip="删除宠物"
                                )
                            ]
                        )
                    ]
                ),
                on_click=lambda e, pet_id=pet['id']: self.on_pet_detail_click(pet_id)
            )
        )
    
    def refresh_pet_list(self):
        """刷新宠物列表"""
        # 重新创建宠物Tab内容
        if self.current_tab == 0:
            self.content_area.content = self.create_pet_tab_content()
            self._page.update()
    
    def on_pet_detail_click(self, pet_id: str):
        """点击宠物详情"""
        self.app.navigate_to("/pet_detail", pet_id=pet_id)
    
    def on_pet_delete_click(self, pet_id: str, pet_name: str):
        """点击删除宠物"""
        print(f"MainView: 请求删除宠物 {pet_name} (ID: {pet_id})")
        
        # 创建确认删除对话框
        def confirm_delete(e):
            """确认删除"""
            try:
                from services.api_client import api_client, APIError
                
                print(f"MainView: 开始删除宠物 {pet_name}")
                
                # 调用API删除宠物
                api_client.delete_pet(pet_id)
                
                print(f"MainView: 宠物 {pet_name} 删除成功")
                
                # 显示成功消息
                self._page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"宠物 {pet_name} 已删除"),
                    bgcolor=AppTheme.ACCENT_COLOR
                )
                self._page.snack_bar.open = True
                
                # 关闭对话框
                dialog.open = False
                
                # 刷新宠物列表 - 强制刷新并切换到宠物tab
                print("MainView: 删除成功，开始刷新宠物列表...")
                
                # 确保切换到宠物tab
                self.current_tab = 0
                self.navigation_bar.selected_index = 0
                
                # 重新创建宠物tab内容
                self.content_area.content = self.create_pet_tab_content()
                self._page.update()
                
                print("MainView: 宠物列表刷新完成")
                
            except APIError as e:
                print(f"MainView: 删除宠物失败 - {e}")
                
                # 显示错误消息
                self._page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"删除失败: {e.message}"),
                    bgcolor=AppTheme.WARNING_COLOR
                )
                self._page.snack_bar.open = True
                
                # 关闭对话框
                dialog.open = False
                self._page.update()
                
            except Exception as e:
                print(f"MainView: 删除宠物异常 - {e}")
                
                # 显示错误消息
                self._page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"删除异常: {str(e)}"),
                    bgcolor=AppTheme.WARNING_COLOR
                )
                self._page.snack_bar.open = True
                
                # 关闭对话框
                dialog.open = False
                self._page.update()
        
        def cancel_delete(e):
            """取消删除"""
            dialog.open = False
            self._page.update()
        
        # 创建确认对话框
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("确认删除"),
            content=ft.Text(f"确定要删除宠物 \"{pet_name}\" 吗？\n\n此操作不可撤销，将同时删除该宠物的所有体检记录。"),
            actions=[
                ft.TextButton(
                    content=ft.Text("取消"),
                    on_click=cancel_delete
                ),
                ft.TextButton(
                    content=ft.Text("删除"),
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(
                        color=AppTheme.WARNING_COLOR
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # 显示对话框
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()
    
    def create_checkup_tab_content(self):
        """创建体检Tab内容"""
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                # 顶部应用栏
                ft.AppBar(
                    title=ft.Text("智能体检"),
                    bgcolor=AppTheme.PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                ),
                
                # 体检内容
                ft.Container(
                    expand=True,
                    padding=ft.padding.all(AppTheme.SPACING_LARGE),
                    content=ft.Column(
                        expand=True,
                        spacing=AppTheme.SPACING_LARGE,
                        controls=[
                            # 欢迎信息
                            ft.Container(
                                padding=ft.padding.all(AppTheme.SPACING_LARGE),
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=AppTheme.SPACING_MEDIUM,
                                    controls=[
                                        ft.Icon(
                                            IconConfig.ICON_CHECKUP,
                                            size=64,
                                            color=AppTheme.PRIMARY_COLOR
                                        ),
                                        ft.Text(
                                            "AI智能体检",
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                            color=AppTheme.TEXT_PRIMARY,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Text(
                                            "通过AI对话了解宠物健康状况\n获得专业的医疗建议",
                                            size=16,
                                            color=AppTheme.TEXT_SECONDARY,
                                            text_align=ft.TextAlign.CENTER,
                                        )
                                    ]
                                )
                            ),
                            
                            # 体检选项卡片
                            AppTheme.create_card(
                                content=ft.Container(
                                    padding=ft.padding.all(AppTheme.CARD_PADDING),
                                    content=ft.Column(
                                        spacing=AppTheme.SPACING_MEDIUM,
                                        controls=[
                                            # 对话式体检
                                            ft.ListTile(
                                                leading=ft.Icon(
                                                    IconConfig.ICON_CHECKUP,
                                                    color=AppTheme.PRIMARY_COLOR,
                                                    size=32
                                                ),
                                                title=ft.Text(
                                                    "AI对话体检",
                                                    size=18,
                                                    weight=ft.FontWeight.BOLD
                                                ),
                                                subtitle=ft.Text(
                                                    "与AI医生对话，描述症状获得专业建议",
                                                    color=AppTheme.TEXT_SECONDARY
                                                ),
                                                trailing=ft.Icon(
                                                    IconConfig.ICON_BACK,
                                                    color=AppTheme.TEXT_HINT
                                                ),
                                                on_click=self.on_ai_checkup_click
                                            ),
                                            
                                            ft.Divider(color=AppTheme.DIVIDER),
                                            
                                            # 定期体检
                                            ft.ListTile(
                                                leading=ft.Icon(
                                                    IconConfig.ICON_HEALTHY,
                                                    color=AppTheme.ACCENT_COLOR,
                                                    size=32
                                                ),
                                                title=ft.Text(
                                                    "定期体检记录",
                                                    size=18,
                                                    weight=ft.FontWeight.BOLD
                                                ),
                                                subtitle=ft.Text(
                                                    "记录日常观察，生成健康报告",
                                                    color=AppTheme.TEXT_SECONDARY
                                                ),
                                                trailing=ft.Icon(
                                                    IconConfig.ICON_BACK,
                                                    color=AppTheme.TEXT_HINT
                                                ),
                                                on_click=self.on_scheduled_checkup_click
                                            )
                                        ]
                                    )
                                )
                            ),
                            
                            # 提示信息
                            ft.Container(
                                padding=ft.padding.all(AppTheme.SPACING_MEDIUM),
                                bgcolor=ft.Colors.AMBER_50,
                                border_radius=AppTheme.CARD_RADIUS,
                                content=ft.Row(
                                    spacing=AppTheme.SPACING_SMALL,
                                    controls=[
                                        ft.Icon(
                                            IconConfig.ICON_INFO,
                                            color=ft.Colors.AMBER_700,
                                            size=20
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=ft.Text(
                                                "AI诊断仅供参考，如有严重症状请及时就医",
                                                size=14,
                                                color=ft.Colors.AMBER_700
                                            )
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                )
            ]
        )
    
    def on_ai_checkup_click(self, e):
        """点击AI对话体检"""
        self.app.navigate_to("/checkup_conversation")
    
    def on_scheduled_checkup_click(self, e):
        """点击定期体检记录"""
        # TODO: 实现定期体检功能
        self._page.snack_bar = ft.SnackBar(
            content=ft.Text("定期体检功能开发中..."),
            bgcolor=AppTheme.INFO_COLOR
        )
        self._page.snack_bar.open = True
        self._page.update()
    
    def create_care_tab_content(self):
        """创建关怀Tab内容"""
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                # 顶部应用栏
                ft.AppBar(
                    title=ft.Text("关怀服务"),
                    bgcolor=AppTheme.PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                ),
                
                # 关怀内容
                ft.Container(
                    expand=True,
                    padding=ft.padding.all(AppTheme.SPACING_LARGE),
                    content=ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                IconConfig.ICON_CARE,
                                size=64,
                                color=AppTheme.TEXT_HINT
                            ),
                            ft.Text(
                                "关怀服务",
                                size=20,
                                color=AppTheme.TEXT_PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "这里将显示关怀服务功能\\n包括AI建议、医院查找、殡葬服务",
                                color=AppTheme.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            )
                        ]
                    )
                )
            ]
        )
    
    def on_add_pet_click(self, e):
        """点击添加宠物按钮"""
        self.app.navigate_to("/pet_register")