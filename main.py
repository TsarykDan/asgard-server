import os
import sys
import requests

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatIconButton, MDIconButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

SERVER_URL = "https://asgard-server-xu8n.onrender.com"

KV = '''
<GoldButton@MDFillRoundFlatIconButton>:
    md_bg_color: 0.1, 0.13, 0.2, 1
    line_color: 0.85, 0.65, 0.13, 1
    text_color: 0.9, 0.75, 0.2, 1
    icon_color: 0.9, 0.75, 0.2, 1
    font_style: "Caption"
    elevation: 0

MDScreenManager:
    LoginScreen:
        name: 'login'
    MainGameScreen:
        name: 'main_game'

<LoginScreen>:
    md_bg_color: 0.05, 0.07, 0.12, 1
    MDBoxLayout:
        orientation: 'vertical'
        padding: "30dp"
        spacing: "15dp"
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        adaptive_height: True

        MDLabel:
            text: "АЗГАРД"
            font_style: "H4"
            bold: True
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.95, 0.75, 0.2, 1

        MDTextField:
            id: username_field
            hint_text: "Введіть свій нікнейм..."
            mode: "round"
            fill_color_normal: 0.1, 0.13, 0.2, 1
            text_color_focus: 1, 1, 1, 1

        MDTextField:
            id: code_field
            hint_text: "Код Короля / Адміна (якщо є)..."
            password: True
            mode: "round"
            fill_color_normal: 0.1, 0.13, 0.2, 1
            text_color_focus: 1, 1, 1, 1

        MDRaisedButton:
            text: "УВІЙТИ В КОРОЛІВСТВО"
            pos_hint: {'center_x': 0.5}
            md_bg_color: 0.85, 0.65, 0.13, 1
            text_color: 0, 0, 0, 1
            font_style: "Button"
            on_release: root.check_login_flow()

        MDLabel:
            id: error_lbl
            text: ""
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.9, 0.2, 0.2, 1

<MainGameScreen>:
    md_bg_color: 0.05, 0.07, 0.12, 1

    MDBoxLayout:
        orientation: 'vertical'

        # --- ВЕРХНЯ ПАНЕЛЬ (HEADER) ---
        MDCard:
            orientation: 'vertical'
            size_hint_y: None
            adaptive_height: True
            padding: ["12dp", "8dp", "12dp", "12dp"]
            spacing: "4dp"
            md_bg_color: 0.08, 0.1, 0.16, 1
            radius: [0, 0, 16, 16]

            MDBoxLayout:
                size_hint_y: None
                height: "30dp"
                MDIconButton:
                    icon: "logout"
                    theme_text_color: "Custom"
                    text_color: 0.6, 0.6, 0.6, 1
                    on_release: root.logout_act()
                Widget:
                MDIconButton:
                    id: btn_panel
                    icon: "shield-crown"
                    theme_text_color: "Custom"
                    text_color: 0.85, 0.65, 0.13, 1
                    opacity: 0
                    disabled: True
                    on_release: root.open_control_panel()

            MDLabel:
                text: "К О РО Л І В С Т В О"
                font_style: "Caption"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.7, 0.6, 0.3, 1
                adaptive_height: True

            MDLabel:
                text: "АЗГАРД"
                font_style: "H6"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.95, 0.75, 0.2, 1
                adaptive_height: True

            MDBoxLayout:
                adaptive_size: True
                pos_hint: {'center_x': 0.5}
                spacing: "8dp"

                MDLabel:
                    id: user_status_lbl
                    text: "● Гравець"
                    font_style: "Subtitle2"
                    theme_text_color: "Custom"
                    text_color: 0.2, 0.8, 0.4, 1
                    adaptive_size: True

                MDLabel:
                    id: user_balance_lbl
                    text: "0 UNIT"
                    font_style: "Subtitle2"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.9, 0.75, 0.2, 1
                    adaptive_size: True

            MDCard:
                size_hint: None, None
                size: "120dp", "24dp"
                pos_hint: {'center_x': 0.5}
                md_bg_color: 0.85, 0.68, 0.13, 1
                radius: [6]
                MDLabel:
                    id: vip_tag_lbl
                    text: "ГРОМАДЯНИН"
                    font_style: "Caption"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1

            MDLabel:
                id: bank_lbl
                text: "БАНК АЗГАРДУ: 0 UNIT"
                font_style: "Caption"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.8, 0.65, 0.2, 1
                adaptive_height: True

            MDGridLayout:
                cols: 3
                spacing: "5dp"
                adaptive_height: True
                padding: [0, "6dp", 0, 0]

                GoldButton:
                    text: "МАГАЗИН"
                    icon: "store"
                    on_release: root.show_tab('shop')
                GoldButton:
                    text: "РИНОК"
                    icon: "scale-balance"
                    on_release: root.show_tab('market')
                GoldButton:
                    text: "ГРАВЦІ"
                    icon: "account-group"
                    on_release: root.show_tab('citizens')
                GoldButton:
                    text: "НАКАЗИ"
                    icon: "scroll-text"
                    on_release: root.show_tab('chat')
                GoldButton:
                    text: "ПЕРЕКАЗИ"
                    icon: "bank-transfer"
                    on_release: root.show_tab('transfer')
                GoldButton:
                    text: "КАЗИНО"
                    icon: "slot-machine"
                    on_release: root.show_tab('casino')

            MDBoxLayout:
                adaptive_size: True
                pos_hint: {'center_x': 0.5}
                spacing: "5dp"
                GoldButton:
                    text: "ЛС ЧАТ"
                    icon: "message-text"
                    on_release: root.show_tab('pm')
                GoldButton:
                    text: "ПОШТА"
                    icon: "email"
                    on_release: root.show_email_dialog()

        # --- ДИНАМІЧНА ЗОНА ---
        ScrollView:
            id: content_scroll
            MDBoxLayout:
                id: dynamic_content
                orientation: 'vertical'
                padding: "10dp"
                spacing: "8dp"
                adaptive_height: True

        # --- НИЖНЯ ПАНЕЛЬ ---
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: "110dp"
            padding: ["10dp", "4dp", "10dp", "8dp"]
            spacing: "6dp"

            MDRaisedButton:
                text: "СКАРГА НА КОРОЛЯ / ПОРУШНИКА"
                size_hint_x: 1
                md_bg_color: 0.15, 0.1, 0.1, 1
                line_color: 0.6, 0.2, 0.2, 1
                text_color: 0.9, 0.4, 0.4, 1
                on_release: root.show_complaint_dialog()

            MDBoxLayout:
                spacing: "8dp"
                size_hint_y: None
                height: "46dp"

                MDTextField:
                    id: msg_input
                    hint_text: "Написати в загальний чат..."
                    mode: "round"
                    fill_color_normal: 0.08, 0.1, 0.15, 1
                    line_color_focus: 0.85, 0.65, 0.13, 1
                    text_color_focus: 1, 1, 1, 1
                    hint_text_color_normal: 0.5, 0.5, 0.5, 1

                MDFloatingActionButton:
                    icon: "send"
                    md_bg_color: 0.85, 0.65, 0.13, 1
                    icon_color: 0, 0, 0, 1
                    user_font_size: "18sp"
                    on_release: root.send_chat_msg()
'''

