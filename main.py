import os
import sys
import requests

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFillRoundFlatIconButton, MDIconButton, MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView

SERVER_URL = "https://asgard-server-xu8n.onrender.com"

KV = '''
<NavBtn@MDRaisedButton>:
    md_bg_color: 0.1, 0.14, 0.22, 1
    text_color: 0.9, 0.8, 0.4, 1
    font_style: "Caption"
    size_hint_x: 0.32
    height: "36dp"
    elevation: 1

MDScreenManager:
    LoginScreen:
        name: 'login'
    MainGameScreen:
        name: 'main_game'

<LoginScreen>:
    md_bg_color: 0.04, 0.06, 0.1, 1
    MDBoxLayout:
        orientation: 'vertical'
        padding: "24dp"
        spacing: "12dp"
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        adaptive_height: True

        MDLabel:
            text: "А З Г А Р Д"
            font_style: "H4"
            bold: True
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.95, 0.75, 0.2, 1

        MDTextField:
            id: username_field
            hint_text: "Введіть свій нікнейм..."
            mode: "round"
            fill_color_normal: 0.08, 0.11, 0.18, 1
            text_color_focus: 1, 1, 1, 1

        MDTextField:
            id: code_field
            hint_text: "Код Короля / Адміна (якщо є)..."
            password: True
            mode: "round"
            fill_color_normal: 0.08, 0.11, 0.18, 1
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
    md_bg_color: 0.04, 0.06, 0.1, 1

    MDBoxLayout:
        orientation: 'vertical'

        # --- ВЕРХНЯ ШАПКА ТА СТАТУС ---
        MDCard:
            orientation: 'vertical'
            size_hint_y: None
            adaptive_height: True
            padding: ["10dp", "6dp", "10dp", "8dp"]
            spacing: "4dp"
            md_bg_color: 0.07, 0.09, 0.15, 1
            radius: [0, 0, 12, 12]

            MDBoxLayout:
                size_hint_y: None
                height: "32dp"
                MDIconButton:
                    icon: "logout"
                    theme_text_color: "Custom"
                    text_color: 0.6, 0.6, 0.6, 1
                    user_font_size: "18sp"
                    on_release: root.logout_act()

                MDLabel:
                    id: header_status_lbl
                    text: "[Гравець: --] | [Титул: --]"
                    font_style: "Caption"
                    bold: True
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0.9, 0.75, 0.2, 1

                MDRaisedButton:
                    id: btn_admin_panel
                    text: "Пульт Адміна"
                    md_bg_color: 0.7, 0.1, 0.1, 1
                    text_color: 1, 1, 1, 1
                    font_style: "Caption"
                    size_hint: None, None
                    size: "95dp", "28dp"
                    opacity: 0
                    disabled: True
                    on_release: root.open_admin_panel()

                MDRaisedButton:
                    text: "✉ Пошта"
                    md_bg_color: 0.12, 0.4, 0.6, 1
                    text_color: 1, 1, 1, 1
                    font_style: "Caption"
                    size_hint: None, None
                    size: "75dp", "28dp"
                    on_release: root.show_email_dialog()

            MDLabel:
                id: bank_and_balance_lbl
                text: "[Капітал Банку: 0.00 юнітів] | [Баланс: 0.00 юнітів]"
                font_style: "Caption"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.95, 0.8, 0.2, 1
                adaptive_height: True

            # --- МЕНЮ НАВІГАЦІЇ (2 РЯДИ КНОПОК ДЛЯ СМАРТФОНА) ---
            MDGridLayout:
                cols: 5
                spacing: "4dp"
                adaptive_height: True
                padding: [0, "4dp", 0, 0]

                NavBtn:
                    text: "Чат"
                    on_release: root.show_tab('chat')
                NavBtn:
                    text: "Карта"
                    on_release: root.show_tab('map')
                NavBtn:
                    text: "Політична"
                    on_release: root.show_tab('politics')
                NavBtn:
                    text: "ЛС"
                    on_release: root.show_tab('pm')
                NavBtn:
                    text: "Перекази"
                    on_release: root.show_tab('transfer')
                NavBtn:
                    text: "Казино"
                    on_release: root.show_tab('casino')
                NavBtn:
                    text: "Магазин"
                    on_release: root.show_tab('shop')
                NavBtn:
                    text: "Ринок"
                    on_release: root.show_tab('market')
                NavBtn:
                    text: "Громадяни"
                    on_release: root.show_tab('citizens')
                NavBtn:
                    text: "Закони"
                    on_release: root.show_tab('laws')

        # --- ОСНОВНА ДИНАМІЧНА ЗОНА З ПРОКРУТКОЮ ---
        ScrollView:
            id: content_scroll
            do_scroll_x: False
            MDBoxLayout:
                id: dynamic_content
                orientation: 'vertical'
                padding: "10dp"
                spacing: "10dp"
                adaptive_height: True

        # --- НИЖНІЙ БЛОК (СКАРГА ТА ПОЛЕ ВВОДУ ЧАТУ) ---
        MDBoxLayout:
            id: bottom_panel
            orientation: 'vertical'
            size_hint_y: None
            adaptive_height: True
            padding: ["8dp", "4dp", "8dp", "6dp"]
            spacing: "6dp"

            MDRaisedButton:
                text: "[УВАГА] Подати скаргу на порушника закону"
                size_hint_x: 1
                height: "32dp"
                md_bg_color: 0.5, 0.12, 0.12, 1
                text_color: 1, 0.9, 0.9, 1
                font_style: "Caption"
                on_release: root.show_complaint_dialog()

            MDBoxLayout:
                id: chat_input_box
                spacing: "6dp"
                size_hint_y: None
                height: "42dp"

                MDTextField:
                    id: msg_input
                    hint_text: "Напишіть повідомлення в бесіду..."
                    mode: "round"
                    fill_color_normal: 0.08, 0.1, 0.16, 1
                    text_color_focus: 1, 1, 1, 1
                    font_size: "14sp"

                MDRaisedButton:
                    text: "Надіслати"
                    md_bg_color: 0.8, 0.6, 0.1, 1
                    text_color: 0, 0, 0, 1
                    font_style: "Button"
                    on_release: root.send_chat_msg()
'''

