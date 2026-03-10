"""
宠物临终关怀App - Flet主题配置
基于UI_DESIGN_GUIDE.md的色彩系统和设计规范
"""
import flet as ft


class AppTheme:
    """应用主题配置类"""
    
    # ========== 主色调 ==========
    PRIMARY_COLOR = "#FF6B6B"  # 温暖的珊瑚红
    ACCENT_COLOR = "#4CAF50"   # 生机绿
    WARNING_COLOR = "#F44336"  # 警告红
    INFO_COLOR = "#2196F3"     # 信任蓝
    
    # ========== 健康状态色彩 ==========
    HEALTH_HEALTHY = "#4CAF50"    # 健康 - 绿色
    HEALTH_ATTENTION = "#FF9800"  # 关注 - 橙色
    HEALTH_SERIOUS = "#F44336"    # 严重 - 红色
    HEALTH_END_OF_LIFE = "#9C27B0" # 临终 - 紫色
    
    # ========== 中性色 ==========
    TEXT_PRIMARY = "#333333"    # 文字主色
    TEXT_SECONDARY = "#666666"  # 文字次色
    TEXT_HINT = "#999999"       # 提示文字
    BACKGROUND = "#F8F9FA"      # 背景色
    CARD_BACKGROUND = "#FFFFFF" # 卡片背景
    DIVIDER = "#E0E0E0"         # 分割线
    
    # ========== 组件样式 ==========
    # 按钮
    BUTTON_RADIUS = 8
    BUTTON_HEIGHT = 48
    
    # 卡片
    CARD_RADIUS = 12
    CARD_PADDING = 16
    CARD_ELEVATION = 3
    
    # 输入框
    INPUT_RADIUS = 8
    INPUT_HEIGHT = 56
    
    # 间距
    SPACING_SMALL = 8
    SPACING_MEDIUM = 12
    SPACING_LARGE = 16
    SPACING_XLARGE = 20
    
    # 触摸目标最小尺寸（无障碍标准）
    MIN_TOUCH_TARGET = 44
    
    @staticmethod
    def get_health_color(status: str) -> str:
        """根据健康状态获取对应颜色
        
        Args:
            status: 健康状态 ('healthy', 'attention', 'serious', 'end-of-life')
            
        Returns:
            对应的颜色值
        """
        status_colors = {
            'healthy': AppTheme.HEALTH_HEALTHY,
            'attention': AppTheme.HEALTH_ATTENTION,
            'serious': AppTheme.HEALTH_SERIOUS,
            'end-of-life': AppTheme.HEALTH_END_OF_LIFE,
        }
        return status_colors.get(status, AppTheme.TEXT_HINT)
    
    @staticmethod
    def get_health_text(status: str) -> str:
        """根据健康状态获取对应文本
        
        Args:
            status: 健康状态
            
        Returns:
            对应的中文文本
        """
        status_texts = {
            'healthy': '健康',
            'attention': '关注',
            'serious': '严重',
            'end-of-life': '临终',
        }
        return status_texts.get(status, '未知')
    
    @staticmethod
    def create_primary_button(text: str, on_click=None, **kwargs) -> ft.ElevatedButton:
        """创建主要按钮"""
        return ft.ElevatedButton(
            content=ft.Text(text),
            bgcolor=AppTheme.PRIMARY_COLOR,
            color=ft.Colors.WHITE,
            height=AppTheme.BUTTON_HEIGHT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=AppTheme.BUTTON_RADIUS)
            ),
            on_click=on_click,
            **kwargs
        )
    
    @staticmethod
    def create_secondary_button(text: str, on_click=None, **kwargs) -> ft.OutlinedButton:
        """创建次要按钮"""
        return ft.OutlinedButton(
            content=ft.Text(text),
            height=AppTheme.BUTTON_HEIGHT,
            style=ft.ButtonStyle(
                color=AppTheme.PRIMARY_COLOR,
                side=ft.BorderSide(color=AppTheme.PRIMARY_COLOR, width=1),
                shape=ft.RoundedRectangleBorder(radius=AppTheme.BUTTON_RADIUS)
            ),
            on_click=on_click,
            **kwargs
        )
    
    @staticmethod
    def create_card(**kwargs) -> ft.Card:
        """创建卡片"""
        return ft.Card(
            elevation=AppTheme.CARD_ELEVATION,
            **kwargs
        )
    
    @staticmethod
    def create_text_field(label: str, **kwargs) -> ft.TextField:
        """创建文本输入框"""
        return ft.TextField(
            label=label,
            height=AppTheme.INPUT_HEIGHT,
            border_radius=AppTheme.INPUT_RADIUS,
            **kwargs
        )


class IconConfig:
    """图标配置"""
    
    # 主要图标
    ICON_PET = ft.icons.Icons.PETS
    ICON_CHECKUP = ft.icons.Icons.HEALTH_AND_SAFETY
    ICON_CARE = ft.icons.Icons.FAVORITE
    ICON_HOSPITAL = ft.icons.Icons.LOCAL_HOSPITAL
    ICON_EMERGENCY = ft.icons.Icons.EMERGENCY
    ICON_CAMERA = ft.icons.Icons.CAMERA_ALT
    ICON_PHONE = ft.icons.Icons.PHONE
    ICON_ADD = ft.icons.Icons.ADD
    ICON_EDIT = ft.icons.Icons.EDIT
    ICON_DELETE = ft.icons.Icons.DELETE
    ICON_BACK = ft.icons.Icons.ARROW_BACK
    ICON_MENU = ft.icons.Icons.MENU
    ICON_REFRESH = ft.icons.Icons.REFRESH
    
    # 状态图标
    ICON_HEALTHY = ft.icons.Icons.CHECK_CIRCLE
    ICON_WARNING = ft.icons.Icons.WARNING
    ICON_ERROR = ft.icons.Icons.ERROR
    ICON_INFO = ft.icons.Icons.INFO
    
    # 体检相关
    ICON_FEEDING = ft.icons.Icons.RESTAURANT
    ICON_DRINKING = ft.icons.Icons.LOCAL_DRINK
    ICON_EXCRETION = ft.icons.Icons.WC
    ICON_ACTIVITY = ft.icons.Icons.DIRECTIONS_RUN
    ICON_BEHAVIOR = ft.icons.Icons.PSYCHOLOGY
    ICON_BODY = ft.icons.Icons.MEDICAL_SERVICES
    ICON_MEDICAL = ft.icons.Icons.MEDICAL_SERVICES
    
    # 其他
    ICON_SEND = ft.icons.Icons.SEND
    ICON_ATTACH = ft.icons.Icons.ATTACH_FILE
    ICON_CLOSE = ft.icons.Icons.CLOSE
    ICON_CHECK = ft.icons.Icons.CHECK