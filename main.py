import os
import sys
from datetime import datetime
import requests

# --- НАЛАШТУВАННЯ ВІКНА ТА АДАПТИВНОСТІ ---
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.utils import platform

# Задаємо більш комфортний розмір вікна для ПК
if platform not in ('android', 'ios'):
    Window.size = (400, 800)

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


def resource_path(relative_path):
    """Отримує абсолютний шлях до ресурсів (для .py та збірки APK)"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SERVER_URL = "https://asgard-server-xu8n.onrender.com"

# --- КОЛЬОРОВА ПАЛІТРА (DARK NEON / AZGARD) ---
COLOR_BG = (0.07, 0.08, 0.14, 1)          # Глибокий темно-синій фон
COLOR_CARD_BG = (0.11, 0.13, 0.22, 1)     # Фон картки / контейнерів
COLOR_GOLD = (0.95, 0.76, 0.2, 1)          # Неоновий золотий акцент
COLOR_GOLD_BTN = (0.85, 0.65, 0.12, 1)      # Кнопка Gold
COLOR_TEXT_WHITE = (0.94, 0.96, 1.0, 1)     # Текст білий з легким блакитним відтінком
COLOR_RED = (0.9, 0.22, 0.28, 1)           # Акцентний червоний
COLOR_TAB_BG = (0.15, 0.18, 0.28, 1)      # Фон неактивних вкладок
COLOR_ADMIN_RED = (0.78, 0.15, 0.2, 1)     # Адмінський червоний

def hex_color(hex_str):
    hex_str = hex_str.lstrip('#')
    return [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)] + [1]


class AzgardButton(Button):
    def __init__(self, bg_color=COLOR_GOLD_BTN, text_color=(0.05, 0.07, 0.12, 1), radius=[dp(12)], **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.bold = True
        self.color = text_color
        self.bg_color = bg_color
        self.radius = radius
        
        with self.canvas.before:
            self.paint_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=self.radius)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_state(self, instance, state):
        if state == 'down':
            self.paint_color.rgba = (self.bg_color[0]*0.7, self.bg_color[1]*0.7, self.bg_color[2]*0.7, 1)
        else:
            self.paint_color.rgba = self.bg_color


class CustomTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.14, 0.17, 0.28, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.hint_text_color = (0.5, 0.55, 0.68, 1)
        self.multiline = False
        self.font_size = sp(15)
        self.padding = [dp(10), dp(10), dp(10), dp(10)]


class ColoredScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLOR_BG)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class LoginScreen(ColoredScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        center_box = RelativeLayout(size_hint=(1, 1))
        
        # Збільшено контейнер та елементи форми авторизації
        card = BoxLayout(
            orientation='vertical', padding=dp(20), spacing=dp(14), 
            size_hint=(0.9, None), height=dp(420),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with card.canvas.before:
            Color(*COLOR_CARD_BG)
            self.card_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(18)])
        card.bind(pos=self._update_card, size=self._update_card)

        card.add_widget(Label(
            text="⚡ AZGARD MOBILE ⚡", 
            font_size=sp(22), 
            color=COLOR_GOLD, 
            bold=True,
            size_hint_y=0.2
        ))
        
        self.username_input = TextInput(
            text='', 
            multiline=False, 
            hint_text="Введіть свій нікнейм...",
            size_hint_y=0.2,
            font_size=sp(15),
            background_color=(0.15, 0.18, 0.3, 1),
            foreground_color=COLOR_TEXT_WHITE,
            hint_text_color=(0.5, 0.6, 0.7, 1),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            on_text_validate=self.check_login_flow
        )
        card.add_widget(self.username_input)
        
        self.king_code_input = TextInput(
            text='', 
            multiline=False, 
            password=True,
            hint_text="Код Короля / Адміна...",
            size_hint_y=0.2,
            font_size=sp(15),
            background_color=(0.15, 0.18, 0.3, 1),
            foreground_color=COLOR_TEXT_WHITE,
            hint_text_color=(0.5, 0.6, 0.7, 1),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            on_text_validate=self.check_login_flow
        )
        card.add_widget(self.king_code_input)
        
        btn_login = AzgardButton(
            text="УВІЙТИ В АЗГАРД", 
            size_hint_y=0.22, 
            font_size=sp(15),
            bg_color=COLOR_GOLD_BTN,
            text_color=(0.05, 0.07, 0.12, 1),
            radius=[dp(12)]
        )
        btn_login.bind(on_press=self.check_login_flow)
        card.add_widget(btn_login)
        
        self.error_label = Label(text="", color=COLOR_RED, size_hint_y=0.18, bold=True, font_size=sp(13))
        card.add_widget(self.error_label)
        
        center_box.add_widget(card)
        self.add_widget(center_box)

    def _update_card(self, instance, value):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size

    def check_login_flow(self, instance):
        username = self.username_input.text.strip()
        auth_code = self.king_code_input.text.strip()
        
        if not username:
            self.error_label.text = "Нікнейм не може бути порожнім!"
            return
        
        try:
            res = requests.post(f"{SERVER_URL}/login", json={"username": username, "auth_code": auth_code}, timeout=4)
            data = res.json()
            if data.get("status") == "ok":
                self.king_code_input.text = ""
                self.error_label.text = ""
                app = App.get_running_app()
                app.current_user = {
                    "username": data["username"], 
                    "role": data["role"], 
                    "balance": data["balance"], 
                    "user_id": data["user_id"],
                    "email": data.get("email", "")
                }
                self.manager.current = 'main_game'
            else:
                self.error_label.text = data.get("message", "Помилка входу!")
        except Exception:
            self.error_label.text = "Сервер вимкнено або недоступний!"


class MainGameScreen(ColoredScreen):
    def on_pre_enter(self):
        app = App.get_running_app()
        self.user_data = app.current_user
        self.update_header()
        self.show_tab('chat')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {}
        
        self.main_layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        
        # 1. Верхня Шапка (Збільшено висоту та шрифти)
        self.header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(98), padding=[dp(10), dp(6)], spacing=dp(6))
        with self.header.canvas.before:
            Color(*COLOR_CARD_BG)
            self.header_rect = Rectangle(size=self.header.size, pos=self.header.pos)
        self.header.bind(pos=self._update_header_rect, size=self._update_header_rect)

        self.info_label = Label(text="", halign="center", valign="middle", color=COLOR_GOLD, bold=True, font_size=sp(14), markup=True)
        self.info_label.bind(size=self.info_label.setter('text_size'))
        
        header_btns = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), spacing=dp(8))
        
        self.btn_email = AzgardButton(
            text="✉️ Пошта", 
            size_hint_x=0.33,
            bg_color=(0.14, 0.42, 0.65, 1), 
            text_color=COLOR_TEXT_WHITE,
            radius=[dp(8)], font_size=sp(13)
        )
        self.btn_email.bind(on_press=self.show_email_popup)

        self.btn_panel = AzgardButton(
            text="Пульт", 
            size_hint_x=0.34,
            bg_color=COLOR_GOLD_BTN, 
            text_color=(0.05, 0.07, 0.12, 1),
            radius=[dp(8)], font_size=sp(13)
        )
        self.btn_panel.bind(on_press=self.open_control_panel)
        
        self.btn_logout = AzgardButton(
            text="Вийти", 
            size_hint_x=0.33,
            bg_color=(0.68, 0.15, 0.18, 1), 
            text_color=COLOR_TEXT_WHITE,
            radius=[dp(8)], font_size=sp(13)
        )
        self.btn_logout.bind(on_press=self.show_logout_warning)
        
        header_btns.add_widget(self.btn_email)
        header_btns.add_widget(self.btn_panel)
        header_btns.add_widget(self.btn_logout)
        
        self.header.add_widget(self.info_label)
        self.header.add_widget(header_btns)
        self.main_layout.add_widget(self.header)
        
        # 2. Гортальний список вкладок (Збільшено кнопки меню)
        self.tabs_scroll = ScrollView(
            size_hint_y=None, height=dp(54), 
            do_scroll_y=False, do_scroll_x=True,
            bar_color=[0,0,0,0], bar_inactive_color=[0,0,0,0]
        )
        
        self.tabs_nav = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=dp(8), padding=[dp(8), dp(6)])
        self.tabs_nav.bind(minimum_width=self.tabs_nav.setter('width'))
        
        self.tabs_map = [
            ("💬 Чат", 'chat'), 
            ("✉️ ЛС", 'pm'), 
            ("💸 Перекази", 'transfer'), 
            ("🎰 Казино", 'casino'), 
            ("🛒 Магазин", 'shop'), 
            ("⚖️ Ринок", 'market'), 
            ("📜 Громадяни", 'citizens'), 
            ("📘 Закони", 'rules')
        ]
        self.tab_buttons = {}
        for title, key in self.tabs_map:
            btn = AzgardButton(
                text=title, 
                size_hint_x=None, width=dp(125), 
                bg_color=COLOR_TAB_BG, 
                text_color=COLOR_TEXT_WHITE, 
                radius=[dp(10)], font_size=sp(14)
            )
            btn.bind(on_press=lambda instance, k=key: self.show_tab(k))
            self.tabs_nav.add_widget(btn)
            self.tab_buttons[key] = btn
            
        self.tabs_scroll.add_widget(self.tabs_nav)
        self.main_layout.add_widget(self.tabs_scroll)
        
        # 3. Область Контенту
        self.content_area = BoxLayout(orientation='vertical', size_hint_y=1, padding=dp(8))
        self.main_layout.add_widget(self.content_area)
        self.add_widget(self.main_layout)
        
        Clock.schedule_interval(self.auto_refresh_data, 3)

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def show_logout_warning(self, instance=None):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        email_status = f"[color=00FF66]Пошта: {self.user_data.get('email')}[/color]" if self.user_data.get('email') else "[color=FF3333]ПОШТУ НЕ ПРИВ'ЯЗАНО![/color]"

        warning_text = (
            "[color=FF3333][b]ПОПЕРЕДЖЕННЯ ПРО ВИХІД[/b][/color]\n\n"
            f"{email_status}\n\n"
            "[size=12]Без пошти ви можете втратити акаунт назавжди![/size]"
        )
        
        box.add_widget(Label(text=warning_text, markup=True, halign="center", font_size=sp(14)))
        
        btn_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.4)
        btn_cancel = AzgardButton(text="Скасувати", bg_color=(0.3, 0.3, 0.35, 1), text_color=COLOR_TEXT_WHITE, font_size=sp(13), radius=[dp(8)])
        btn_confirm = AzgardButton(text="Вийти", bg_color=(0.8, 0.1, 0.1, 1), text_color=COLOR_TEXT_WHITE, font_size=sp(13), radius=[dp(8)])
        
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_confirm)
        box.add_widget(btn_box)

        popup = Popup(title="Вихід з гри", content=box, size_hint=(0.9, 0.45))
        btn_cancel.bind(on_press=popup.dismiss)
        
        def confirm_exit(x):
            popup.dismiss()
            self.manager.current = 'login'

        btn_confirm.bind(on_press=confirm_exit)
        popup.open()

    def show_email_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        current_email = self.user_data.get('email', '')
        
        email_display = current_email if current_email else "Не прив'язано"
        
        box.add_widget(Label(
            text=f"=== ПРИВ'ЯЗКА GMAIL ===\n[size=12]{email_display}[/size]", 
            markup=True, halign="center", size_hint_y=0.25, font_size=sp(14)
        ))

        email_input = TextInput(
            hint_text="example@gmail.com",
            text=current_email,
            multiline=False,
            size_hint_y=0.25,
            font_size=sp(14),
            background_color=(0.15, 0.18, 0.3, 1),
            foreground_color=COLOR_TEXT_WHITE,
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        box.add_widget(email_input)

        btn_save = AzgardButton(text="Зберегти", bg_color=COLOR_GOLD_BTN, text_color=(0,0,0,1), size_hint_y=0.25, radius=[dp(8)], font_size=sp(14))
        box.add_widget(btn_save)

        res_lbl = Label(text="", size_hint_y=0.25, markup=True, font_size=sp(12))
        box.add_widget(res_lbl)

        popup = Popup(title="Сповіщення Gmail", content=box, size_hint=(0.9, 0.48))

        def save_email_act(x):
            mail = email_input.text.strip()
            if mail and "@" in mail:
                try:
                    res = requests.post(f"{SERVER_URL}/set_email", json={"username": self.user_data['username'], "email": mail}, timeout=3).json()
                    if res.get("status") == "ok":
                        self.user_data['email'] = mail
                        res_lbl.text = "[color=00FF66]Пошту збережено![/color]"
                        self.update_header()
                    else:
                        res_lbl.text = f"[color=FF3333]{res.get('message')}[/color]"
                except Exception:
                    res_lbl.text = "[color=FF3333]Помилка мережі![/color]"
            else:
                res_lbl.text = "[color=FF3333]Некоректний email![/color]"

        btn_save.bind(on_press=save_email_act)
        popup.open()

    def update_header(self):
        username = self.user_data.get('username', '')
        try:
            res = requests.get(f"{SERVER_URL}/user_info/{username}", timeout=3).json()
            self.user_data['role'] = res.get('role', 'Громадянин')
            self.user_data['balance'] = res.get('balance', 0.0)
            self.user_data['user_id'] = res.get('user_id', '--')
            self.user_data['email'] = res.get('email', '')
            bank_capital = res.get('bank_capital', 0.0)
        except Exception:
            bank_capital = 0.0

        user_id = self.user_data.get('user_id', '--')
        
        self.info_label.text = (
            f"[b]{username}[/b] (ID:{user_id}) | [color=FFD700]{self.user_data['role']}[/color]\n"
            f"Баланс: [color=00FF66]{self.user_data['balance']:.1f} Ю[/color] | Казна: {bank_capital:.1f} Ю"
        )
        
        role = self.user_data['role']
        if role == "Адмін":
            self.btn_panel.opacity = 1
            self.btn_panel.disabled = False
            self.btn_panel.text = "Адмін"
            self.btn_panel.bg_color = COLOR_ADMIN_RED
        elif role == "Король":
            self.btn_panel.opacity = 1
            self.btn_panel.disabled = False
            self.btn_panel.text = "Король"
            self.btn_panel.bg_color = COLOR_GOLD_BTN
        else:
            self.btn_panel.opacity = 0
            self.btn_panel.disabled = True

    def show_tab(self, tab_name):
        self.content_area.clear_widgets()
        self.update_header()
        
        for k, btn in self.tab_buttons.items():
            if k == tab_name:
                btn.bg_color = COLOR_GOLD_BTN
                btn.color = (0.05, 0.07, 0.12, 1)
            else:
                btn.bg_color = COLOR_TAB_BG
                btn.color = COLOR_TEXT_WHITE

        if tab_name == 'chat': 
            self.build_chat_tab()
        elif tab_name == 'pm':
            self.build_pm_tab()
        elif tab_name == 'transfer':
            self.build_transfer_tab()
        elif tab_name == 'casino':
            self.build_casino_tab()
        elif tab_name == 'shop':
            self.build_shop_tab()
        elif tab_name == 'market':
            self.build_market_tab()
        elif tab_name == 'citizens':
            self.build_citizens_tab()
        elif tab_name == 'rules': 
            self.build_rules_tab()

    def build_chat_tab(self):
        rel_container = RelativeLayout()

        try:
            bg_img = Image(
                source=(resource_path('chat_bg.jpg')), 
                opacity=0.22, 
                allow_stretch=True, 
                keep_ratio=False,
                pos_hint={'x': 0, 'y': 0},
                size_hint=(1, 1)
            )
            rel_container.add_widget(bg_img)
        except Exception:
            pass

        chat_layout = BoxLayout(orientation='vertical', pos_hint={'x': 0, 'y': 0}, size_hint=(1, 1))

        self.order_board = Label(
            text="[НАКАЗ КОРОЛЯ]: Немає активних наказів.",
            size_hint_y=None, height=dp(34), color=COLOR_GOLD, bold=True, halign="center", font_size=sp(13), markup=True
        )
        self.order_board.bind(size=self.order_board.setter('text_size'))
        chat_layout.add_widget(self.order_board)
        
        self.chat_scroll = ScrollView(size_hint_y=1)
        self.chat_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(8), padding=dp(6))
        self.chat_grid.bind(minimum_height=self.chat_grid.setter('height'))
        self.chat_scroll.add_widget(self.chat_grid)
        chat_layout.add_widget(self.chat_scroll)
        
        # Поле вводу повідомлення збільшено до висоти 52dp
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(52), spacing=dp(8), padding=[0, dp(6), 0, 0])
        self.msg_input = TextInput(
            hint_text="Повідомлення...", multiline=False, 
            background_color=(0.14, 0.17, 0.28, 0.95), foreground_color=COLOR_TEXT_WHITE,
            font_size=sp(15), padding=[dp(10), dp(10), dp(10), dp(10)], on_text_validate=self.send_message
        )
        btn_send = AzgardButton(text="►", size_hint_x=None, width=dp(56), bg_color=COLOR_GOLD_BTN, text_color=(0,0,0,1), radius=[dp(8)])
        btn_send.bind(on_press=self.send_message)
        input_layout.add_widget(self.msg_input)
        input_layout.add_widget(btn_send)
        chat_layout.add_widget(input_layout)
        
        # Кнопка скарги збільшена
        btn_complaint = AzgardButton(
            text="⚠️ Подати скаргу на порушника", size_hint_y=None, height=dp(38),
            bg_color=(0.55, 0.15, 0.15, 0.85), text_color=COLOR_TEXT_WHITE, font_size=sp(13), radius=[dp(8)]
        )
        btn_complaint.bind(on_press=self.show_complaint_popup)
        chat_layout.add_widget(btn_complaint)
        
        rel_container.add_widget(chat_layout)
        self.content_area.add_widget(rel_container)

        self.load_king_order()
        self.load_chat()

    def send_message(self, instance=None):
        text = self.msg_input.text.strip()
        if not text: return
        try:
            requests.post(f"{SERVER_URL}/send_message", json={"sender": self.user_data['username'], "text": text}, timeout=3)
            self.msg_input.text = ""
            self.load_chat()
            Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)
        except Exception: pass

    def load_chat(self):
        if not hasattr(self, 'chat_grid'): return
        try:
            messages = requests.get(f"{SERVER_URL}/messages", timeout=3).json()
            self.chat_grid.clear_widgets()
            for msg in messages:
                sender, text, timestamp, sender_id, sender_role = msg["sender"], msg["text"], msg["timestamp"], msg["sender_id"], msg["sender_role"]
                role_tag = f"[{sender_role}] " if sender_role in ["Король", "Адмін"] else ""
                disp_id = sender_id if sender_id else "--"
                color_code = "FF3333" if sender_role == "Адмін" else ("FFD700" if sender_role == "Король" else "99CCFF")
                    
                lbl = Label(
                    text=f"[color={color_code}][{timestamp}] {role_tag}{sender} ({disp_id}):[/color] {text}", 
                    size_hint_y=None, font_size=sp(14), halign="left", valign="middle", markup=True
                )
                lbl.bind(texture_size=lbl.setter('size'))
                lbl.bind(width=lambda im, val: setattr(lbl, 'text_size', (val, None)))
                self.chat_grid.add_widget(lbl)
        except Exception: pass

    def load_king_order(self):
        if not hasattr(self, 'order_board'): return
        try:
            res = requests.get(f"{SERVER_URL}/king_order", timeout=3).json()
            if res.get("type"):
                self.order_board.text = f"[color=FFD700][{res['type'].upper()} ДЛЯ {res['target'].upper()}]:[/color] {res['text']}"
            else:
                self.order_board.text = "[ОГОЛОШЕННЯ]: Немає активних указів."
        except Exception: pass

    def build_pm_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8))
        layout.add_widget(Label(text="=== ПРИВАТНІ ПОВІДОМЛЕННЯ ===", font_size=sp(16), color=COLOR_GOLD, bold=True, size_hint_y=None, height=dp(34)))

        self.pm_target_input = TextInput(
            hint_text="Кому (Нік або ID)...", multiline=False, size_hint_y=None, height=dp(46),
            background_color=(0.14, 0.17, 0.28, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        layout.add_widget(self.pm_target_input)

        self.pm_scroll = ScrollView(size_hint_y=1)
        self.pm_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(6), padding=dp(6))
        self.pm_grid.bind(minimum_height=self.pm_grid.setter('height'))
        self.pm_scroll.add_widget(self.pm_grid)
        layout.add_widget(self.pm_scroll)

        pm_input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8))
        self.pm_text_input = TextInput(
            hint_text="Текст...", multiline=False,
            background_color=(0.14, 0.17, 0.28, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)],
            on_text_validate=self.send_pm
        )
        btn_send_pm = AzgardButton(text="►", size_hint_x=None, width=dp(54), bg_color=COLOR_GOLD_BTN, text_color=(0,0,0,1), radius=[dp(8)])
        btn_send_pm.bind(on_press=self.send_pm)
        pm_input_layout.add_widget(self.pm_text_input)
        pm_input_layout.add_widget(btn_send_pm)
        layout.add_widget(pm_input_layout)

        self.content_area.add_widget(layout)
        self.load_pms()

    def send_pm(self, instance=None):
        target = self.pm_target_input.text.strip()
        text = self.pm_text_input.text.strip()
        if not target or not text: return

        try:
            res = requests.post(f"{SERVER_URL}/send_pm", json={"sender": self.user_data['username'], "target": target, "text": text}, timeout=3).json()
            if res.get("status") == "ok":
                self.pm_text_input.text = ""
                self.load_pms()
            else:
                self.show_popup_msg("ЛС Помилка", res.get("message", "Не знайдено!"))
        except Exception: pass

    def load_pms(self):
        if not hasattr(self, 'pm_grid'): return
        try:
            username = self.user_data['username']
            pms = requests.get(f"{SERVER_URL}/pms/{username}", timeout=3).json()
            self.pm_grid.clear_widgets()

            for pm in pms:
                s, r, t, tm = pm["sender"], pm["receiver"], pm["text"], pm["timestamp"]
                color_tag = "00FF66" if s == username else "FF9933"
                direction = f"-> {r}" if s == username else f"<- {s}"
                
                lbl = Label(
                    text=f"[color={color_tag}][{tm}] [{direction}]:[/color] {t}",
                    size_hint_y=None, font_size=sp(13), halign="left", valign="middle", markup=True
                )
                lbl.bind(texture_size=lbl.setter('size'))
                lbl.bind(width=lambda im, val: setattr(lbl, 'text_size', (val, None)))
                self.pm_grid.add_widget(lbl)
        except Exception: pass

    def build_transfer_tab(self):
        rel = RelativeLayout()
        layout = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12),
                           size_hint=(0.94, None), height=dp(320),
                           pos_hint={'center_x': 0.5, 'center_y': 0.5})

        with layout.canvas.before:
            Color(*COLOR_CARD_BG)
            self.tr_rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[dp(16)])
        layout.bind(pos=lambda inst, val: setattr(self.tr_rect, 'pos', val), size=lambda inst, val: setattr(self.tr_rect, 'size', val))

        layout.add_widget(Label(text="=== КІБЕР-БАНКІНГ ===", font_size=sp(18), color=COLOR_GOLD, bold=True, size_hint_y=0.2))

        self.tr_target_input = TextInput(
            hint_text="Отримувач (Нік або ID)...", multiline=False, size_hint_y=0.2,
            background_color=(0.15, 0.18, 0.3, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        layout.add_widget(self.tr_target_input)

        self.tr_amount_input = TextInput(
            hint_text="Сума (Юніти)...", multiline=False, size_hint_y=0.2,
            background_color=(0.15, 0.18, 0.3, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)],
            on_text_validate=self.exec_transfer
        )
        layout.add_widget(self.tr_amount_input)

        btn_transfer = AzgardButton(text="💸 ПЕРЕКАЗАТИ 💸", size_hint_y=0.25, font_size=sp(15), bg_color=COLOR_GOLD_BTN, text_color=(0,0,0,1), radius=[dp(10)])
        btn_transfer.bind(on_press=self.exec_transfer)
        layout.add_widget(btn_transfer)

        self.tr_status_label = Label(text="Миттєвий переказ коштів", font_size=sp(13), color=COLOR_TEXT_WHITE, halign="center", size_hint_y=0.15)
        layout.add_widget(self.tr_status_label)

        rel.add_widget(layout)
        self.content_area.add_widget(rel)

    def exec_transfer(self, instance=None):
        target = self.tr_target_input.text.strip()
        amount_str = self.tr_amount_input.text.strip()

        if not target or not amount_str:
            self.tr_status_label.text = "[color=FF3333]Заповніть усі поля![/color]"
            self.tr_status_label.markup = True
            return

        try:
            amount = float(amount_str)
            res = requests.post(f"{SERVER_URL}/transfer", json={"sender": self.user_data['username'], "target": target, "amount": amount}, timeout=3).json()
            if res.get("status") == "ok":
                self.tr_status_label.text = f"[color=00FF66]{res.get('message')}[/color]"
                self.tr_status_label.markup = True
                self.tr_target_input.text = ""
                self.tr_amount_input.text = ""
                self.update_header()
            else:
                self.tr_status_label.text = f"[color=FF3333]{res.get('message')}[/color]"
                self.tr_status_label.markup = True
        except ValueError:
            self.tr_status_label.text = "[color=FF3333]Введіть число![/color]"
            self.tr_status_label.markup = True
        except Exception:
            self.tr_status_label.text = "[color=FF3333]Сервер недоступний![/color]"
            self.tr_status_label.markup = True

    def build_casino_tab(self):
        rel = RelativeLayout()
        layout = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12),
                           size_hint=(0.94, None), height=dp(350),
                           pos_hint={'center_x': 0.5, 'center_y': 0.5})

        with layout.canvas.before:
            Color(*COLOR_CARD_BG)
            self.cas_rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[dp(16)])
        layout.bind(pos=lambda inst, val: setattr(self.cas_rect, 'pos', val), size=lambda inst, val: setattr(self.cas_rect, 'size', val))

        layout.add_widget(Label(text="=== КАЗИНО: КОЛЕСО ===", font_size=sp(18), color=COLOR_GOLD, bold=True, size_hint_y=0.15))

        info_text = (
            "🌟 [color=00FF66]2x[/color] — Шанс 10%\n"
            "⚡ [color=99CCFF]x0.5[/color] — Шанс 20%\n"
            "💀 [color=FF3333]БАНКРУТ[/color] — Шанс 70%"
        )
        layout.add_widget(Label(text=info_text, markup=True, halign="center", font_size=sp(13), size_hint_y=0.3))

        self.casino_bet_input = TextInput(
            hint_text="Сума ставки...", multiline=False, size_hint_y=0.18,
            background_color=(0.15, 0.18, 0.3, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)],
            on_text_validate=self.spin_casino
        )
        layout.add_widget(self.casino_bet_input)

        btn_spin = AzgardButton(text="🎰 КРУТИТИ 🎰", size_hint_y=0.22, font_size=sp(15), bg_color=COLOR_GOLD_BTN, text_color=(0,0,0,1), radius=[dp(10)])
        btn_spin.bind(on_press=self.spin_casino)
        layout.add_widget(btn_spin)

        self.casino_result_label = Label(text="Випробуйте удачу!", font_size=sp(13), color=COLOR_TEXT_WHITE, halign="center", size_hint_y=0.15)
        layout.add_widget(self.casino_result_label)

        rel.add_widget(layout)
        self.content_area.add_widget(rel)

    def spin_casino(self, instance=None):
        bet_str = self.casino_bet_input.text.strip()
        if not bet_str:
            self.casino_result_label.text = "[color=FF3333]Введіть ставку![/color]"
            self.casino_result_label.markup = True
            return

        try:
            bet = float(bet_str)
            res = requests.post(f"{SERVER_URL}/spin_wheel", json={"username": self.user_data['username'], "bet": bet}, timeout=3).json()

            if res.get("status") == "ok":
                self.casino_result_label.text = res.get("message", "")
                self.update_header()
            else:
                self.casino_result_label.text = f"[color=FF3333]{res.get('message', 'Помилка!')}[/color]"
                self.casino_result_label.markup = True
        except ValueError:
            self.casino_result_label.text = "[color=FF3333]Введіть число![/color]"
            self.casino_result_label.markup = True
        except Exception:
            self.casino_result_label.text = "[color=FF3333]Помилка мережі![/color]"
            self.casino_result_label.markup = True

    def auto_refresh_data(self, dt):
        if self.manager.current == 'main_game':
            self.load_king_order()
            self.update_header()
            if hasattr(self, 'chat_grid') and self.chat_grid.parent:
                self.load_chat()
            if hasattr(self, 'pm_grid') and self.pm_grid.parent:
                self.load_pms()
            if hasattr(self, 'market_grid') and self.market_grid.parent:
                self.load_market_items()

    def show_complaint_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        self.target_input = TextInput(hint_text="Нік або ID порушника", multiline=False, background_color=(0.14, 0.17, 0.28, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)])
        self.reason_input = TextInput(hint_text="Суть порушення...", background_color=(0.14, 0.17, 0.28, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)])
        btn_submit = AzgardButton(text="ВІДПРАВИТИ", bg_color=COLOR_GOLD_BTN, text_color=(0,0,0,1), radius=[dp(8)], font_size=sp(14))
        box.add_widget(self.target_input)
        box.add_widget(self.reason_input)
        box.add_widget(btn_submit)
        
        popup = Popup(title="Подати скаргу", content=box, size_hint=(0.9, 0.5))
        btn_submit.bind(on_press=lambda x: self.submit_complaint(popup))
        popup.open()

    def submit_complaint(self, popup):
        raw_target = self.target_input.text.strip()
        reason = self.reason_input.text.strip()
        if raw_target and reason:
            try:
                requests.post(f"{SERVER_URL}/submit_complaint", json={"reporter": self.user_data['username'], "target": raw_target, "reason": reason}, timeout=3)
            except Exception: pass
        popup.dismiss()

    def build_shop_tab(self):
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(8))
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text="=== МАГАЗИН АЗГАРДУ ===", font_size=sp(17), color=COLOR_GOLD, bold=True, size_hint_y=None, height=dp(32)))
        grid.add_widget(Label(text="--- ВІП СТАТУСИ ---", font_size=sp(14), color=COLOR_GOLD, bold=True, size_hint_y=None, height=dp(26)))
        
        vips = [(1, "Віпка 1", 700, "+10% з/п"), (2, "Віпка 2", 1000, "+20% з/п"), (3, "Віпка 3", 2000, "2х з/п")]
        for level, label, price, desc in vips:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8))
            row.add_widget(Label(text=f"[b]{label}[/b] ({desc})", markup=True, color=COLOR_TEXT_WHITE, font_size=sp(13), size_hint_x=0.55, halign='left'))
            row.add_widget(Label(text=f"{price}Ю", color=COLOR_GOLD, font_size=sp(13), size_hint_x=0.2, bold=True))
            btn = AzgardButton(text="Купити", bg_color=COLOR_GOLD_BTN, size_hint_x=0.25, radius=[dp(8)], font_size=sp(12))
            btn.bind(on_press=lambda instance, lvl=level, pr=price, lbl=label: self.buy_vip(lvl, pr, lbl))
            row.add_widget(btn)
            grid.add_widget(row)
            
        grid.add_widget(Label(text="--- ДОЗВОЛИ ---", font_size=sp(14), color=COLOR_GOLD, bold=True, size_hint_y=None, height=dp(26)))
        permits = [("sell", "Дозвіл на продаж", 500), ("territory", "Дозвіл на територію", 300), ("food", "Дозвіл на їжу", 200), ("weapons", "Дозвіл на зброю", 250), ("tools", "Дозвіл на інструменти", 250)]
        for key, label, price in permits:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8))
            row.add_widget(Label(text=label, color=COLOR_TEXT_WHITE, font_size=sp(13), size_hint_x=0.55, halign='left'))
            row.add_widget(Label(text=f"{price}Ю", color=COLOR_GOLD, font_size=sp(13), size_hint_x=0.2, bold=True))
            btn = AzgardButton(text="Купити", bg_color=COLOR_GOLD_BTN, size_hint_x=0.25, radius=[dp(8)], font_size=sp(12))
            btn.bind(on_press=lambda instance, k=key, pr=price, lbl=label: self.buy_permit(k, pr, lbl))
            row.add_widget(btn)
            grid.add_widget(row)
            
        scroll.add_widget(grid)
        self.content_area.add_widget(scroll)

    def buy_vip(self, level, price, label):
        try:
            res = requests.post(f"{SERVER_URL}/buy_vip", json={"username": self.user_data['username'], "level": level, "price": price}, timeout=3).json()
            if res.get("status") == "ok":
                self.update_header()
                self.show_popup_msg("Успішно", f"Куплено {label}!")
            else:
                self.show_popup_msg("Магазин", res.get("message", "Помилка"))
        except Exception: pass

    def buy_permit(self, key, price, label):
        try:
            res = requests.post(f"{SERVER_URL}/buy_permit", json={"username": self.user_data['username'], "key": key, "price": price}, timeout=3).json()
            if res.get("status") == "ok":
                self.update_header()
                self.show_popup_msg("Успішно", f"Куплено {label}!")
            else:
                self.show_popup_msg("Магазин", res.get("message", "Помилка"))
        except Exception: pass

    def show_popup_msg(self, title, message):
        box = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(12))
        box.add_widget(Label(text=message, color=COLOR_TEXT_WHITE, font_size=sp(14), halign="center"))
        btn = AzgardButton(text="ОК", bg_color=COLOR_GOLD_BTN, size_hint_y=0.4, font_size=sp(14), radius=[dp(8)])
        box.add_widget(btn)
        popup = Popup(title=title, content=box, size_hint=(0.88, 0.35))
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def build_market_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8))
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), spacing=dp(8))
        top_bar.add_widget(Label(text="=== РИНОК ===", font_size=sp(16), color=COLOR_GOLD, bold=True, halign="left"))
        btn_sell = AzgardButton(text="+ Виставити", size_hint_x=None, width=dp(120), bg_color=COLOR_GOLD_BTN, radius=[dp(8)], font_size=sp(12))
        btn_sell.bind(on_press=self.show_sell_popup)
        top_bar.add_widget(btn_sell)
        layout.add_widget(top_bar)
        
        self.market_scroll = ScrollView(size_hint_y=1)
        self.market_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(6))
        self.market_grid.bind(minimum_height=self.market_grid.setter('height'))
        self.market_scroll.add_widget(self.market_grid)
        layout.add_widget(self.market_scroll)
        
        self.content_area.add_widget(layout)
        self.load_market_items()

    def load_market_items(self):
        if not hasattr(self, 'market_grid'): return
        try:
            items = requests.get(f"{SERVER_URL}/market_items", timeout=3).json()
            self.market_grid.clear_widgets()
            current_user = self.user_data['username']
            current_role = self.user_data['role']
            
            for item in items:
                item_id, seller, item_name, price, desc = item["id"], item["seller"], item["item_name"], item["price"], item["description"]
                row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(54), spacing=dp(8))
                desc_str = f" ([color=bbbbbb]{desc}[/color])" if desc else ""
                item_lbl = Label(
                    text=f"[b]{item_name}[/b] - [color=FFD700]{price:.1f}Ю[/color]\n[size=11]Продавець: {seller}{desc_str}[/size]",
                    markup=True, font_size=sp(13), size_hint_x=0.68, halign="left", valign="middle"
                )
                item_lbl.bind(size=item_lbl.setter('text_size'))
                row_layout.add_widget(item_lbl)
                
                if seller == current_user:
                    btn_action = AzgardButton(text="Забрати", bg_color=(0.5, 0.3, 0.1, 1), size_hint_x=0.32, radius=[dp(8)], font_size=sp(12))
                    btn_action.bind(on_press=lambda instance, i_id=item_id: self.cancel_market_item(i_id))
                elif current_role == "Адмін":
                    btn_action = AzgardButton(text="Видалити", bg_color=COLOR_ADMIN_RED, text_color=COLOR_TEXT_WHITE, size_hint_x=0.32, radius=[dp(8)], font_size=sp(12))
                    btn_action.bind(on_press=lambda instance, i_id=item_id: self.cancel_market_item(i_id, is_admin_override=True))
                else:
                    btn_action = AzgardButton(text="Купити", bg_color=(0.14, 0.52, 0.32, 1), text_color=COLOR_TEXT_WHITE, size_hint_x=0.32, radius=[dp(8)], font_size=sp(12))
                    btn_action.bind(on_press=lambda instance, i_id=item_id, pr=price, sel=seller, item=item_name: self.buy_market_item(i_id, pr, sel, item))
                    
                row_layout.add_widget(btn_action)
                self.market_grid.add_widget(row_layout)
        except Exception: pass

    def show_sell_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        self.market_item_input = TextInput(hint_text="Назва предмету...", multiline=False, background_color=(0.14, 0.17, 0.28, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)])
        self.market_price_input = TextInput(hint_text="Ціна (Юніти)...", multiline=False, background_color=(0.14, 0.17, 0.28, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)])
        self.market_desc_input = TextInput(hint_text="Опис (необов'язково)...", background_color=(0.14, 0.17, 0.28, 1), foreground_color=COLOR_TEXT_WHITE, font_size=sp(14), padding=[dp(10), dp(10), dp(10), dp(10)])
        btn_add = AzgardButton(text="ВИСТАВИТИ", bg_color=COLOR_GOLD_BTN, text_color=(0,0,0,1), radius=[dp(8)], font_size=sp(14))
        box.add_widget(self.market_item_input)
        box.add_widget(self.market_price_input)
        box.add_widget(self.market_desc_input)
        box.add_widget(btn_add)
        
        popup = Popup(title="Створення лоту", content=box, size_hint=(0.9, 0.55))
        btn_add.bind(on_press=lambda x: self.submit_market_item(popup))
        popup.open()

    def submit_market_item(self, popup):
        item = self.market_item_input.text.strip()
        price_str = self.market_price_input.text.strip()
        desc = self.market_desc_input.text.strip()
        if item and price_str:
            try:
                price = float(price_str)
                if price > 0:
                    requests.post(f"{SERVER_URL}/submit_market", json={"seller": self.user_data['username'], "item_name": item, "price": price, "description": desc}, timeout=3)
                    self.load_market_items()
            except ValueError: pass
        popup.dismiss()

    def cancel_market_item(self, item_id, is_admin_override=False):
        try:
            requests.post(f"{SERVER_URL}/cancel_market", json={"item_id": item_id, "seller": self.user_data['username'], "is_admin": is_admin_override}, timeout=3)
            self.load_market_items()
        except Exception: pass

    def buy_market_item(self, item_id, price, seller, item_name):
        try:
            res = requests.post(f"{SERVER_URL}/buy_market", json={"buyer": self.user_data['username'], "item_id": item_id, "price": price, "seller": seller, "item_name": item_name}, timeout=3).json()
            if res.get("status") == "ok":
                self.update_header()
                self.load_market_items()
                self.show_popup_msg("Купівля", f"Куплено {item_name}!")
            else:
                self.show_popup_msg("Помилка", res.get("message", "Помилка"))
        except Exception: pass

    def build_citizens_tab(self):
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(8))
        grid.bind(minimum_height=grid.setter('height'))
        grid.add_widget(Label(text="=== ЖИТЕЛІ АЗГАРДУ ===", font_size=sp(17), color=COLOR_GOLD, bold=True, size_hint_y=None, height=dp(32)))
        
        try:
            users = requests.get(f"{SERVER_URL}/citizens", timeout=3).json()
            for u in users:
                username, u_id, role, bal, vip = u["username"], u["user_id"], u["role"], u["balance"], u["vip_level"]
                card_text = f"[color=FFD700][ID:{u_id}] {username}[/color] | {role}\nБаланс: {bal:.1f}Ю | ВІП: {vip}"
                lbl = Label(text=card_text, markup=True, font_size=sp(13), size_hint_y=None, height=dp(46), halign="left", valign="middle")
                lbl.bind(size=lbl.setter('size'))
                grid.add_widget(lbl)
        except Exception: pass
        
        scroll.add_widget(grid)
        self.content_area.add_widget(scroll)

    def build_rules_tab(self):
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(12), padding=dp(10))
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text="=== ЗАКОНИ ТА КОНСТИТУЦІЯ АЗГАРДУ ===", font_size=sp(16), color=COLOR_GOLD, bold=True, size_hint_y=None, height=dp(34)))
        
        rules_text = (
            "[b][color=FFD700]1. ЗАГАЛЬНІ ПРАВИЛА ЧАТУ ТА СПІЛКУВАННЯ:[/color][/b]\n"
            "• [color=FFD700]1.1.[/color] Заборонена нецензурна лексика, мати та приховані образи.\n"
            "• [color=FFD700]1.2.[/color] Не ображати Азгардців, їхніх близьких та національну гідність.\n"
            "• [color=FFD700]1.3.[/color] Будь-які погрози реальним життям або розправою заборонені.\n"
            "• [color=FFD700]1.4.[/color] Повага до Короля, Адміністрації та законів держави обов'язкова.\n"
            "• [color=FFD700]1.5.[/color] Заборонено спам, капс, флуд та публікація контенту 18+.\n\n"

            "[b][color=FFD700]2. ДЕРЖАВНИЙ УСТРІЙ ТА БЕЗПЕКА:[/color][/b]\n"
            "• [color=FFD700]2.1.[/color] Сепаратизм, заклики до повалення влади Короля — негайне вигнання.\n"
            "• [color=FFD700]2.2.[/color] Виконувати всі прямі накази та укази Короля, опубліковані в дошці.\n"
            "• [color=FFD700]2.3.[/color] Використання багів або читів тягне за собою повний бан акаунта.\n\n"

            "[b][color=FFD700]3. ЕКОНОМІКА ТА РИНОК:[/color][/b]\n"
            "• [color=FFD700]3.1.[/color] Шахрайство при переказах чи купівлі лотів суворо карається.\n"
            "• [color=FFD700]3.2.[/color] Заборонено виставляти фейкові товари або спамити однаковими лотами.\n"
            "• [color=FFD700]3.3.[/color] Торгівля дозволами чи привілеями без згоди Адміністрації заборонена."
        )
        
        lbl_content = Label(text=rules_text, markup=True, size_hint_y=None, font_size=sp(13), halign='left', valign='top', color=COLOR_TEXT_WHITE)
        lbl_content.bind(texture_size=lbl_content.setter('size'))
        lbl_content.bind(width=lambda im, val: setattr(lbl_content, 'text_size', (val, None)))
        
        grid.add_widget(lbl_content)
        scroll.add_widget(grid)
        self.content_area.add_widget(scroll)

    # --- ПУЛЬТ КЕРУВАННЯ КОРОЛЯ / АДМІНА ---
    def open_control_panel(self, instance):
        role = self.user_data['role']
        
        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        scroll = ScrollView(size_hint_y=1)
        main_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=dp(10))
        main_layout.bind(minimum_height=main_layout.setter('height'))

        with main_layout.canvas.before:
            Color(*hex_color('#161a29'))
            self.panel_rect = RoundedRectangle(size=main_layout.size, pos=main_layout.pos, radius=[dp(14)])
            main_layout.bind(size=self._update_panel_rect, pos=self._update_panel_rect)

        # --- ЗАГОЛОВОК ---
        title = Label(
            text="ПАНЕЛЬ АБСОЛЮТНОГО КОРОЛЯ" if role == "Король" else "ПАНЕЛЬ АДМІНІСТРАТОРА", 
            color=hex_color('#ff4d4d'), bold=True, font_size=sp(15), size_hint_y=None, height=dp(28)
        )
        divider = Label(
            text="--------------------------------------------------", 
            color=hex_color('#ff4d4d'), size_hint_y=None, height=dp(14)
        )
        complaints_title = Label(
            text="Державні скарги громадян:", 
            color=hex_color('#ff4d4d'), bold=True, font_size=sp(13), size_hint_y=None, height=dp(24)
        )
        
        main_layout.add_widget(title)
        main_layout.add_widget(divider)
        main_layout.add_widget(complaints_title)

        # Список скарг
        self.complaints_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(90))
        self.complaints_scroll = ScrollView()
        self.complaints_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(6))
        self.complaints_grid.bind(minimum_height=self.complaints_grid.setter('height'))
        self.complaints_scroll.add_widget(self.complaints_grid)
        self.complaints_box.add_widget(self.complaints_scroll)
        main_layout.add_widget(self.complaints_box)

        # --- 1. ДИСЦИПЛІНАРНИЙ КОМІТЕТ (БАН/РОЗБАН) ---
        main_layout.add_widget(Label(text="Дисциплінарний Комітет (Бан/Розбан):", color=hex_color('#ffd700'), bold=True, font_size=sp(12), size_hint_y=None, height=dp(22)))
        box1 = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(44))
        self.input_ban_nick = CustomTextInput(hint_text="Нік/ID...", size_hint_x=0.4)
        btn_ban = AzgardButton(text="Забанити", bg_color=hex_color('#b31b1b'), text_color=(1,1,1,1), size_hint_x=0.3, font_size=sp(12), radius=[dp(8)])
        btn_ban.bind(on_press=lambda x: self.send_admin_act({"action": "ban_user", "target": self.input_ban_nick.text, "role": role}))
        
        btn_unban = AzgardButton(text="Розбанити", bg_color=hex_color('#1b8a22'), text_color=(1,1,1,1), size_hint_x=0.3, font_size=sp(12), radius=[dp(8)])
        btn_unban.bind(on_press=lambda x: self.send_admin_act({"action": "unban_user", "target": self.input_ban_nick.text, "role": role}))
        
        box1.add_widget(self.input_ban_nick)
        box1.add_widget(btn_ban)
        box1.add_widget(btn_unban)
        main_layout.add_widget(box1)

        # --- 2. ДЕРЖАВНА КАЗНАЧЕЯ (ЮНІТИ) ---
        main_layout.add_widget(Label(text="Державна Казначея (Юніти):", color=hex_color('#ffd700'), bold=True, font_size=sp(12), size_hint_y=None, height=dp(22)))
        box2 = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(44))
        self.input_treasury_nick = CustomTextInput(hint_text="Нік/ID...", size_hint_x=0.25)
        self.input_treasury_amount = CustomTextInput(hint_text="Сума...", size_hint_x=0.25)
        
        btn_add_units = AzgardButton(text="+Дати", bg_color=hex_color('#1b8a22'), text_color=(1,1,1,1), size_hint_x=0.16, font_size=sp(11), radius=[dp(8)])
        btn_add_units.bind(on_press=lambda x: self.send_admin_act({"action": "give_units", "target": self.input_treasury_nick.text, "amount": self.input_treasury_amount.text, "role": role}))
        
        btn_remove_units = AzgardButton(text="-Забрати", bg_color=hex_color('#8b4513'), text_color=(1,1,1,1), size_hint_x=0.17, font_size=sp(11), radius=[dp(8)])
        btn_remove_units.bind(on_press=lambda x: self.send_admin_act({"action": "take_units", "target": self.input_treasury_nick.text, "amount": self.input_treasury_amount.text, "role": role}))
        
        btn_set_units = AzgardButton(text="=Задати", bg_color=hex_color('#2b6cb0'), text_color=(1,1,1,1), size_hint_x=0.17, font_size=sp(11), radius=[dp(8)])
        btn_set_units.bind(on_press=lambda x: self.send_admin_act({"action": "set_units", "target": self.input_treasury_nick.text, "amount": self.input_treasury_amount.text, "role": role}))
        
        box2.add_widget(self.input_treasury_nick)
        box2.add_widget(self.input_treasury_amount)
        box2.add_widget(btn_add_units)
        box2.add_widget(btn_remove_units)
        box2.add_widget(btn_set_units)
        main_layout.add_widget(box2)

        # --- 3. НАДАННЯ ВІП-РАНГІВ (0-4) ---
        main_layout.add_widget(Label(text="Надання ВІП-Рангів (0-4):", color=hex_color('#ffd700'), bold=True, font_size=sp(12), size_hint_y=None, height=dp(22)))
        box3 = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(44))
        self.input_vip_nick = CustomTextInput(hint_text="Нік/ID...", size_hint_x=0.4)
        self.input_vip_level = CustomTextInput(hint_text="Рівень (0-4)...", size_hint_x=0.3)
        btn_set_vip = AzgardButton(text="Встановити", bg_color=hex_color('#1d82b6'), text_color=(1,1,1,1), size_hint_x=0.3, font_size=sp(11), radius=[dp(8)])
        btn_set_vip.bind(on_press=lambda x: self.send_admin_act({"action": "give_vip", "target": self.input_vip_nick.text, "level": self.input_vip_level.text, "role": role}))
        
        box3.add_widget(self.input_vip_nick)
        box3.add_widget(self.input_vip_level)
        box3.add_widget(btn_set_vip)
        main_layout.add_widget(box3)

        # --- 4. КЕРУВАННЯ ДОЗВОЛАМИ ---
        main_layout.add_widget(Label(text="Керування Дозволами:", color=hex_color('#ffd700'), bold=True, font_size=sp(12), size_hint_y=None, height=dp(22)))
        box4 = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(44))
        self.input_perm_nick = CustomTextInput(hint_text="Нік/ID...", size_hint_x=0.3)
        self.input_perm_type = CustomTextInput(hint_text="Тип...", size_hint_x=0.3)
        
        btn_grant_perm = AzgardButton(text="Дати", bg_color=hex_color('#1b8a22'), text_color=(1,1,1,1), size_hint_x=0.2, font_size=sp(11), radius=[dp(8)])
        btn_grant_perm.bind(on_press=lambda x: self.send_admin_act({"action": "grant_perm", "target": self.input_perm_nick.text, "perm": self.input_perm_type.text, "role": role}))
        
        btn_revoke_perm = AzgardButton(text="Забрати", bg_color=hex_color('#b31b1b'), text_color=(1,1,1,1), size_hint_x=0.2, font_size=sp(11), radius=[dp(8)])
        btn_revoke_perm.bind(on_press=lambda x: self.send_admin_act({"action": "revoke_perm", "target": self.input_perm_nick.text, "perm": self.input_perm_type.text, "role": role}))
        
        box4.add_widget(self.input_perm_nick)
        box4.add_widget(self.input_perm_type)
        box4.add_widget(btn_grant_perm)
        box4.add_widget(btn_revoke_perm)
        main_layout.add_widget(box4)

        # --- 5. КАПІТАЛ БАНКУ ---
        main_layout.add_widget(Label(text="Капітал Банку:", color=hex_color('#ffd700'), bold=True, font_size=sp(12), size_hint_y=None, height=dp(22)))
        box5 = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(44))
        self.input_bank_capital = CustomTextInput(hint_text="Сума...", size_hint_x=0.5)
        btn_set_capital = AzgardButton(text="Встановити", bg_color=hex_color('#b8860b'), text_color=(1,1,1,1), size_hint_x=0.5, font_size=sp(11), radius=[dp(8)])
        btn_set_capital.bind(on_press=lambda x: self.send_admin_act({"action": "set_bank_capital", "amount": self.input_bank_capital.text, "role": role}))
        
        box5.add_widget(self.input_bank_capital)
        box5.add_widget(btn_set_capital)
        main_layout.add_widget(box5)

        # --- 6. ОГОЛОШЕННЯ НАКАЗІВ / ЗАВДАНЬ ---
        main_layout.add_widget(Label(text="Оголошення Наказів / Завдань:", color=hex_color('#ffd700'), bold=True, font_size=sp(12), size_hint_y=None, height=dp(22)))
        box6 = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(44))
        self.input_order_target = CustomTextInput(hint_text="Кому...", size_hint_x=0.3)
        self.input_order_text = CustomTextInput(hint_text="Текст...", size_hint_x=0.3)
        
        btn_send_order = AzgardButton(text="Наказ", bg_color=hex_color('#b8860b'), text_color=(1,1,1,1), size_hint_x=0.2, font_size=sp(11), radius=[dp(8)])
        btn_send_order.bind(on_press=lambda x: self.send_admin_act({"action": "royal_order", "order_type": "Наказ", "target": self.input_order_target.text, "text": self.input_order_text.text, "role": role}))
        
        btn_send_task = AzgardButton(text="Завдання", bg_color=hex_color('#2b6cb0'), text_color=(1,1,1,1), size_hint_x=0.2, font_size=sp(11), radius=[dp(8)])
        btn_send_task.bind(on_press=lambda x: self.send_admin_act({"action": "royal_order", "order_type": "Завдання", "target": self.input_order_target.text, "text": self.input_order_text.text, "role": role}))
        
        box6.add_widget(self.input_order_target)
        box6.add_widget(self.input_order_text)
        box6.add_widget(btn_send_order)
        box6.add_widget(btn_send_task)
        main_layout.add_widget(box6)

        # --- 7. ЗБОРИ ТА ДЕРЖАВНИЙ ПОРЯДОК ---
        main_layout.add_widget(Label(text="Збори та Державний Порядок:", color=hex_color('#ffd700'), bold=True, font_size=sp(12), size_hint_y=None, height=dp(22)))
        btn_tax = AzgardButton(
            text="Зібрати податок (По 50 юнітів)", 
            bg_color=hex_color('#7a6211'), text_color=(1,1,1,1),
            size_hint_y=None, height=dp(44), font_size=sp(12), radius=[dp(8)]
        )
        btn_tax.bind(on_press=lambda x: self.send_admin_act({"action": "collect_tax", "amount": 50, "role": role}))
        main_layout.add_widget(btn_tax)

        scroll.add_widget(main_layout)
        popup_layout.add_widget(scroll)

        # --- 8. КНОПКА ЗАКРИТТЯ ---
        btn_close = AzgardButton(
            text="Закрити пульт керування", 
            bg_color=hex_color('#282b3d'), text_color=(1,1,1,1),
            size_hint_y=None, height=dp(46), font_size=sp(13), radius=[dp(8)]
        )
        popup_layout.add_widget(btn_close)

        king_popup = Popup(title="Пульт Керування Державою", content=popup_layout, size_hint=(0.95, 0.94))
        btn_close.bind(on_press=king_popup.dismiss)
        
        self.load_complaints()
        king_popup.open()

    def _update_panel_rect(self, instance, value):
        if hasattr(self, 'panel_rect'):
            self.panel_rect.pos = instance.pos
            self.panel_rect.size = instance.size

    def send_admin_act(self, payload):
        try:
            res = requests.post(f"{SERVER_URL}/admin_action", json=payload, timeout=3).json()
            if res.get("status") == "ok":
                self.show_popup_msg("Успіх", res.get("message", "Дію виконано!"))
            else:
                self.show_popup_msg("Помилка", res.get("message", "Не вдалося виконати!"))
            self.update_header()
            self.load_complaints()
            self.load_king_order()
        except Exception: 
            self.show_popup_msg("Помилка", "З'єднання із сервером втрачено!")

    def load_complaints(self):
        if not hasattr(self, 'complaints_grid'): return
        try:
            items = requests.get(f"{SERVER_URL}/complaints", timeout=3).json()
            self.complaints_grid.clear_widgets()
            for c in items:
                lbl = Label(
                    text=f"Скарга #{c['id']}: від {c['reporter']} на {c['target']}\n-> {c['reason']}", 
                    size_hint_y=None, font_size=sp(12), halign="left", color=COLOR_TEXT_WHITE
                )
                lbl.bind(texture_size=lbl.setter('size'))
                lbl.bind(width=lambda im, val: setattr(lbl, 'text_size', (val, None)))
                self.complaints_grid.add_widget(lbl)
        except Exception: pass


class AzgardApp(App):
    def build(self):
        self.current_user = {}
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(MainGameScreen(name='main_game'))
        return self.sm

if __name__ == '__main__':
    AzgardApp().run()
