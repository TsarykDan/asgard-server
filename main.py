import os
import sys
import requests

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
    """Отримує абсолютний шлях до ресурсів (працює і в коді, і в зібраному .exe)"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


SERVER_URL = "https://asgard-server-xu8n.onrender.com"

COLOR_BG = (0.05, 0.07, 0.12, 1)
COLOR_GOLD = (1, 0.84, 0, 1)
COLOR_GOLD_BTN = (0.73, 0.56, 0.12, 1)
COLOR_TEXT_WHITE = (0.95, 0.95, 0.95, 1)
COLOR_RED = (0.9, 0.25, 0.25, 1)
COLOR_TAB_BG = (0.12, 0.18, 0.28, 1)
COLOR_ADMIN_RED = (0.7, 0.1, 0.1, 1)


class AsgardButton(Button):
    def __init__(self, bg_color=COLOR_GOLD_BTN, text_color=(0.05, 0.07, 0.12, 1), radius=[10], **kwargs):
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
            self.paint_color.rgba = (self.bg_color[0] * 0.7, self.bg_color[1] * 0.7, self.bg_color[2] * 0.7, 1)
        else:
            self.paint_color.rgba = self.bg_color


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
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        
        layout.add_widget(Label(
            text="*** КОРОЛІВСТВО ASGARD ***", 
            font_size="22sp", 
            color=COLOR_GOLD, 
            bold=True,
            size_hint_y=0.22
        ))
        
        self.username_input = TextInput(
            text='', 
            multiline=False, 
            hint_text="Введіть свій нікнейм...",
            size_hint_y=0.12,
            background_color=(0.1, 0.15, 0.22, 1),
            foreground_color=COLOR_TEXT_WHITE,
            hint_text_color=(0.5, 0.6, 0.7, 1)
        )
        layout.add_widget(self.username_input)
        
        self.king_code_input = TextInput(
            text='', 
            multiline=False, 
            password=True,
            hint_text="Код Короля або Адміна (інакше порожньо)...",
            size_hint_y=0.12,
            background_color=(0.1, 0.15, 0.22, 1),
            foreground_color=COLOR_TEXT_WHITE,
            hint_text_color=(0.5, 0.6, 0.7, 1)
        )
        layout.add_widget(self.king_code_input)
        
        btn_login = AsgardButton(
            text="УВІЙТИ В КОРОЛІВСТВО", 
            size_hint_y=0.15, 
            bg_color=COLOR_GOLD_BTN,
            text_color=(0.05, 0.07, 0.12, 1)
        )
        btn_login.bind(on_press=self.check_login_flow)
        layout.add_widget(btn_login)
        
        self.error_label = Label(text="", color=COLOR_RED, size_hint_y=0.1, bold=True)
        layout.add_widget(self.error_label)
        
        self.add_widget(layout)

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
        
        self.main_layout = BoxLayout(orientation='vertical')
        
        # --- ВЕРХНЯ ПАНЕЛЬ (HEADER) ---
        self.header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=5, spacing=8)
        
        self.info_label = Label(
            text="", 
            halign="left", 
            valign="middle", 
            color=COLOR_GOLD, 
            bold=True, 
            font_size="11sp"
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        
        # Кнопка "Пульт" (для Адміна/Короля)
        self.btn_panel = AsgardButton(
            text="Пульт", 
            size_hint=(None, 1),
            width=70,
            font_size="12sp",
            bg_color=COLOR_GOLD_BTN, 
            text_color=(0.05, 0.07, 0.12, 1),
            radius=[6]
        )
        self.btn_panel.bind(on_press=self.open_control_panel)
        
        # 👑 ЗБІЛЬШЕНА КНОПКА МЕНЮ
        self.btn_menu = AsgardButton(
            text="МЕНЮ", 
            size_hint=(None, 1),
            width=90,
            font_size="13sp",
            bg_color=COLOR_GOLD_BTN, 
            text_color=(0.05, 0.07, 0.12, 1),
            radius=[6]
        )
        self.btn_menu.bind(on_press=self.open_menu_popup)
        
        self.header.add_widget(self.info_label)
        self.header.add_widget(self.btn_panel)
        self.header.add_widget(self.btn_menu)
        
        self.main_layout.add_widget(self.header)
        
        # --- ОСНОВНА ЗОНА КОНТЕНТУ ---
        self.content_area = BoxLayout(orientation='vertical', size_hint_y=1, padding=5)
        self.main_layout.add_widget(self.content_area)
        self.add_widget(self.main_layout)
        
        Clock.schedule_interval(self.auto_refresh_data, 3)

    # --- 📱 ГОЛОВНЕ ВІКНО МЕНЮ ---
    def open_menu_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        box.add_widget(Label(
            text="=== МЕНЮ АЗГАРДУ ===", 
            font_size="18sp", 
            color=COLOR_GOLD, 
            bold=True, 
            size_hint_y=None, 
            height=35
        ))
        
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        grid.bind(minimum_height=grid.setter('height'))
        
        tabs = [
            ("Загальний Чат", 'chat'), 
            ("Приватні Повідомлення (ЛС)", 'pm'), 
            ("Перекази Коштів", 'transfer'), 
            ("Казино (Колесо Фортуни)", 'casino'), 
            ("Державний Магазин", 'shop'), 
            ("Торговий Ринок", 'market'), 
            ("Реєстр Громадян", 'citizens'), 
            ("Кодекс Законів", 'rules')
        ]
        
        popup = Popup(title="Навігація по королівству", content=box, size_hint=(0.9, 0.85))
        
        for title, key in tabs:
            btn = AsgardButton(
                text=title, 
                size_hint_y=None, 
                height=55,  # Збільшена висота кнопок
                font_size="14sp",
                bg_color=COLOR_TAB_BG, 
                text_color=COLOR_TEXT_WHITE, 
                radius=[8]
            )
            def make_select(k):
                return lambda x: (self.show_tab(k), popup.dismiss())
            btn.bind(on_press=make_select(key))
            grid.add_widget(btn)
            
        btn_email = AsgardButton(
            text="Прив'язати Gmail", 
            size_hint_y=None, 
            height=55, 
            font_size="14sp",
            bg_color=(0.1, 0.4, 0.6, 1), 
            text_color=COLOR_TEXT_WHITE, 
            radius=[8]
        )
        btn_email.bind(on_press=lambda x: (popup.dismiss(), self.show_email_popup(x)))
        grid.add_widget(btn_email)
        
        btn_logout = AsgardButton(
            text="Вийти з акаунту", 
            size_hint_y=None, 
            height=55, 
            font_size="14sp",
            bg_color=(0.6, 0.1, 0.1, 1), 
            text_color=COLOR_TEXT_WHITE, 
            radius=[8]
        )
        btn_logout.bind(on_press=lambda x: (popup.dismiss(), self.show_logout_warning(x)))
        grid.add_widget(btn_logout)
        
        scroll.add_widget(grid)
        box.add_widget(scroll)
        
        btn_close = AsgardButton(
            text="Закрити", 
            size_hint_y=None, 
            height=45, 
            font_size="13sp",
            bg_color=(0.2, 0.2, 0.2, 1), 
            text_color=COLOR_TEXT_WHITE, 
            radius=[8]
        )
        btn_close.bind(on_press=popup.dismiss)
        box.add_widget(btn_close)
        
        popup.open()

    # --- ПОПЕРЕДЖЕННЯ ПРИ ВИХОДІ ---
    def show_logout_warning(self, instance):
        box = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        email_status = f"[color=00FF66]Прив'язана пошта: {self.user_data.get('email')}[/color]" if self.user_data.get('email') else "[color=FF3333]ПОШТУ НЕ ПРИВ'ЯЗАНО![/color]"

        warning_text = (
            "[color=FF3333][b]УВАГА! ПОПЕРЕДЖЕННЯ ПРО ВИХІД![/b][/color]\n\n"
            "Ви дійсно хочете вийти з акаунту?\n"
            f"{email_status}\n\n"
            "[size=13]Якщо у вас немає прив'язаної пошти, ви можете [b]повністю втратити доступ[/b] "
            "до цього акаунту![/size]"
        )
        
        box.add_widget(Label(text=warning_text, markup=True, halign="center", valign="middle"))
        
        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.35)
        btn_cancel = AsgardButton(text="Скасувати", bg_color=(0.3, 0.3, 0.3, 1), text_color=COLOR_TEXT_WHITE)
        btn_confirm = AsgardButton(text="Так, вийти", bg_color=(0.8, 0.1, 0.1, 1), text_color=COLOR_TEXT_WHITE)
        
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_confirm)
        box.add_widget(btn_box)

        popup = Popup(title="Підтвердження виходу", content=box, size_hint=(0.85, 0.5))
        btn_cancel.bind(on_press=popup.dismiss)
        
        def confirm_exit(x):
            popup.dismiss()
            self.manager.current = 'login'

        btn_confirm.bind(on_press=confirm_exit)
        popup.open()

    # --- ПРИВ'ЯЗКА EMAIL ---
    def show_email_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=15, spacing=12)
        
        current_email = self.user_data.get('email', '')
        status_str = f"Поточна пошта: [color=FFD700]{current_email}[/color]" if current_email else "[color=FF9999]Пошту ще не прив'язано[/color]"
        
        box.add_widget(Label(
            text=f"=== ПРИВ'ЯЗКА ПОШТИ (GMAIL) ===\n{status_str}", 
            markup=True, halign="center", size_hint_y=0.25
        ))

        email_input = TextInput(
            hint_text="Введіть ваш Gmail...",
            text=current_email,
            multiline=False,
            size_hint_y=0.2,
            background_color=(0.1, 0.15, 0.25, 1),
            foreground_color=COLOR_TEXT_WHITE
        )
        box.add_widget(email_input)

        btn_save = AsgardButton(text="Зберегти пошту", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1), size_hint_y=0.25)
        box.add_widget(btn_save)

        res_lbl = Label(text="", size_hint_y=0.2, markup=True)
        box.add_widget(res_lbl)

        popup = Popup(title="Налаштування Gmail", content=box, size_hint=(0.85, 0.55))

        def save_email_act(x):
            mail = email_input.text.strip()
            if mail and "@" in mail:
                try:
                    res = requests.post(f"{SERVER_URL}/set_email", json={"username": self.user_data['username'], "email": mail}, timeout=3).json()
                    if res.get("status") == "ok":
                        self.user_data['email'] = mail
                        res_lbl.text = "[color=00FF66]Пошту успішно збережено![/color]"
                        self.update_header()
                    else:
                        res_lbl.text = f"[color=FF3333]{res.get('message')}[/color]"
                except Exception:
                    res_lbl.text = "[color=FF3333]Помилка зв'язку з сервером![/color]"
            else:
                res_lbl.text = "[color=FF3333]Введіть коректну електронну пошту![/color]"

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
        mail_badge = " [Gmail]" if self.user_data.get('email') else ""
        
        self.info_label.text = (
            f"Гравець: {username}{mail_badge} (ID: {user_id}) | Роль: {self.user_data['role']}\n"
            f"Банк: {bank_capital:.0f} Ю | Баланс: {self.user_data['balance']:.0f} Ю"
        )
        
        role = self.user_data['role']
        if role == "Адмін":
            self.btn_panel.opacity = 1
            self.btn_panel.disabled = False
            self.btn_panel.text = "Пульт"
            self.btn_panel.bg_color = COLOR_ADMIN_RED
        elif role == "Король":
            self.btn_panel.opacity = 1
            self.btn_panel.disabled = False
            self.btn_panel.text = "Пульт"
            self.btn_panel.bg_color = COLOR_GOLD_BTN
        else:
            self.btn_panel.opacity = 0
            self.btn_panel.disabled = True

    def show_tab(self, tab_name):
        self.content_area.clear_widgets()
        self.update_header()
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

    # --- ВКЛАДКА: ЧАТ ---
    def build_chat_tab(self):
        rel_container = RelativeLayout()

        try:
            bg_img = Image(
                source=(resource_path('chat_bg.jpg')), 
                opacity=0.3, 
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
            text="[АКТУАЛЬНИЙ НАКАЗ КОРОЛЯ]: Немає активних наказів на цей час.",
            size_hint_y=0.1, color=COLOR_GOLD, bold=True, halign="center", valign="middle", markup=True, font_size="12sp"
        )
        self.order_board.bind(size=self.order_board.setter('text_size'))
        chat_layout.add_widget(self.order_board)
        
        self.chat_scroll = ScrollView(size_hint_y=0.68)
        self.chat_grid = GridLayout(cols=1, size_hint_y=None, spacing=8, padding=5)
        self.chat_grid.bind(minimum_height=self.chat_grid.setter('height'))
        self.chat_scroll.add_widget(self.chat_grid)
        chat_layout.add_widget(self.chat_scroll)
        
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=5)
        self.msg_input = TextInput(
            hint_text="Напишіть повідомлення...", multiline=False, 
            font_size="13sp",
            background_color=(0.1, 0.15, 0.25, 0.75), foreground_color=COLOR_TEXT_WHITE
        )
        btn_send = AsgardButton(text="Надіслати", size_hint_x=0.3, font_size="12sp", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1))
        btn_send.bind(on_press=self.send_message)
        input_layout.add_widget(self.msg_input)
        input_layout.add_widget(btn_send)
        chat_layout.add_widget(input_layout)
        
        btn_complaint = AsgardButton(
            text="[УВАГА] Подати скаргу на порушника закону", size_hint_y=0.1, font_size="11sp",
            bg_color=(0.5, 0.15, 0.15, 0.85), text_color=COLOR_TEXT_WHITE
        )
        btn_complaint.bind(on_press=self.show_complaint_popup)
        chat_layout.add_widget(btn_complaint)
        
        rel_container.add_widget(chat_layout)
        self.content_area.add_widget(rel_container)

        self.load_king_order()
        self.load_chat()

    def send_message(self, instance):
        text = self.msg_input.text.strip()
        if not text:
            return
        try:
            requests.post(f"{SERVER_URL}/send_message", json={"sender": self.user_data['username'], "text": text}, timeout=3)
            self.msg_input.text = ""
            self.load_chat()
        except Exception:
            pass

    def load_chat(self):
        if not hasattr(self, 'chat_grid'):
            return
        try:
            messages = requests.get(f"{SERVER_URL}/messages", timeout=3).json()
            self.chat_grid.clear_widgets()
            for msg in messages:
                sender = msg["sender"]
                text = msg["text"]
                timestamp = msg["timestamp"]
                sender_id = msg["sender_id"]
                sender_role = msg["sender_role"]
                
                role_tag = f"[{sender_role}] " if sender_role in ["Король", "Адмін"] else ""
                disp_id = sender_id if sender_id else "--"
                color_code = "FF3333" if sender_role == "Адмін" else ("FFD700" if sender_role == "Король" else "99CCFF")
                    
                lbl = Label(
                    text=f"[color={color_code}][{timestamp}] {role_tag}{sender} (ID: {disp_id}):[/color] {text}", 
                    size_hint_y=None, height=35, halign="left", valign="middle", markup=True, font_size="13sp"
                )
                lbl.bind(size=lbl.setter('text_size'))
                self.chat_grid.add_widget(lbl)
        except Exception:
            pass

    def load_king_order(self):
        if not hasattr(self, 'order_board'):
            return
        try:
            res = requests.get(f"{SERVER_URL}/king_order", timeout=3).json()
            if res.get("type"):
                self.order_board.text = f"[color=FFD700][КОРОЛІВСЬКИЙ {res['type'].upper()} ДЛЯ {res['target'].upper()}]:[/color] {res['text']}"
            else:
                self.order_board.text = "[БЕЗПЕКА]: Немає активних указів верхівки."
        except Exception:
            pass

    # --- ВКЛАДКА: ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС) ---
    def build_pm_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=10)
        
        layout.add_widget(Label(
            text="=== ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС) ===", 
            font_size="16sp", color=COLOR_GOLD, bold=True, size_hint_y=0.08
        ))

        self.pm_target_input = TextInput(
            hint_text="Введіть нікнейм або ID отримувача...",
            multiline=False, size_hint_y=0.1, font_size="13sp",
            background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE
        )
        layout.add_widget(self.pm_target_input)

        self.pm_scroll = ScrollView(size_hint_y=0.67)
        self.pm_grid = GridLayout(cols=1, size_hint_y=None, spacing=8, padding=5)
        self.pm_grid.bind(minimum_height=self.pm_grid.setter('height'))
        self.pm_scroll.add_widget(self.pm_grid)
        layout.add_widget(self.pm_scroll)

        pm_input_layout = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=5)
        self.pm_text_input = TextInput(
            hint_text="Текст приватного повідомлення...", multiline=False, font_size="13sp",
            background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE
        )
        btn_send_pm = AsgardButton(text="Надіслати", size_hint_x=0.3, font_size="12sp", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1))
        btn_send_pm.bind(on_press=self.send_pm)
        pm_input_layout.add_widget(self.pm_text_input)
        pm_input_layout.add_widget(btn_send_pm)
        layout.add_widget(pm_input_layout)

        self.content_area.add_widget(layout)
        self.load_pms()

    def send_pm(self, instance):
        target = self.pm_target_input.text.strip()
        text = self.pm_text_input.text.strip()
        if not target or not text:
            return

        try:
            res = requests.post(f"{SERVER_URL}/send_pm", json={"sender": self.user_data['username'], "target": target, "text": text}, timeout=3).json()
            if res.get("status") == "ok":
                self.pm_text_input.text = ""
                self.load_pms()
            else:
                self.show_popup_msg("ЛС Помилка", res.get("message", "Отримувача не знайдено!"))
        except Exception:
            pass

    def load_pms(self):
        if not hasattr(self, 'pm_grid'):
            return
        try:
            username = self.user_data['username']
            pms = requests.get(f"{SERVER_URL}/pms/{username}", timeout=3).json()
            self.pm_grid.clear_widgets()

            for pm in pms:
                s, r, t, tm = pm["sender"], pm["receiver"], pm["text"], pm["timestamp"]
                color_tag = "00FF66" if s == username else "FF9933"
                direction = f"-> До {r}" if s == username else f"<- Від {s}"
                
                lbl = Label(
                    text=f"[color={color_tag}][{tm}] [{direction}]:[/color] {t}",
                    size_hint_y=None, height=35, halign="left", valign="middle", markup=True, font_size="13sp"
                )
                lbl.bind(size=lbl.setter('text_size'))
                self.pm_grid.add_widget(lbl)
        except Exception:
            pass

    # --- ВКЛАДКА: P2P ПЕРЕКАЗИ ---
    def build_transfer_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        layout.add_widget(Label(
            text="=== КІБЕР-БАНКІНГ: ПЕРЕКАЗ ЮНІТІВ ===", 
            font_size="16sp", color=COLOR_GOLD, bold=True, size_hint_y=0.12
        ))

        self.tr_target_input = TextInput(
            hint_text="Нікнейм або ID отримувача...",
            multiline=False, size_hint_y=0.12, font_size="13sp",
            background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE
        )
        layout.add_widget(self.tr_target_input)

        self.tr_amount_input = TextInput(
            hint_text="Сума переказу (Ю)...",
            multiline=False, size_hint_y=0.12, font_size="13sp",
            background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE
        )
        layout.add_widget(self.tr_amount_input)

        btn_transfer = AsgardButton(
            text="ПЕРЕКАЗАТИ КОШТИ",
            size_hint_y=0.18, font_size="13sp", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1)
        )
        btn_transfer.bind(on_press=self.exec_transfer)
        layout.add_widget(btn_transfer)

        self.tr_status_label = Label(
            text="Миттєвий переказ грошей підданим Азгарду.",
            font_size="13sp", color=COLOR_TEXT_WHITE, bold=True, halign="center", size_hint_y=0.46
        )
        layout.add_widget(self.tr_status_label)

        self.content_area.add_widget(layout)

    def exec_transfer(self, instance):
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
            self.tr_status_label.text = "[color=FF3333]Введіть числове значення суми![/color]"
            self.tr_status_label.markup = True
        except Exception:
            self.tr_status_label.text = "[color=FF3333]Сервер недоступний![/color]"
            self.tr_status_label.markup = True

    # --- ВКЛАДКА: КАЗИНО ---
    def build_casino_tab(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        layout.add_widget(Label(
            text="=== КАЗИНО АЗГАРДУ: КОЛЕСО ФОРТУНИ ===", 
            font_size="16sp", color=COLOR_GOLD, bold=True, size_hint_y=0.1
        ))

        info_text = (
            "[b][color=FFD700]СЕКТОРИ КОЛЕСА:[/color][/b]\n"
            "* [color=00FF66]2x (Подвоєння)[/color] — Шанс 10%\n"
            "* [color=99CCFF]x0.5 (Повернення 50%)[/color] — Шанс 20%\n"
            "* [color=FF3333]4x БАНКРУТ (Втрата всієї ставки)[/color] — Шанс 70%"
        )
        layout.add_widget(Label(text=info_text, markup=True, halign="center", font_size="12sp", size_hint_y=0.25))

        self.casino_bet_input = TextInput(
            hint_text="Введіть суму ставки (Ю)...",
            multiline=False, size_hint_y=0.12, font_size="13sp",
            background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE
        )
        layout.add_widget(self.casino_bet_input)

        btn_spin = AsgardButton(
            text="КРУТИТИ КОЛЕСО",
            size_hint_y=0.18, font_size="13sp", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1)
        )
        btn_spin.bind(on_press=self.spin_casino)
        layout.add_widget(btn_spin)

        self.casino_result_label = Label(
            text="Зробіть ставку та випробуйте свою удачу!",
            font_size="13sp", color=COLOR_TEXT_WHITE, bold=True, halign="center", size_hint_y=0.25
        )
        layout.add_widget(self.casino_result_label)

        self.content_area.add_widget(layout)

    def spin_casino(self, instance):
        bet_str = self.casino_bet_input.text.strip()
        if not bet_str:
            self.casino_result_label.text = "[color=FF3333]Введіть суму ставки![/color]"
            self.casino_result_label.markup = True
            return

        try:
            bet = float(bet_str)
            res = requests.post(f"{SERVER_URL}/spin_wheel", json={"username": self.user_data['username'], "bet": bet}, timeout=3).json()

            if res.get("status") == "ok":
                msg = res.get("message", "")
                self.casino_result_label.text = msg
                self.update_header()
            else:
                self.casino_result_label.text = f"[color=FF3333]{res.get('message', 'Помилка!')}[/color]"
                self.casino_result_label.markup = True
        except ValueError:
            self.casino_result_label.text = "[color=FF3333]Введіть числове значення ставки![/color]"
            self.casino_result_label.markup = True
        except Exception:
            self.casino_result_label.text = "[color=FF3333]Сервер недоступний![/color]"
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
        box = BoxLayout(orientation='vertical', padding=12, spacing=10)
        self.target_input = TextInput(hint_text="Нікнейм або ID порушника", multiline=False, background_color=(0.08, 0.12, 0.2, 1), foreground_color=COLOR_TEXT_WHITE)
        self.reason_input = TextInput(hint_text="Яке саме правило з кодексу порушено?", background_color=(0.08, 0.12, 0.2, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_submit = AsgardButton(text="ВІДПРАВИТИ СУДДІ", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1))
        box.add_widget(self.target_input)
        box.add_widget(self.reason_input)
        box.add_widget(btn_submit)
        
        popup = Popup(title="Повідомити про правопорушення", content=box, size_hint=(0.85, 0.55))
        btn_submit.bind(on_press=lambda x: self.submit_complaint(popup))
        popup.open()

    def submit_complaint(self, popup):
        raw_target = self.target_input.text.strip()
        reason = self.reason_input.text.strip()
        if raw_target and reason:
            try:
                requests.post(f"{SERVER_URL}/submit_complaint", json={"reporter": self.user_data['username'], "target": raw_target, "reason": reason}, timeout=3)
            except Exception:
                pass
        popup.dismiss()

    # --- ВКЛАДКА: ДЕРЖАВНИЙ МАГАЗИН ---
    def build_shop_tab(self):
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=15, padding=12)
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text="=== ДЕРЖАВНИЙ МАГАЗИН АЗГАРДУ ===", font_size="16sp", color=COLOR_GOLD, bold=True, size_hint_y=None, height=40))
        grid.add_widget(Label(text="--- ВІП СТАТУСИ ---", font_size="14sp", color=COLOR_GOLD, bold=True, size_hint_y=None, height=30))
        
        vips = [(1, "Віпка (Рівень 1)", 700, "+10% до зарплати"), (2, "Віпка 2 (Рівень 2)", 1000, "+20% до зарплати"), (3, "Віпка 3 (Рівень 3)", 2000, "2х зарплатні")]
        for level, label, price, desc in vips:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
            row.add_widget(Label(text=f"[b]{label}[/b]\n[size=12]{desc}[/size]", markup=True, color=COLOR_TEXT_WHITE, size_hint_x=0.5, halign='left'))
            row.add_widget(Label(text=f"{price} Ю", color=COLOR_GOLD, size_hint_x=0.2, bold=True))
            btn = AsgardButton(text="Купити", font_size="12sp", bg_color=COLOR_GOLD_BTN, size_hint_x=0.3, radius=[5])
            btn.bind(on_press=lambda instance, lvl=level, pr=price, lbl=label: self.buy_vip(lvl, pr, lbl))
            row.add_widget(btn)
            grid.add_widget(row)
            
        vip4_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        vip4_row.add_widget(Label(text="[b]Віпка 4 (Рівень 4)[/b]\n[size=12]2х зарплатні[/size]", markup=True, color=(0.5, 0.7, 0.9, 1), size_hint_x=0.5, halign='left'))
        vip4_row.add_widget(Label(text="Безцінно", color=COLOR_RED, size_hint_x=0.2, bold=True))
        vip4_btn = AsgardButton(text="За досягнення", font_size="10sp", bg_color=(0.2, 0.2, 0.2, 1), text_color=(0.5, 0.5, 0.5, 1), size_hint_x=0.3, radius=[5], disabled=True)
        vip4_row.add_widget(vip4_btn)
        grid.add_widget(vip4_row)
        
        grid.add_widget(Label(text="--- ДЕРЖАВНІ ДОЗВОЛИ ---", font_size="14sp", color=COLOR_GOLD, bold=True, size_hint_y=None, height=30))
        permits = [("sell", "Дозвіл на продаж", 500), ("territory", "Дозвіл на власність території", 300), ("food", "Дозвіл на продаваня їжі", 200), ("weapons", "Дозвіл на виробництво зброї", 250), ("tools", "Дозвіл на виробництво інструментів", 250)]
        for key, label, price in permits:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
            row.add_widget(Label(text=label, font_size="11sp", color=COLOR_TEXT_WHITE, size_hint_x=0.5, halign='left'))
            row.add_widget(Label(text=f"{price} Ю", color=COLOR_GOLD, size_hint_x=0.2, bold=True))
            btn = AsgardButton(text="Придбати", font_size="12sp", bg_color=COLOR_GOLD_BTN, size_hint_x=0.3, radius=[5])
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
                self.show_popup_msg("Успішно", f"Вітаємо! Ви придбали {label}!")
            else:
                self.show_popup_msg("Магазин", res.get("message", "Помилка"))
        except Exception:
            pass

    def buy_permit(self, key, price, label):
        try:
            res = requests.post(f"{SERVER_URL}/buy_permit", json={"username": self.user_data['username'], "key": key, "price": price}, timeout=3).json()
            if res.get("status") == "ok":
                self.update_header()
                self.show_popup_msg("Успішно", f"Придбано державний {label}!")
            else:
                self.show_popup_msg("Магазин", res.get("message", "Помилка"))
        except Exception:
            pass

    def show_popup_msg(self, title, message):
        box = BoxLayout(orientation='vertical', padding=15, spacing=15)
        box.add_widget(Label(text=message, color=COLOR_TEXT_WHITE, halign="center"))
        btn = AsgardButton(text="Зрозуміло", bg_color=COLOR_GOLD_BTN, size_hint_y=0.4)
        box.add_widget(btn)
        popup = Popup(title=title, content=box, size_hint=(0.8, 0.35))
        btn.bind(on_press=popup.dismiss)
        popup.open()

    # --- ВКЛАДКА: РИНОК ---
    def build_market_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=10)
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=10)
        top_bar.add_widget(Label(text="=== РИНОК АЗГАРДУ ===", font_size="15sp", color=COLOR_GOLD, bold=True, halign="left"))
        btn_sell = AsgardButton(text="Виставити предмет", font_size="11sp", size_hint_x=0.4, bg_color=COLOR_GOLD_BTN, radius=[5])
        btn_sell.bind(on_press=self.show_sell_popup)
        top_bar.add_widget(btn_sell)
        layout.add_widget(top_bar)
        
        self.market_scroll = ScrollView(size_hint_y=0.88)
        self.market_grid = GridLayout(cols=1, size_hint_y=None, spacing=12, padding=5)
        self.market_grid.bind(minimum_height=self.market_grid.setter('height'))
        self.market_scroll.add_widget(self.market_grid)
        layout.add_widget(self.market_scroll)
        
        self.content_area.add_widget(layout)
        self.load_market_items()

    def load_market_items(self):
        if not hasattr(self, 'market_grid'):
            return
        try:
            items = requests.get(f"{SERVER_URL}/market_items", timeout=3).json()
            self.market_grid.clear_widgets()
            current_user = self.user_data['username']
            current_role = self.user_data['role']
            
            for item in items:
                item_id, seller, item_name, price, desc = item["id"], item["seller"], item["item_name"], item["price"], item["description"]
                row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=75, spacing=10)
                desc_str = f"\n[size=12][color=bbbbbb]{desc}[/color][/size]" if desc else ""
                item_lbl = Label(
                    text=f"[b]{item_name}[/b] - [color=FFD700]{price:.1f} Ю[/color]\n[size=12]Продавець: {seller}[/size]{desc_str}",
                    markup=True, size_hint_x=0.65, halign="left", valign="middle"
                )
                item_lbl.bind(size=item_lbl.setter('text_size'))
                row_layout.add_widget(item_lbl)
                
                if seller == current_user:
                    btn_action = AsgardButton(text="Забрати", font_size="11sp", bg_color=(0.5, 0.3, 0.1, 1), size_hint_x=0.35, radius=[5])
                    btn_action.bind(on_press=lambda instance, i_id=item_id: self.cancel_market_item(i_id))
                elif current_role == "Адмін":
                    btn_action = AsgardButton(text="Видалити (Admin)", font_size="10sp", bg_color=COLOR_ADMIN_RED, text_color=COLOR_TEXT_WHITE, size_hint_x=0.35, radius=[5])
                    btn_action.bind(on_press=lambda instance, i_id=item_id: self.cancel_market_item(i_id, is_admin_override=True))
                else:
                    btn_action = AsgardButton(text="Купити", font_size="11sp", bg_color=(0.1, 0.5, 0.3, 1), text_color=COLOR_TEXT_WHITE, size_hint_x=0.35, radius=[5])
                    btn_action.bind(on_press=lambda instance, i_id=item_id, pr=price, sel=seller, item=item_name: self.buy_market_item(i_id, pr, sel, item))
                    
                row_layout.add_widget(btn_action)
                self.market_grid.add_widget(row_layout)
                sep = Label(text="----------------------------------------------------------------", size_hint_y=None, height=5, color=(0.15, 0.22, 0.33, 1))
                self.market_grid.add_widget(sep)
        except Exception:
            pass

    def show_sell_popup(self, instance):
        box = BoxLayout(orientation='vertical', padding=12, spacing=10)
        self.market_item_input = TextInput(hint_text="Назва предмету...", multiline=False, background_color=(0.08, 0.12, 0.2, 1), foreground_color=COLOR_TEXT_WHITE)
        self.market_price_input = TextInput(hint_text="Ціна (Юніти)...", multiline=False, background_color=(0.08, 0.12, 0.2, 1), foreground_color=COLOR_TEXT_WHITE)
        self.market_desc_input = TextInput(hint_text="Опис предмета (необов'язково)...", background_color=(0.08, 0.12, 0.2, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_add = AsgardButton(text="ВИСТАВИТИ НА РИНОК", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1))
        box.add_widget(self.market_item_input)
        box.add_widget(self.market_price_input)
        box.add_widget(self.market_desc_input)
        box.add_widget(btn_add)
        
        popup = Popup(title="Створення торгового лоту", content=box, size_hint=(0.85, 0.65))
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
            except ValueError:
                pass
        popup.dismiss()

    def cancel_market_item(self, item_id, is_admin_override=False):
        try:
            requests.post(f"{SERVER_URL}/cancel_market", json={"item_id": item_id, "seller": self.user_data['username'], "is_admin": is_admin_override}, timeout=3)
            self.load_market_items()
        except Exception:
            pass

    def buy_market_item(self, item_id, price, seller, item_name):
        try:
            res = requests.post(f"{SERVER_URL}/buy_market", json={"buyer": self.user_data['username'], "item_id": item_id, "price": price, "seller": seller, "item_name": item_name}, timeout=3).json()
            if res.get("status") == "ok":
                self.update_header()
                self.load_market_items()
                self.show_popup_msg("Ринкова угода", f"Ви успішно придбали {item_name}!")
            else:
                self.show_popup_msg("Помилка купівлі", res.get("message", "Помилка"))
        except Exception:
            pass

    # --- ВКЛАДКА: ГРОМАДЯНИ ---
    def build_citizens_tab(self):
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=12, padding=12)
        grid.bind(minimum_height=grid.setter('height'))
        grid.add_widget(Label(text="=== РЕЄСТР ЖИТЕЛІВ АЗГАРДУ ===", font_size="16sp", color=COLOR_GOLD, bold=True, size_hint_y=None, height=40))
        
        try:
            users = requests.get(f"{SERVER_URL}/citizens", timeout=3).json()
            for u in users:
                username, u_id, role, bal, vip = u["username"], u["user_id"], u["role"], u["balance"], u["vip_level"]
                p_sell, p_terr, p_food, p_weapon, p_tool = u["permit_sell"], u["permit_territory"], u["permit_food"], u["permit_weapons"], u["permit_tools"]
                email = u.get("email", "")
                
                vip_text = "Немає"
                if vip == 1: vip_text = "Віпка 1 (+10% до з/п)"
                elif vip == 2: vip_text = "Віпка 2 (+20% до з/п)"
                elif vip == 3: vip_text = "Віпка 3 (2х з/п)"
                elif vip == 4: vip_text = "Віпка 4 (Досягнення)"
                
                permits = []
                if p_sell: permits.append("Продаж")
                if p_terr: permits.append("Територія")
                if p_food: permits.append("Їжа")
                if p_weapon: permits.append("Зброя")
                if p_tool: permits.append("Інструменти")
                permits_text = ", ".join(permits) if permits else "Відсутні"
                
                email_text = f" | [color=88BBFF]Gmail: {email}[/color]" if email else " | [color=666666]Без пошти[/color]"
                
                card_text = (
                    f"[color=FFD700][ID: {u_id}] {username}[/color]{email_text} | Роль: {role} | Капітал: {bal:.0f} Ю\n"
                    f"[color=FFB300]ВІП-Статус:[/color] {vip_text}\n"
                    f"[color=00FFCC]Дозволи:[/color] {permits_text}"
                )
                lbl = Label(text=card_text, markup=True, size_hint_y=None, height=80, halign="left", valign="middle", font_size="12sp")
                lbl.bind(size=lbl.setter('text_size'))
                grid.add_widget(lbl)
                sep = Label(text="----------------------------------------------------------------", size_hint_y=None, height=10, color=(0.2, 0.3, 0.4, 1))
                grid.add_widget(sep)
        except Exception:
            pass
        
        scroll.add_widget(grid)
        self.content_area.add_widget(scroll)

    # --- ВКЛАДКА: ЗАКОНИ ---
    def build_rules_tab(self):
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=12, padding=12)
        grid.bind(minimum_height=grid.setter('height'))
        
        title = Label(text="=== КОДЕКС ЗАКОНІВ АЗГАРДУ ===", font_size="16sp", color=COLOR_GOLD, bold=True, size_hint_y=None, height=40)
        grid.add_widget(title)
        
        rules_text = (
            "[b][color=FFD700]ЗАКОНИ ДЛЯ ЧАТУ (ЦЗ АЗГАРДУ)[/color][/b]\n\n"
            "[b][color=FFD700]1.[/color][/b] Не вживати нецензурну лексику.\n[color=FF4D4D]  - Наслідок: Штраф / мут.[/color]\n\n"
            "[b][color=FFD700]2.[/color][/b] Не принижувати гідність іншого Азгардця (не ображати).\n[color=FF4D4D]  - Наслідок: Штраф (при повторенні двічі на день — суд).[/color]\n\n"
            "[b][color=FFD700]3.[/color][/b] Погане висловлювання щодо рідні союзників або іншого Азгардця суворо заборонене.\n[color=FF4D4D]  - Наслідок: Суд / великий штраф.[/color]\n\n"
            "[b][color=FFD700]4.[/color][/b] Погрози заборонені.\n[color=FF4D4D]  - Наслідок: Штраф.[/color]\n\n"
            "[b][color=FFD700]5.[/color][/b] Не висловлюватися негативно на Короля без поважних причин.\n[color=FF4D4D]  - Наслідок: Мут.[/color]\n\n"
            "[b][color=FFD700]6.[/color][/b] Не змінювати профіль головної бесіди без дозволу верхівки.\n[color=FF4D4D]  - Наслідок: Невеликий штраф.[/color]\n\n"
            "[b][color=FFD700]7.[/color][/b] Не спамити одними і тими самими повідомленнями.\n[color=FF4D4D]  - Наслідок: Штраф / mut (при частому повторенні — суд).[/color]\n\n"
            "[b][color=FFD700]8.[/color][/b] Не надсилати контент 18+.\n[color=FF4D4D]  - Наслідок: Суд.[/color]\n\n"
            "[b][color=FFD700]9.[/color][/b] Не створювати голосування без оголошення віче.\n[color=FF4D4D]  - Наслідок: Штраф / мут.[/color]\n\n"
            "[b][color=FFD700]10.[/color][/b] Не розповсюджувати інформацію про Королівство без дозволу Короля.\n[color=FF4D4D]  - Наслідок: Суд / вигнання.[/color]\n\n"
            "[b][color=FFD700]11.[/color][/b] Не створювати нові бесіди на тему Королівства без відомості Короля.\n[color=FF4D4D]  - Наслідок: Великий штраф.[/color]\n\n"
            "[b][color=FFD700]12.[/color][/b] Сепаратизм у сторону Азгарду суворо заборонений.\n[color=FF4D4D]  - Наслідок: Вигнання.[/color]\n\n"
            "[b][color=FFD700]13.[/color][/b] Уникання конфліктів обов'язкове.\n[color=FF4D4D]  - Наслідок: Штраф для обох сторін.[/color]\n\n"
            "[b][color=FFD700]14.[/color][/b] Цифровий сепаратизм суворо заборонений.\n[color=FF4D4D]  - Наслідок: Великі штрафи + суд + виправні роботи.[/color]\n\n"
            "----------------------------------------------------\n"
            "[b][color=FFD700]ЗАКОНИ ПОЗАЦИФРОВОГО ПРОСТОРУ (ЗПП АЗГАРДУ)[/color][/b]\n\n"
            "[b][color=FFD700]1.[/color][/b] Уникати конфліктів.\n[color=FF4D4D]  - Наслідок: Штраф або суд для обох сторін.[/color]\n\n"
            "[b][color=FFD700]2.[/color][/b] У випадку бійки винен той, хто завдав перший удар.\n[color=FF4D4D]  - Наслідок: Великі штрафи та суд.[/color]\n\n"
            "[b][color=FFD700]3.[/color][/b] Невиконання наказів Короля без відповідних причин суворо карається.\n[color=FF4D4D]  - Наслідок: Штраф та змушення до виправних робіт.[/color]\n\n"
            "[b][color=FFD700]4.[/color][/b] Володіння бізнесом чи територією без придбаних дозволів суворо карається.\n[color=FF4D4D]  - Наслідок: Забирання майна + суд.[/color]\n\n"
            "[b][color=FFD700]5.[/color][/b] Нелегітимне володіння зброєю суворо заборонене.\n[color=FF4D4D]  - Наслідок: Штраф + суд.[/color]\n\n"
            "[b][color=FFD700]6.[/color][/b] Заборона вживання спиртних виробів до 14 років.\n[color=FF4D4D]  - Наслідок: Суд.[/color]\n\n"
            "[b][color=FFD700]7.[/color][/b] Уникати конфлікту з членом іншої держави.\n[color=FF4D4D]  - Наслідок: Суд.[/color]\n\n"
            "[b][color=FFD700]8.[/color][/b] Несплата податків за територію карається.\n[color=FF4D4D]  - Наслідок: Виправні роботи.[/color]\n\n"
            "[b][color=FFD700]17.[/color][/b] Незнання закону не ухиляє вас від відповідальності.\n\n"
            "[b][color=FFD700]18.[/color][/b] Зневага до Азгардської символіки карається.\n[color=FF4D4D]  - Наслідок: Штраф.[/color]\n\n"
            "[size=12]Віче — народний радний заход, в якому верхівка не має більшого пріоритету.[/size]"
        )
        
        lbl_content = Label(text=rules_text, markup=True, font_size="12sp", size_hint_y=None, halign='left', valign='top', color=COLOR_TEXT_WHITE)
        lbl_content.bind(texture_size=lbl_content.setter('size'))
        lbl_content.bind(width=lambda im, val: setattr(lbl_content, 'text_size', (val, None)))
        
        grid.add_widget(lbl_content)
        scroll.add_widget(grid)
        self.content_area.add_widget(scroll)

    # --- ПУЛЬТ КЕРУВАННЯ ---
    def open_control_panel(self, instance):
        role = self.user_data['role']
        is_admin = (role == "Адмін")
        
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        title_text = "*** ПУЛЬТ АБСОЛЮТНОГО АДМІНІСТРУВАННЯ АЗГАРДОМ ***" if is_admin else "*** ПУЛЬТ ВЕРХОВНОГО КЕРУВАННЯ АЗГАРДОМ ***"
        title_color = COLOR_RED if is_admin else COLOR_GOLD
        
        popup_layout.add_widget(Label(text=title_text, font_size="14sp", color=title_color, bold=True, size_hint_y=None, height=35))
        
        scroll = ScrollView(size_hint_y=0.9)
        content_grid = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=5)
        content_grid.bind(minimum_height=content_grid.setter('height'))
        
        if is_admin:
            content_grid.add_widget(Label(text="--- СУПЕР СИЛА БОГІВ АЗГАРДУ ---", font_size="12sp", size_hint_y=None, height=25, color=COLOR_RED, bold=True))
            role_mgmt = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
            self.role_target_input = TextInput(hint_text="Нік або ID...", multiline=False, background_color=(0.15, 0.05, 0.05, 1), foreground_color=COLOR_TEXT_WHITE)
            btn_make_king = AsgardButton(text="Зробити Королем", font_size="10sp", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1), radius=[5])
            btn_demote = AsgardButton(text="Зробити Громадянином", font_size="10sp", bg_color=(0.4, 0.4, 0.4, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
            btn_make_king.bind(on_press=lambda x: self.send_admin_act({"action": "set_role", "role": "Король", "target": self.role_target_input.text}))
            btn_demote.bind(on_press=lambda x: self.send_admin_act({"action": "set_role", "role": "Громадянин", "target": self.role_target_input.text}))
            role_mgmt.add_widget(self.role_target_input)
            role_mgmt.add_widget(btn_make_king)
            role_mgmt.add_widget(btn_demote)
            content_grid.add_widget(role_mgmt)
            
            delete_mgmt = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
            self.delete_target_input = TextInput(hint_text="ID чи нік...", multiline=False, background_color=(0.15, 0.05, 0.05, 1), foreground_color=COLOR_TEXT_WHITE)
            btn_delete_acc = AsgardButton(text="ВИДАЛИТИ АКАУНТ", font_size="10sp", bg_color=(0.9, 0.1, 0.1, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
            btn_delete_acc.bind(on_press=lambda x: self.send_admin_act({"action": "delete", "target": self.delete_target_input.text, "admin_user": self.user_data['username']}))
            delete_mgmt.add_widget(self.delete_target_input)
            delete_mgmt.add_widget(btn_delete_acc)
            content_grid.add_widget(delete_mgmt)
            content_grid.add_widget(Label(text="----------------------------------------------------------------", size_hint_y=None, height=10, color=COLOR_RED))

        content_grid.add_widget(Label(text="Державні скарги громадян:", font_size="12sp", size_hint_y=None, height=25, color=COLOR_RED, bold=True))
        self.complaints_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
        self.complaints_scroll = ScrollView()
        self.complaints_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.complaints_grid.bind(minimum_height=self.complaints_grid.setter('height'))
        self.complaints_scroll.add_widget(self.complaints_grid)
        self.complaints_box.add_widget(self.complaints_scroll)
        content_grid.add_widget(self.complaints_box)
        
        content_grid.add_widget(Label(text="Дисциплінарний Комітет (Бан/Розбан):", font_size="12sp", size_hint_y=None, height=25, color=COLOR_GOLD, bold=True))
        ban_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.ban_input = TextInput(hint_text="Нік або ID...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_ban = AsgardButton(text="Забанити", font_size="10sp", bg_color=(0.7, 0.1, 0.1, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_unban = AsgardButton(text="Розбанити", font_size="10sp", bg_color=(0.1, 0.5, 0.1, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_ban.bind(on_press=lambda x: self.send_admin_act({"action": "ban", "target": self.ban_input.text, "admin_user": self.user_data['username']}))
        btn_unban.bind(on_press=lambda x: self.send_admin_act({"action": "unban", "target": self.ban_input.text}))
        ban_layout.add_widget(self.ban_input)
        ban_layout.add_widget(btn_ban)
        ban_layout.add_widget(btn_unban)
        content_grid.add_widget(ban_layout)
        
        content_grid.add_widget(Label(text="Державна Казначея (Юніти):", font_size="12sp", size_hint_y=None, height=25, color=COLOR_GOLD, bold=True))
        bank_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.bank_target = TextInput(hint_text="Нік або ID...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        self.bank_amount = TextInput(hint_text="Сума...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_give = AsgardButton(text="+ Дати", font_size="10sp", bg_color=(0.1, 0.5, 0.3, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_take = AsgardButton(text="- Забрати", font_size="10sp", bg_color=(0.5, 0.3, 0.1, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_set = AsgardButton(text="= Встановити", font_size="9sp", bg_color=(0.2, 0.4, 0.6, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_give.bind(on_press=lambda x: self.send_admin_act({"action": "units", "mode": "add", "target": self.bank_target.text, "amount": self.bank_amount.text}))
        btn_take.bind(on_press=lambda x: self.send_admin_act({"action": "units", "mode": "sub", "target": self.bank_target.text, "amount": self.bank_amount.text}))
        btn_set.bind(on_press=lambda x: self.send_admin_act({"action": "units", "mode": "set", "target": self.bank_target.text, "amount": self.bank_amount.text}))
        bank_layout.add_widget(self.bank_target)
        bank_layout.add_widget(self.bank_amount)
        bank_layout.add_widget(btn_give)
        bank_layout.add_widget(btn_take)
        bank_layout.add_widget(btn_set)
        content_grid.add_widget(bank_layout)

        content_grid.add_widget(Label(text="Надання ВІП-Рангів (0-4):", font_size="12sp", size_hint_y=None, height=25, color=COLOR_GOLD, bold=True))
        vip_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.vp_target = TextInput(hint_text="Нік або ID...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        self.vp_vip_level = TextInput(hint_text="Рівень (0-4)...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_set_vip = AsgardButton(text="Встановити ВІП", font_size="10sp", bg_color=(0.1, 0.5, 0.7, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_set_vip.bind(on_press=lambda x: self.send_admin_act({"action": "vip", "target": self.vp_target.text, "vip_level": self.vp_vip_level.text}))
        vip_layout.add_widget(self.vp_target)
        vip_layout.add_widget(self.vp_vip_level)
        vip_layout.add_widget(btn_set_vip)
        content_grid.add_widget(vip_layout)

        content_grid.add_widget(Label(text="Керування Дозволами (продаж / тер / їжа / зброя / інстр):", font_size="11sp", size_hint_y=None, height=25, color=COLOR_GOLD, bold=True))
        permit_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.perm_target = TextInput(hint_text="Нік або ID...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        self.perm_type = TextInput(hint_text="Тип...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_give_perm = AsgardButton(text="Дати дозвіл", font_size="10sp", bg_color=(0.1, 0.6, 0.3, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_revoke_perm = AsgardButton(text="Забрати", font_size="10sp", bg_color=(0.7, 0.2, 0.2, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_give_perm.bind(on_press=lambda x: self.handle_permit_act(1))
        btn_revoke_perm.bind(on_press=lambda x: self.handle_permit_act(0))
        permit_layout.add_widget(self.perm_target)
        permit_layout.add_widget(self.perm_type)
        permit_layout.add_widget(btn_give_perm)
        permit_layout.add_widget(btn_revoke_perm)
        content_grid.add_widget(permit_layout)
        
        content_grid.add_widget(Label(text="Капітал Банку:", font_size="12sp", size_hint_y=None, height=25, color=COLOR_GOLD, bold=True))
        capital_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.capital_input = TextInput(hint_text="Сума...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_set_capital = AsgardButton(text="Встановити Капітал", font_size="10sp", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1), radius=[5])
        btn_set_capital.bind(on_press=lambda x: self.send_admin_act({"action": "capital", "capital": self.capital_input.text}))
        capital_layout.add_widget(self.capital_input)
        capital_layout.add_widget(btn_set_capital)
        content_grid.add_widget(capital_layout)
        
        content_grid.add_widget(Label(text="Оголошення Наказів / Завдань:", font_size="12sp", size_hint_y=None, height=25, color=COLOR_GOLD, bold=True))
        order_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.order_target = TextInput(hint_text="Нік, ID або Усім...", multiline=False, background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        self.order_text = TextInput(hint_text="Текст...", background_color=(0.1, 0.15, 0.25, 1), foreground_color=COLOR_TEXT_WHITE)
        btn_cmd = AsgardButton(text="Наказ", font_size="10sp", bg_color=COLOR_GOLD_BTN, text_color=(0, 0, 0, 1), radius=[5])
        btn_task = AsgardButton(text="Завдання", font_size="10sp", bg_color=(0.2, 0.5, 0.7, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_cmd.bind(on_press=lambda x: self.send_admin_act({"action": "royal_order", "order_type": "Наказ", "target": self.order_target.text, "text": self.order_text.text, "role": self.user_data['role']}))
        btn_task.bind(on_press=lambda x: self.send_admin_act({"action": "royal_order", "order_type": "Завдання", "target": self.order_target.text, "text": self.order_text.text, "role": self.user_data['role']}))
        order_layout.add_widget(self.order_target)
        order_layout.add_widget(self.order_text)
        order_layout.add_widget(btn_cmd)
        order_layout.add_widget(btn_task)
        content_grid.add_widget(order_layout)
        
        content_grid.add_widget(Label(text="Збори та Державний Порядок:", font_size="12sp", size_hint_y=None, height=25, color=COLOR_GOLD, bold=True))
        btn_tax = AsgardButton(text="Зібрати податок з усіх (По 50 Ю)", size_hint_y=None, height=40, font_size="11sp", bg_color=(0.5, 0.4, 0.1, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        btn_tax.bind(on_press=lambda x: self.send_admin_act({"action": "taxes"}))
        content_grid.add_widget(btn_tax)
        
        scroll.add_widget(content_grid)
        popup_layout.add_widget(scroll)
        
        btn_close = AsgardButton(text="Закрити пульт керування", size_hint_y=None, height=40, font_size="11sp", bg_color=(0.2, 0.2, 0.2, 1), text_color=COLOR_TEXT_WHITE, radius=[5])
        popup_layout.add_widget(btn_close)
        
        king_popup = Popup(title="Панель Керування Азгардом", content=popup_layout, size_hint=(0.98, 0.98))
        btn_close.bind(on_press=king_popup.dismiss)
        
        self.load_complaints()
        king_popup.open()

    def send_admin_act(self, payload):
        try:
            requests.post(f"{SERVER_URL}/admin_action", json=payload, timeout=3)
            self.update_header()
            self.load_complaints()
            self.load_king_order()
        except Exception:
            pass

    def handle_permit_act(self, val):
        term = self.perm_type.text.strip().lower()
        col = None
        if term in ["продаж", "sell", "продажi"]: 
            col = "permit_sell"
        elif term in ["територія", "тер", "territory", "територiя"]: 
            col = "permit_territory"
        elif term in ["їжа", "food", "їжi"]: 
            col = "permit_food"
        elif term in ["зброя", "weapon", "weapons", "зброї"]: 
            col = "permit_weapons"
        elif term in ["інструменти", "інстр", "tools", "інструментів", "iнструменти"]: 
            col = "permit_tools"
        
        if col:
            self.send_admin_act({"action": "permit", "target": self.perm_target.text, "column": col, "val": val})

    def load_complaints(self):
        if not hasattr(self, 'complaints_grid'):
            return
        try:
            items = requests.get(f"{SERVER_URL}/complaints", timeout=3).json()
            self.complaints_grid.clear_widgets()
            for c in items:
                lbl = Label(text=f"[color=FFD700]Скарга #{c['id']}:[/color] від {c['reporter']} на {c['target']}\n -> Суть: {c['reason']}", size_hint_y=None, height=45, halign="left", markup=True, font_size="11sp")
                lbl.bind(size=lbl.setter('text_size'))
                self.complaints_grid.add_widget(lbl)
        except Exception:
            pass


class AsgardApp(App):
    def build(self):
        self.current_user = {}
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainGameScreen(name='main_game'))
        return sm


if __name__ == '__main__':
    AsgardApp().run()
