"""
宠物临终关怀App - Flet版本主入口
"""
import flet as ft
from views.splash_view import SplashView
from views.main_view import MainView
from views.pet_register_view import PetRegisterView
from views.pet_list_view import PetListView
from views.pet_detail_view import PetDetailView
from views.checkup_conversation_view import CheckupConversationView
from views.checkup_report_view import CheckupReportView
from theme.app_theme import AppTheme


class PetCareApp:
    """主应用类"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.setup_theme()
        self.setup_routes()
        
        # 显示启动页面
        self.navigate_to("/splash")
    
    def setup_page(self):
        """配置页面基本属性"""
        self.page.title = "宠物关怀 Pet Care"
        self.page.window_width = 400
        self.page.window_height = 800
        self.page.window_resizable = False
        self.page.padding = 0
        self.page.spacing = 0
    
    def setup_theme(self):
        """配置应用主题"""
        # 使用UI设计指南的色彩系统
        self.page.theme = ft.Theme(
            color_scheme_seed=AppTheme.PRIMARY_COLOR,
            use_material3=True
        )
        
        # 设置主题模式
        self.page.theme_mode = ft.ThemeMode.LIGHT
    
    def setup_routes(self):
        """设置路由"""
        self.routes = {
            "/splash": SplashView,
            "/main": MainView,
            "/pet_register": PetRegisterView,
            "/pet_list": PetListView,
            "/pet_detail": PetDetailView,
            "/checkup_conversation": CheckupConversationView,
            "/checkup_report": CheckupReportView,
        }
    
    def navigate_to(self, route: str, **kwargs):
        """导航到指定页面"""
        if route in self.routes:
            # 清除当前视图
            self.page.views.clear()
            
            # 创建新视图
            view_class = self.routes[route]
            view = view_class(self.page, self, **kwargs)
            
            # 添加到页面
            self.page.views.append(view)
            self.page.update()
        else:
            print(f"警告: 路由 '{route}' 不存在")
    
    def go_back(self):
        """返回上一页"""
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.update()


def main(page: ft.Page):
    """应用入口函数"""
    app = PetCareApp(page)


if __name__ == "__main__":
    ft.run(main)