class LoginScreen(MDScreen):
    def check_login_flow(self):
        username = self.ids.username_field.text.strip()
        auth_code = self.ids.code_field.text.strip()
        
        if not username:
            self.ids.error_lbl.text = "Нікнейм не може бути порожнім!"
            return
        
        try:
            res = requests.post(f"{SERVER_URL}/login", json={"username": username, "auth_code": auth_code}, timeout=4)
            data = res.json()
            if data.get("status") == "ok":
                self.ids.code_field.text = ""
                self.ids.error_lbl.text = ""
                app = MDApp.get_running_app()
                app.current_user = {
                    "username": data["username"], 
                    "role": data["role"], 
                    "balance": data["balance"], 
                    "user_id": data["user_id"],
                    "email": data.get("email", "")
                }
                self.manager.current = 'main_game'
            else:
                self.ids.error_lbl.text = data.get("message", "Помилка входу!")
        except Exception:
            self.ids.error_lbl.text = "Сервер вимкнено або недоступний!"


class MainGameScreen(MDScreen):
    active_tab = 'chat'
    dialog = None

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        self.user_data = app.current_user
        self.update_header()
        self.show_tab('chat')
        Clock.schedule_interval(self.auto_refresh, 3)

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

        u_id = self.user_data.get('user_id', '--')
        self.ids.user_status_lbl.text = f"● {username} #{u_id}"
        self.ids.user_balance_lbl.text = f"{self.user_data['balance']:.0f} UNIT"
        self.ids.bank_lbl.text = f"БАНК АЗГАРДУ: {bank_capital:.0f} UNIT"
        self.ids.vip_tag_lbl.text = f"{self.user_data['role'].upper()}"

        role = self.user_data['role']
        if role in ["Адмін", "Король"]:
            self.ids.btn_panel.opacity = 1
            self.ids.btn_panel.disabled = False
        else:
            self.ids.btn_panel.opacity = 0
            self.ids.btn_panel.disabled = True

    def auto_refresh(self, dt):
        if self.manager.current == 'main_game':
            self.update_header()
            if self.active_tab == 'chat':
                self.load_chat()

    def show_tab(self, tab_name):
        self.active_tab = tab_name
        container = self.ids.dynamic_content
        container.clear_widgets()

        if tab_name == 'chat':
            self.load_chat()
        elif tab_name == 'citizens':
            self.load_citizens()
        elif tab_name == 'shop':
            self.load_shop()
        elif tab_name == 'market':
            self.load_market()
        elif tab_name == 'transfer':
            self.load_transfer_ui()
        elif tab_name == 'casino':
            self.load_casino_ui()
        elif tab_name == 'pm':
            self.load_pm_ui()

    def load_chat(self):
        container = self.ids.dynamic_content
        container.clear_widgets()
        try:
            messages = requests.get(f"{SERVER_URL}/messages", timeout=3).json()
            for msg in messages:
                card = MDBoxLayout(
                    orientation='vertical',
                    adaptive_height=True,
                    padding="10dp",
                    spacing="4dp",
                    md_bg_color=(0.08, 0.1, 0.15, 1),
                    radius=[8]
                )
                header = MDBoxLayout(adaptive_height=True)
                sender_lbl = MDLabel(
                    text=f"{msg['sender']} [#{msg.get('sender_id', '--')}]",
                    font_style="Caption",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(0.85, 0.65, 0.13, 1),
                    adaptive_height=True
                )
                time_lbl = MDLabel(
                    text=msg.get('timestamp', ''),
                    font_style="Caption",
                    halign="right",
                    theme_text_color="Custom",
                    text_color=(0.5, 0.5, 0.5, 1),
                    adaptive_height=True
                )
                header.add_widget(sender_lbl)
                header.add_widget(time_lbl)

                text_lbl = MDLabel(
                    text=msg['text'],
                    font_style="Body2",
                    theme_text_color="Custom",
                    text_color=(0.95, 0.95, 0.95, 1),
                    adaptive_height=True
                )
                card.add_widget(header)
                card.add_widget(text_lbl)
                container.add_widget(card)
        except Exception:
            pass

    def send_chat_msg(self):
        text = self.ids.msg_input.text.strip()
        if not text:
            return
        try:
            requests.post(f"{SERVER_URL}/send_message", json={"sender": self.user_data['username'], "text": text}, timeout=3)
            self.ids.msg_input.text = ""
            if self.active_tab == 'chat':
                self.load_chat()
        except Exception:
            pass

    def load_citizens(self):
        container = self.ids.dynamic_content
        container.clear_widgets()
        try:
            users = requests.get(f"{SERVER_URL}/citizens", timeout=3).json()
            for u in users:
                card = MDBoxLayout(
                    orientation='vertical',
                    adaptive_height=True,
                    padding="10dp",
                    spacing="4dp",
                    md_bg_color=(0.08, 0.1, 0.15, 1),
                    radius=[8]
                )
                info = MDLabel(
                    text=f"ГРАВЕЦЬ: {u['username']} (ID: {u['user_id']})\nРоль: {u['role']} | Баланс: {u['balance']} UNIT",
                    font_style="Body2",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.9, 0.9, 1),
                    adaptive_height=True
                )
                card.add_widget(info)
                container.add_widget(card)
        except Exception:
            pass

    # --- ІНТЕРАКТИВНИЙ МАГАЗИН ---
    def load_shop(self):
        container = self.ids.dynamic_content
        container.clear_widgets()

        items = [
            {"id": "vip", "name": "VIP-Статус", "price": 500},
            {"id": "guard", "name": "Охорона землі", "price": 200},
            {"id": "tax", "name": "Зниження податків", "price": 1000}
        ]

        title = MDLabel(
            text="🛒 КОРОЛІВСЬКИЙ МАГАЗИН",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.85, 0.65, 0.13, 1),
            adaptive_height=True
        )
        container.add_widget(title)

        for item in items:
            box = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                padding="10dp",
                spacing="10dp",
                md_bg_color=(0.08, 0.1, 0.15, 1),
                radius=[8]
            )
            lbl = MDLabel(
                text=f"{item['name']}\nЦіна: {item['price']} UNIT",
                theme_text_color="Custom",
                text_color=(0.9, 0.9, 0.9, 1),
                adaptive_height=True
            )
            btn = MDRaisedButton(
                text="КУПИТИ",
                md_bg_color=(0.85, 0.65, 0.13, 1),
                text_color=(0, 0, 0, 1),
                on_release=lambda x, i=item: self.buy_item(i)
            )
            box.add_widget(lbl)
            box.add_widget(btn)
            container.add_widget(box)

    def buy_item(self, item):
        try:
            res = requests.post(f"{SERVER_URL}/buy_item", json={"username": self.user_data['username'], "item_id": item['id']}, timeout=3).json()
            self.update_header()
        except Exception:
            pass

    def load_market(self):
        container = self.ids.dynamic_content
        container.clear_widgets()
        lbl = MDLabel(
            text="⚖ РИНОК РЕСУРСІВ АЗГАРДУ\n\nНаразі торги закриті Королем або відсутні лоти.",
            theme_text_color="Custom",
            text_color=(0.9, 0.9, 0.9, 1),
            adaptive_height=True
        )
        container.add_widget(lbl)

    def load_transfer_ui(self):
        container = self.ids.dynamic_content
        container.clear_widgets()
        
        box = MDBoxLayout(orientation='vertical', spacing="10dp", adaptive_height=True)
        target = MDTextField(hint_text="Кому (Нікнейм)")
        amount = MDTextField(hint_text="Сума UNIT", input_filter="int")
        btn = MDRaisedButton(
            text="ПЕРЕКАЗАТИ",
            md_bg_color=(0.85, 0.65, 0.13, 1),
            text_color=(0,0,0,1),
            on_release=lambda x: self.exec_transfer(target.text, amount.text)
        )
        box.add_widget(target)
        box.add_widget(amount)
        box.add_widget(btn)
        container.add_widget(box)

    def exec_transfer(self, target, amount):
        if target and amount:
            try:
                res = requests.post(f"{SERVER_URL}/transfer", json={"sender": self.user_data['username'], "recipient": target, "amount": float(amount)}, timeout=3).json()
                self.update_header()
            except Exception:
                pass

    # --- ІНТЕРАКТИВНЕ КАЗИНО (ВВЕДЕННЯ СТАВКИ) ---
    def load_casino_ui(self):
        container = self.ids.dynamic_content
        container.clear_widgets()

        box = MDBoxLayout(orientation='vertical', spacing="12dp", adaptive_height=True)

        lbl = MDLabel(
            text="🎰 КАЗИНО АЗГАРДУ\nВведіть суму ставки та випробуйте удачу!",
            theme_text_color="Custom",
            text_color=(0.9, 0.9, 0.9, 1),
            adaptive_height=True
        )
        
        self.bet_input = MDTextField(
            hint_text="Сума ставки (UNIT)",
            mode="round",
            input_filter="int",
            fill_color_normal=(0.08, 0.1, 0.15, 1)
        )

        btn = MDRaisedButton(
            text="ЗРОБИТИ СТАВКУ ТА ЗАКРУТИТИ",
            md_bg_color=(0.85, 0.65, 0.13, 1),
            text_color=(0, 0, 0, 1),
            on_release=lambda x: self.spin_casino()
        )

        self.casino_res_lbl = MDLabel(
            text="",
            bold=True,
            adaptive_height=True
        )

        box.add_widget(lbl)
        box.add_widget(self.bet_input)
        box.add_widget(btn)
        box.add_widget(self.casino_res_lbl)
        container.add_widget(box)

    def spin_casino(self):
        val = self.bet_input.text.strip()
        if not val or int(val) <= 0:
            self.casino_res_lbl.text = "Введіть коректну ставку!"
            self.casino_res_lbl.text_color = (0.9, 0.2, 0.2, 1)
            return

        try:
            res = requests.post(f"{SERVER_URL}/casino_spin", json={"username": self.user_data['username'], "bet": int(val)}, timeout=3).json()
            if res.get("status") == "ok":
                win = res.get("win_amount", 0)
                if win > 0:
                    self.casino_res_lbl.text = f"🎉 Виграш! +{win} UNIT!"
                    self.casino_res_lbl.text_color = (0.2, 0.8, 0.4, 1)
                else:
                    self.casino_res_lbl.text = f"❌ Непощастило. -{val} UNIT"
                    self.casino_res_lbl.text_color = (0.9, 0.2, 0.2, 1)
                self.update_header()
            else:
                self.casino_res_lbl.text = res.get("message", "Помилка!")
                self.casino_res_lbl.text_color = (0.9, 0.2, 0.2, 1)
        except Exception:
            self.casino_res_lbl.text = "Помилка зв'язку з сервером!"

    # --- ІНТЕРАКТИВНІ ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС) ---
    def load_pm_ui(self):
        container = self.ids.dynamic_content
        container.clear_widgets()

        box = MDBoxLayout(orientation='vertical', spacing="10dp", adaptive_height=True)

        lbl = MDLabel(
            text="💬 ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС)",
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.85, 0.65, 0.13, 1),
            adaptive_height=True
        )

        self.pm_target = MDTextField(
            hint_text="Кому (Нікнейм отримувача)",
            mode="round",
            fill_color_normal=(0.08, 0.1, 0.15, 1)
        )

        self.pm_text = MDTextField(
            hint_text="Текст приватного повідомлення...",
            mode="round",
            fill_color_normal=(0.08, 0.1, 0.15, 1)
        )

        btn = MDRaisedButton(
            text="НАДІСЛАТИ ЛС",
            md_bg_color=(0.85, 0.65, 0.13, 1),
            text_color=(0, 0, 0, 1),
            on_release=lambda x: self.send_pm_msg()
        )

        box.add_widget(lbl)
        box.add_widget(self.pm_target)
        box.add_widget(self.pm_text)
        box.add_widget(btn)
        container.add_widget(box)

    def send_pm_msg(self):
        target = self.pm_target.text.strip()
        text = self.pm_text.text.strip()
        if target and text:
            try:
                requests.post(f"{SERVER_URL}/send_pm", json={"sender": self.user_data['username'], "recipient": target, "text": text}, timeout=3)
                self.pm_text.text = ""
            except Exception:
                pass

    def logout_act(self):
        self.manager.current = 'login'

    def show_email_dialog(self):
        field = MDTextField(hint_text="Введіть Gmail...")
        self.dialog = MDDialog(
            title="Прив'язка Пошти",
            type="custom",
            content_cls=field,
            buttons=[
                MDRaisedButton(text="Зберегти", on_release=lambda x: self.save_email(field.text))
            ]
        )
        self.dialog.open()

    def save_email(self, email):
        if email and "@" in email:
            try:
                requests.post(f"{SERVER_URL}/set_email", json={"username": self.user_data['username'], "email": email}, timeout=3)
                self.update_header()
            except Exception:
                pass
        if self.dialog:
            self.dialog.dismiss()

    def show_complaint_dialog(self):
        box = MDBoxLayout(orientation="vertical", spacing="10dp", adaptive_height=True)
        target = MDTextField(hint_text="Нікнейм порушника")
        reason = MDTextField(hint_text="Причина скарги")
        box.add_widget(target)
        box.add_widget(reason)

        self.dialog = MDDialog(
            title="Подати Скаргу",
            type="custom",
            content_cls=box,
            buttons=[
                MDRaisedButton(text="Надіслати", on_release=lambda x: self.submit_complaint(target.text, reason.text))
            ]
        )
        self.dialog.open()

    def submit_complaint(self, target, reason):
        if target and reason:
            try:
                requests.post(f"{SERVER_URL}/submit_complaint", json={"reporter": self.user_data['username'], "target": target, "reason": reason}, timeout=3)
            except Exception:
                pass
        if self.dialog:
            self.dialog.dismiss()

    def open_control_panel(self):
        pass


class AsgardApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.current_user = {}
        return Builder.load_string(KV)

if __name__ == '__main__':
    AsgardApp().run()