class LoginScreen(MDScreen):
    def check_login_flow(self):
        username = self.ids.username_field.text.strip()
        auth_code = self.ids.code_field.text.strip()
        
        if not username:
            self.ids.error_lbl.text = "Введіть нікнейм!"
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
            self.ids.error_lbl.text = "Сервер недоступний!"


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
            bank_capital = res.get('bank_capital', 0.0)
        except Exception:
            bank_capital = 0.0

        u_id = self.user_data.get('user_id', '--')
        role = self.user_data.get('role', 'Громадянин')
        bal = self.user_data.get('balance', 0.0)

        self.ids.header_status_lbl.text = f"[Гравець: {username} (ID: {u_id})] | [Титул: {role}]"
        self.ids.bank_and_balance_lbl.text = f"[Капітал Банку: {bank_capital:.2f}] | [Баланс: {bal:.2f} юнітів]"

        if role in ["Адмін", "Король"]:
            self.ids.btn_admin_panel.opacity = 1
            self.ids.btn_admin_panel.disabled = False
        else:
            self.ids.btn_admin_panel.opacity = 0
            self.ids.btn_admin_panel.disabled = True

    def auto_refresh(self, dt):
        if self.manager.current == 'main_game':
            self.update_header()
            if self.active_tab == 'chat':
                self.load_chat()

    def show_tab(self, tab_name):
        self.active_tab = tab_name
        container = self.ids.dynamic_content
        container.clear_widgets()

        # Приховуємо або показуємо нижню панель вводу чату залежно від вкладинки
        if tab_name == 'chat':
            self.ids.chat_input_box.height = "42dp"
            self.ids.chat_input_box.opacity = 1
            self.load_chat()
        else:
            self.ids.chat_input_box.height = "0dp"
            self.ids.chat_input_box.opacity = 0

        if tab_name == 'map':
            self.load_simple_info("🗺 КАРТА КОРОЛІВСТВА", "Карта території Азгарду знаходить під охороною. Розширюйте володіння!")
        elif tab_name == 'politics':
            self.load_simple_info("👑 ПОЛІТИЧНИЙ УСТРІЙ", "Азгард — абсолютна монархія. Всі укази Короля є обов'язковими до виконання.")
        elif tab_name == 'pm':
            self.load_pm_ui()
        elif tab_name == 'transfer':
            self.load_transfer_ui()
        elif tab_name == 'casino':
            self.load_casino_ui()
        elif tab_name == 'shop':
            self.load_shop_ui()
        elif tab_name == 'market':
            self.load_simple_info("⚖ РИНОК РЕСУРСІВ", "На даний момент ринок очікує нових торгівців.")
        elif tab_name == 'citizens':
            self.load_citizens()
        elif tab_name == 'laws':
            self.load_simple_info("📜 ЗАКОНИ АЗГАРДУ", "1. Шануйте Короля.\n2. Сплачуйте податки.\n3. Не порушуйте порядок у чаті.")

    def load_simple_info(self, title, text):
        container = self.ids.dynamic_content
        card = MDCard(orientation='vertical', padding="14dp", adaptive_height=True, md_bg_color=(0.08, 0.1, 0.16, 1))
        t_lbl = MDLabel(text=title, font_style="Subtitle1", bold=True, theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1), adaptive_height=True)
        b_lbl = MDLabel(text=text, font_style="Body2", theme_text_color="Custom", text_color=(0.9, 0.9, 0.9, 1), adaptive_height=True)
        card.add_widget(t_lbl)
        card.add_widget(b_lbl)
        container.add_widget(card)

    def load_chat(self):
        container = self.ids.dynamic_content
        container.clear_widgets()
        try:
            messages = requests.get(f"{SERVER_URL}/messages", timeout=3).json()
            for msg in messages:
                card = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="8dp", spacing="2dp", md_bg_color=(0.07, 0.09, 0.15, 1), radius=[6])
                header = MDLabel(text=f"{msg['sender']} [#{msg.get('sender_id', '--')}]:", font_style="Caption", bold=True, theme_text_color="Custom", text_color=(0.85, 0.65, 0.13, 1), adaptive_height=True)
                body = MDLabel(text=msg['text'], font_style="Body2", theme_text_color="Custom", text_color=(1, 1, 1, 1), adaptive_height=True)
                card.add_widget(header)
                card.add_widget(body)
                container.add_widget(card)
        except Exception:
            pass

    def send_chat_msg(self):
        text = self.ids.msg_input.text.strip()
        if text:
            try:
                requests.post(f"{SERVER_URL}/send_message", json={"sender": self.user_data['username'], "text": text}, timeout=3)
                self.ids.msg_input.text = ""
                self.load_chat()
            except Exception:
                pass

    def load_pm_ui(self):
        container = self.ids.dynamic_content
        container.clear_widgets()

        title = MDLabel(text="=== ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС) ===", halign="center", font_style="Subtitle2", theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1), adaptive_height=True)
        
        self.pm_target = MDTextField(hint_text="Введіть нікнейм або ID отримувача...", mode="round", fill_color_normal=(0.08, 0.1, 0.16, 1))
        self.pm_text = MDTextField(hint_text="Текст приватного повідомлення...", mode="round", fill_color_normal=(0.08, 0.1, 0.16, 1))
        
        btn = MDRaisedButton(text="Надіслати ЛС", size_hint_x: 1, md_bg_color=(0.8, 0.6, 0.1, 1), text_color=(0,0,0,1), on_release=lambda x: self.send_pm())

        container.add_widget(title)
        container.add_widget(self.pm_target)
        container.add_widget(self.pm_text)
        container.add_widget(btn)

    def send_pm(self):
        target = self.pm_target.text.strip()
        text = self.pm_text.text.strip()
        if target and text:
            try:
                requests.post(f"{SERVER_URL}/send_pm", json={"sender": self.user_data['username'], "recipient": target, "text": text}, timeout=3)
                self.pm_text.text = ""
            except Exception:
                pass

    def load_transfer_ui(self):
        container = self.ids.dynamic_content
        container.clear_widgets()

        title = MDLabel(text="=== КІБЕР-БАНКІНГ: ПЕРЕКАЗ ЮНІТІВ ===", halign="center", font_style="Subtitle2", theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1), adaptive_height=True)
        
        self.tr_target = MDTextField(hint_text="Нікнейм або ID отримувача...", mode="round", fill_color_normal=(0.08, 0.1, 0.16, 1))
        self.tr_amount = MDTextField(hint_text="Сума переказу (Ю)...", input_filter="int", mode="round", fill_color_normal=(0.08, 0.1, 0.16, 1))
        
        btn = MDRaisedButton(text="⟪ ПЕРЕКАЗАТИ КОШТИ ⟫", size_hint_x: 1, height="45dp", md_bg_color=(0.8, 0.6, 0.1, 1), text_color=(0,0,0,1), on_release=lambda x: self.exec_transfer())
        sub = MDLabel(text="Миттєвий переказ грошей підданим Азгарду.", halign="center", font_style="Caption", theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), adaptive_height=True)

        container.add_widget(title)
        container.add_widget(self.tr_target)
        container.add_widget(self.tr_amount)
        container.add_widget(btn)
        container.add_widget(sub)

    def exec_transfer(self):
        target = self.tr_target.text.strip()
        amount = self.tr_amount.text.strip()
        if target and amount:
            try:
                requests.post(f"{SERVER_URL}/transfer", json={"sender": self.user_data['username'], "recipient": target, "amount": float(amount)}, timeout=3)
                self.tr_amount.text = ""
                self.update_header()
            except Exception:
                pass

    def load_casino_ui(self):
        container = self.ids.dynamic_content
        container.clear_widgets()

        title = MDLabel(text="=== КАЗИНО АЗГАРДУ: КОЛЕСО ФОРТУНИ ===", halign="center", font_style="Subtitle2", theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1), adaptive_height=True)
        info = MDLabel(
            text="СЕКТОРЫ КОЛЕСА:\n🎲 2x (Подвоєння) — Шанс 10%\n🎲 x0.5 (Повернення 50%) — Шанс 20%\n🎲 4x БАНКРУТ (Втрата всієї ставки) — Шанс 70%",
            halign="center", font_style="Caption", theme_text_color="Custom", text_color=(0.8, 0.8, 0.8, 1), adaptive_height=True
        )

        self.bet_input = MDTextField(hint_text="Введіть суму ставки (Ю)...", input_filter="int", mode="round", fill_color_normal=(0.08, 0.1, 0.16, 1))
        btn = MDRaisedButton(text="⟪ КРУТИТИ КОЛЕСО ⟫", size_hint_x: 1, height="45dp", md_bg_color=(0.8, 0.6, 0.1, 1), text_color=(0,0,0,1), on_release=lambda x: self.spin_casino())
        
        self.casino_res = MDLabel(text="Зробіть ставку та випробуйте свою удачу!", halign="center", font_style="Caption", theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1), adaptive_height=True)

        container.add_widget(title)
        container.add_widget(info)
        container.add_widget(self.bet_input)
        container.add_widget(btn)
        container.add_widget(self.casino_res)

    def spin_casino(self):
        val = self.bet_input.text.strip()
        if val and int(val) > 0:
            try:
                res = requests.post(f"{SERVER_URL}/casino_spin", json={"username": self.user_data['username'], "bet": int(val)}, timeout=3).json()
                win = res.get("win_amount", 0)
                if win > 0:
                    self.casino_res.text = f"🎉 Виграш: +{win} Ю!"
                    self.casino_res.text_color = (0.2, 0.8, 0.4, 1)
                else:
                    self.casino_res.text = f"❌ Ви програли {-win if win < 0 else val} Ю!"
                    self.casino_res.text_color = (0.9, 0.2, 0.2, 1)
                self.update_header()
            except Exception:
                pass

    def load_shop_ui(self):
        container = self.ids.dynamic_content
        container.clear_widgets()

        title = MDLabel(text="=== ДЕРЖАВНИЙ МАГАЗИН АЗГАРДУ ===", halign="center", font_style="Subtitle2", theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1), adaptive_height=True)
        container.add_widget(title)

        vips = [
            ("Віпка (Рівень 1)", "700 Ю"),
            ("Віпка 2 (Рівень 2)", "1000 Ю"),
            ("Віпка 3 (Рівень 3)", "2000 Ю"),
            ("Віпка 4 (Рівень 4)", "Безцінно")
        ]
        
        for name, price in vips:
            box = MDBoxLayout(adaptive_height=True, spacing="8dp")
            lbl = MDLabel(text=f"{name}\nЦіна: {price}", font_style="Caption", theme_text_color="Custom", text_color=(0.9,0.9,0.9,1))
            btn = MDRaisedButton(text="Купити", md_bg_color=(0.8, 0.6, 0.1, 1), text_color=(0,0,0,1), size_hint_x=0.35)
            box.add_widget(lbl)
            box.add_widget(btn)
            container.add_widget(box)

    def load_citizens(self):
        container = self.ids.dynamic_content
        container.clear_widgets()
        try:
            users = requests.get(f"{SERVER_URL}/citizens", timeout=3).json()
            for u in users:
                card = MDCard(orientation='vertical', padding="8dp", adaptive_height=True, md_bg_color=(0.07, 0.09, 0.15, 1))
                lbl = MDLabel(text=f"👤 {u['username']} (ID: {u['user_id']})\nРоль: {u['role']} | Баланс: {u['balance']} Ю", font_style="Caption", theme_text_color="Custom", text_color=(0.9, 0.9, 0.9, 1))
                card.add_widget(lbl)
                container.add_widget(card)
        except Exception:
            pass

    # --- ПУЛЬТ АДМІНА / КОРОЛЯ (ІНТЕРФЕЙС ЗІ СКРІНШОТА) ---
    def open_admin_panel(self):
        box = MDBoxLayout(orientation="vertical", spacing="8dp", adaptive_height=True)
        
        # 1. Дисциплінарний Комітет
        lbl1 = MDLabel(text="Дисциплінарний Комітет (Бан/Розбан):", font_style="Caption", bold=True, theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1))
        f_ban = MDTextField(hint_text="Нік або ID...", mode="round")
        btn_ban = MDRaisedButton(text="Забанити", md_bg_color=(0.8, 0.2, 0.2, 1))
        btn_unban = MDRaisedButton(text="Розбанити", md_bg_color=(0.2, 0.6, 0.2, 1))
        b_box1 = MDBoxLayout(spacing="4dp", adaptive_height=True)
        b_box1.add_widget(btn_ban)
        b_box1.add_widget(btn_unban)

        # 2. Казначея
        lbl2 = MDLabel(text="Державна Казначея (Юніти):", font_style="Caption", bold=True, theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1))
        f_target = MDTextField(hint_text="Нік або ID...", mode="round")
        f_sum = MDTextField(hint_text="Сума...", mode="round", input_filter="int")
        
        # 3. Капітал Банку
        lbl3 = MDLabel(text="Капітал Банку:", font_style="Caption", bold=True, theme_text_color="Custom", text_color=(0.9, 0.75, 0.2, 1))
        f_bank = MDTextField(hint_text="Сума Капіталу...", mode="round")
        btn_bank = MDRaisedButton(text="Встановити Капітал", md_bg_color=(0.8, 0.6, 0.1, 1), text_color=(0,0,0,1))

        box.add_widget(lbl1)
        box.add_widget(f_ban)
        box.add_widget(b_box1)
        box.add_widget(lbl2)
        box.add_widget(f_target)
        box.add_widget(f_sum)
        box.add_widget(lbl3)
        box.add_widget(f_bank)
        box.add_widget(btn_bank)

        self.dialog = MDDialog(
            title="👑 ПУЛЬТ АБСОЛЮТНОГО АДМІНІСТРУВАННЯ",
            type="custom",
            content_cls=box,
            buttons=[
                MDRaisedButton(text="Закрити пульт керування", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def logout_act(self):
        self.manager.current = 'login'

    def show_email_dialog(self):
        field = MDTextField(hint_text="Введіть Gmail...", mode="round")
        self.dialog = MDDialog(
            title="Прив'язка Пошти",
            type="custom",
            content_cls=field,
            buttons=[
                MDRaisedButton(text="Зберегти", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def show_complaint_dialog(self):
        box = MDBoxLayout(orientation="vertical", spacing="8dp", adaptive_height=True)
        target = MDTextField(hint_text="Нікнейм порушника", mode="round")
        reason = MDTextField(hint_text="Причина скарги", mode="round")
        box.add_widget(target)
        box.add_widget(reason)

        self.dialog = MDDialog(
            title="Подати Скаргу",
            type="custom",
            content_cls=box,
            buttons=[
                MDRaisedButton(text="Надіслати", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()


class AsgardApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.current_user = {}
        return Builder.load_string(KV)

if __name__ == '__main__':
    AsgardApp().run()
