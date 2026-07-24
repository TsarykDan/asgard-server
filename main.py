import sys
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

KV = '''
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        # --- ВЕРХНЯ ПАНЕЛЬ: СТАТУС ГРАВЦЯ ---
        BoxLayout:
            size_hint_y: None
            height: '45dp'
            padding: ['8dp', '4dp']
            canvas.before:
                Color:
                    rgba: 0.05, 0.08, 0.15, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            ScrollView:
                do_scroll_y: False
                do_scroll_x: True
                Label:
                    id: player_info
                    text: "[color=ffcc00][Гравець: test (ID: --)][/color] | [color=ffffff][Титул: Громадянин][/color] | [color=ffcc00][Капітал: 1000000.00][/color] | [color=00ffcc][Баланс: 0.00 Ю][/color]"
                    markup: True
                    size_hint_x: None
                    width: self.texture_size[0] + 20
                    font_size: '13sp'

        # --- ВЕРХНІ КНОПКИ ДІЙ (ПОШТА, АДМІН, ВИХІД) ---
        BoxLayout:
            size_hint_y: None
            height: '38dp'
            spacing: '5dp'
            padding: ['5dp', '2dp']
            canvas.before:
                Color:
                    rgba: 0.08, 0.1, 0.15, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: "✉ Пошта"
                size_hint_x: 0.3
                background_normal: ''
                background_color: 0.1, 0.4, 0.6, 1
                font_size: '12sp'
                on_release: root.show_status("Розділ Пошта у розробці")

            Button:
                text: "Пульт Адміна"
                size_hint_x: 0.4
                background_normal: ''
                background_color: 0.8, 0.1, 0.1, 1
                font_size: '12sp'
                on_release: root.change_tab("admin")

            Button:
                text: "Вихід"
                size_hint_x: 0.3
                background_normal: ''
                background_color: 0.5, 0.1, 0.1, 1
                font_size: '12sp'
                on_release: app.stop()

        # --- ГОРИЗОНТАЛЬНЕ МЕНЮ ВКЛАДОК ---
        BoxLayout:
            size_hint_y: None
            height: '45dp'
            canvas.before:
                Color:
                    rgba: 0.1, 0.14, 0.22, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            ScrollView:
                do_scroll_y: False
                do_scroll_x: True
                bar_width: 0

                BoxLayout:
                    size_hint_x: None
                    width: self.minimum_width
                    spacing: '4dp'
                    padding: ['4dp', '4dp']

                    Button:
                        text: "Чат"
                        size_hint_x: None
                        width: '80dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("chat")
                    Button:
                        text: "Карта"
                        size_hint_x: None
                        width: '80dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("map")
                    Button:
                        text: "Політична"
                        size_hint_x: None
                        width: '95dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("politics")
                    Button:
                        text: "ЛС"
                        size_hint_x: None
                        width: '70dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("pm")
                    Button:
                        text: "Перекази"
                        size_hint_x: None
                        width: '90dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("transfers")
                    Button:
                        text: "Казино"
                        size_hint_x: None
                        width: '80dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("casino")
                    Button:
                        text: "Магазин"
                        size_hint_x: None
                        width: '90dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("shop")
                    Button:
                        text: "Ринок"
                        size_hint_x: None
                        width: '80dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("market")
                    Button:
                        text: "Громадяни"
                        size_hint_x: None
                        width: '100dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("citizens")
                    Button:
                        text: "Закони"
                        size_hint_x: None
                        width: '80dp'
                        background_normal: ''
                        background_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("laws")

        # --- ОСНОВНИЙ ЕКРАН СИСТЕМИ ---
        ScreenManager:
            id: sm

            # 1. ЧАТ
            Screen:
                name: "chat"
                BoxLayout:
                    orientation: 'vertical'
                    padding: '8dp'
                    spacing: '6dp'

                    Label:
                        text: "[color=ffcc00][БЕЗПЕКА]: Немає активних указів верхівки.[/color]"
                        markup: True
                        size_hint_y: None
                        height: '20dp'
                        font_size: '12sp'

                    ScrollView:
                        BoxLayout:
                            id: chat_logs
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: '4dp'
                            Label:
                                text: "Ласкаво просимо до загального чату Азгарду!"
                                size_hint_y: None
                                height: '25dp'
                                color: 0.6, 0.6, 0.6, 1

                    BoxLayout:
                        size_hint_y: None
                        height: '42dp'
                        spacing: '5dp'

                        TextInput:
                            id: chat_input
                            hint_text: "Повідомлення..."
                            multiline: False

                        Button:
                            text: "Надіслати"
                            size_hint_x: None
                            width: '100dp'
                            background_normal: ''
                            background_color: 0.8, 0.6, 0.1, 1
                            on_release: root.send_chat_msg()

                    Button:
                        text: "[УВАГА] Подати скаргу на порушника"
                        size_hint_y: None
                        height: '35dp'
                        background_normal: ''
                        background_color: 0.5, 0.1, 0.1, 1
                        on_release: root.show_status("Скаргу надіслано")

            # 2. ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС)
            Screen:
                name: "pm"
                BoxLayout:
                    orientation: 'vertical'
                    padding: '10dp'
                    spacing: '8dp'

                    Label:
                        text: "=== ПРИВАТНІ ПОВІДОМЛЕННЯ ==="
                        size_hint_y: None
                        height: '25dp'
                        color: 1, 0.8, 0, 1

                    TextInput:
                        id: pm_target
                        hint_text: "Нікнейм або ID..."
                        size_hint_y: None
                        height: '40dp'
                        multiline: False

                    ScrollView:
                        BoxLayout:
                            id: pm_logs
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height

                    BoxLayout:
                        size_hint_y: None
                        height: '42dp'
                        spacing: '5dp'

                        TextInput:
                            id: pm_input
                            hint_text: "Текст ЛС..."
                            multiline: False

                        Button:
                            text: "Надіслати"
                            size_hint_x: None
                            width: '100dp'
                            background_normal: ''
                            background_color: 0.8, 0.6, 0.1, 1
                            on_release: root.send_pm_msg()

            # 3. ПЕРЕКАЗИ
            Screen:
                name: "transfers"
                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: '15dp'
                        spacing: '12dp'

                        Label:
                            text: "=== ПЕРЕКАЗ ЮНІТІВ ==="
                            size_hint_y: None
                            height: '30dp'
                            color: 1, 0.8, 0, 1
                            font_size: '16sp'

                        TextInput:
                            id: transfer_target
                            hint_text: "Отримувач (Нік/ID)..."
                            size_hint_y: None
                            height: '42dp'
                            multiline: False

                        TextInput:
                            id: transfer_amount
                            hint_text: "Сума (Ю)..."
                            size_hint_y: None
                            height: '42dp'
                            multiline: False

                        Button:
                            text: "ПЕРЕКАЗАТИ КОШТИ"
                            size_hint_y: None
                            height: '45dp'
                            background_normal: ''
                            background_color: 0.8, 0.6, 0.1, 1
                            on_release: root.make_transfer()

            # 4. КАЗИНО
            Screen:
                name: "casino"
                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: '15dp'
                        spacing: '10dp'

                        Label:
                            text: "=== КАЗИНО АЗГАРДУ ==="
                            size_hint_y: None
                            height: '30dp'
                            color: 1, 0.8, 0, 1

                        Label:
                            text: "• 2x — Шанс 10%\\n• x0.5 — Шанс 20%\\n• БАНКРУТ — Шанс 70%"
                            size_hint_y: None
                            height: '60dp'

                        TextInput:
                            id: casino_bet
                            hint_text: "Сума ставки (Ю)..."
                            size_hint_y: None
                            height: '42dp'
                            multiline: False

                        Button:
                            text: "🎲 КРУТИТИ КОЛЕСО 🎲"
                            size_hint_y: None
                            height: '45dp'
                            background_normal: ''
                            background_color: 0.8, 0.6, 0.1, 1
                            on_release: root.play_casino()

            # 5. МАГАЗИН
            Screen:
                name: "shop"
                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: '12dp'
                        spacing: '10dp'

                        Label:
                            text: "=== ДЕРЖАВНИЙ МАГАЗИН ==="
                            size_hint_y: None
                            height: '30dp'
                            color: 1, 0.8, 0, 1

                        Button:
                            text: "Купити ВІП 1 (700 Ю)"
                            size_hint_y: None
                            height: '42dp'
                            on_release: root.show_status("Придбано VIP 1")

                        Button:
                            text: "Купити ВІП 2 (1000 Ю)"
                            size_hint_y: None
                            height: '42dp'
                            on_release: root.show_status("Придбано VIP 2")

                        Button:
                            text: "Дозвіл на продаж (500 Ю)"
                            size_hint_y: None
                            height: '42dp'
                            on_release: root.show_status("Отримано дозвіл")

            # 6. ПУЛЬТ АДМІНА
            Screen:
                name: "admin"
                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: '12dp'
                        spacing: '10dp'

                        Label:
                            text: "=== ПУЛЬТ АДМІНІСТРУВАННЯ ==="
                            size_hint_y: None
                            height: '30dp'
                            color: 1, 0.2, 0.2, 1

                        TextInput:
                            hint_text: "Нік або ID гравця..."
                            size_hint_y: None
                            height: '42dp'

                        BoxLayout:
                            size_hint_y: None
                            height: '42dp'
                            spacing: '5dp'
                            Button:
                                text: "Забанити"
                                background_normal: ''
                                background_color: 0.8, 0.1, 0.1, 1
                                on_release: root.show_status("Гравця забанено")
                            Button:
                                text: "Розбанити"
                                background_normal: ''
                                background_color: 0.1, 0.6, 0.1, 1
                                on_release: root.show_status("Гравця розбанено")

                        Button:
                            text: "Закрити пульт"
                            size_hint_y: None
                            height: '40dp'
                            background_normal: ''
                            background_color: 0.3, 0.3, 0.3, 1
                            on_release: root.change_tab("chat")

            # Інші вкладки
            Screen:
                name: "map"
                Label:
                    text: "Карта Азгарду завантажується..."
            Screen:
                name: "politics"
                Label:
                    text: "Політична система у розробці."
            Screen:
                name: "market"
                Label:
                    text: "Вільний ринок порожній."
            Screen:
                name: "citizens"
                Label:
                    text: "Список громадян Азгарду..."
            Screen:
                name: "laws"
                Label:
                    text: "Конституція та закони Азгарду."
'''

class MainScreen(Screen):
    def change_tab(self, tab_name):
        self.ids.sm.current = tab_name

    def show_status(self, text):
        print(f"[STATUS]: {text}")

    def send_chat_msg(self):
        msg = self.ids.chat_input.text.strip()
        if msg:
            lbl = Label(
                text=f"[color=00ffcc]Ви:[/color] {msg}",
                markup=True,
                size_hint_y=None,
                height='25dp',
                halign='left',
                text_size=(Window.width - 30, None)
            )
            self.ids.chat_logs.add_widget(lbl)
            self.ids.chat_input.text = ""

    def send_pm_msg(self):
        target = self.ids.pm_target.text.strip()
        msg = self.ids.pm_input.text.strip()
        if target and msg:
            lbl = Label(
                text=f"[color=ffcc00]До {target}:[/color] {msg}",
                markup=True,
                size_hint_y=None,
                height='25dp',
                halign='left',
                text_size=(Window.width - 30, None)
            )
            self.ids.pm_logs.add_widget(lbl)
            self.ids.pm_input.text = ""

    def make_transfer(self):
        target = self.ids.transfer_target.text.strip()
        amount = self.ids.transfer_amount.text.strip()
        if target and amount:
            print(f"[TRANSFER]: {amount} Ю -> {target}")
            self.ids.transfer_target.text = ""
            self.ids.transfer_amount.text = ""

    def play_casino(self):
        bet = self.ids.casino_bet.text.strip()
        if bet:
            print(f"[CASINO]: Ставка {bet} Ю прийнята!")
            self.ids.casino_bet.text = ""

class AsgardApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    AsgardApp().run()
