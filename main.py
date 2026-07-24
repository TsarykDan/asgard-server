import random
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window

# Налаштовуємо початковий розмір вікна для зручності
Window.size = (450, 750)

KV = '''
#:import SlideTransition kivy.uix.screenmanager.SlideTransition

<MainLayout>:
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
                text: "[color=ffcc00][Гравець: test][/color] | [color=ffffff][Титул: Громадянин][/color] | [color=00ffcc][Баланс: " + str(app.balance) + " Ю][/color]"
                markup: True
                size_hint_x: None
                width: self.texture_size[0] + 20
                font_size: '13sp'

    # --- КНОПКИ ШВИДКОЇ ДІЇ ---
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
            on_release: root.change_tab("chat")

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
                    text: "Карта"
                    size_hint_x: None
                    width: '80dp'
                    background_normal: ''
                    background_color: 0.18, 0.24, 0.35, 1
                    on_release: root.change_tab("info")

    # --- МЕНЕДЖЕР ЕКРАНІВ ---
    ScreenManager:
        id: sm
        ChatScreen:
            name: "chat"
        PMScreen:
            name: "pm"
        TransfersScreen:
            name: "transfers"
        CasinoScreen:
            name: "casino"
        ShopScreen:
            name: "shop"
        AdminScreen:
            name: "admin"
        InfoScreen:
            name: "info"

# --- ЕКРАНИ ---

<ChatScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '8dp'
        spacing: '6dp'

        Label:
            text: "[color=ffcc00][БЕЗПЕКА]: Системи Азгарду працюють у нормі.[/color]"
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
                on_release: root.send_msg()

<PMScreen>:
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
            hint_text: "Отримувач (Нік / ID)..."
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
                on_release: root.send_pm()

<TransfersScreen>:
    BoxLayout:
        orientation: 'vertical'
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
            hint_text: "Отримувач..."
            size_hint_y: None
            height: '42dp'
            multiline: False

        TextInput:
            id: transfer_amount
            hint_text: "Сума (Ю)..."
            size_hint_y: None
            height: '42dp'
            multiline: False
            input_filter: 'float'

        Button:
            text: "ПЕРЕКАЗАТИ КОШТИ"
            size_hint_y: None
            height: '45dp'
            background_normal: ''
            background_color: 0.8, 0.6, 0.1, 1
            on_release: root.make_transfer()

        Label:
            id: transfer_status
            text: ""
            size_hint_y: None
            height: '30dp'
            color: 0.2, 0.8, 0.2, 1

<CasinoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '15dp'
        spacing: '10dp'

        Label:
            text: "=== КАЗИНО АЗГАРДУ ==="
            size_hint_y: None
            height: '30dp'
            color: 1, 0.8, 0, 1

        Label:
            text: "Шанси:\\n• x2 (Перемога) - 30%\\n• x0.5 (Повернення пів ставки) - 30%\\n• БАНКРУТ - 40%"
            size_hint_y: None
            height: '60dp'
            halign: 'center'

        TextInput:
            id: casino_bet
            hint_text: "Сума ставки (Ю)..."
            size_hint_y: None
            height: '42dp'
            multiline: False
            input_filter: 'float'

        Button:
            text: "🎲 КРУТИТИ КОЛЕСО 🎲"
            size_hint_y: None
            height: '45dp'
            background_normal: ''
            background_color: 0.8, 0.6, 0.1, 1
            on_release: root.play()

        Label:
            id: casino_result
            text: ""
            size_hint_y: None
            height: '40dp'
            font_size: '14sp'

<ShopScreen>:
    BoxLayout:
        orientation: 'vertical'
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
            on_release: root.buy("VIP 1", 700)

        Button:
            text: "Купити ВІП 2 (1000 Ю)"
            size_hint_y: None
            height: '42dp'
            on_release: root.buy("VIP 2", 1000)

        Label:
            id: shop_status
            text: ""
            size_hint_y: None
            height: '30dp'
            color: 0.2, 0.8, 0.2, 1

<AdminScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '12dp'
        spacing: '10dp'

        Label:
            text: "=== ПУЛЬТ АДМІНІСТРУВАННЯ ==="
            size_hint_y: None
            height: '30dp'
            color: 1, 0.2, 0.2, 1

        TextInput:
            id: admin_target
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
                on_release: root.ban()
            Button:
                text: "Розбанити"
                background_normal: ''
                background_color: 0.1, 0.6, 0.1, 1
                on_release: root.unban()

        Label:
            id: admin_status
            text: ""
            size_hint_y: None
            height: '30dp'

<InfoScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        Label:
            text: "Розділ знаходиться у розробці..."
'''

# --- ЛОГІКА ЕКРАНІВ (PYTHON) ---

class ChatScreen(Screen):
    def send_msg(self):
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

class PMScreen(Screen):
    def send_pm(self):
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

class TransfersScreen(Screen):
    def make_transfer(self):
        target = self.ids.transfer_target.text.strip()
        amount_text = self.ids.transfer_amount.text.strip()
        app = App.get_running_app()

        if target and amount_text:
            try:
                amount = float(amount_text)
                if amount <= 0:
                    self.ids.transfer_status.text = "Введіть суму більше 0!"
                    return
                if app.balance >= amount:
                    app.balance -= amount
                    self.ids.transfer_status.text = f"Переказано {amount} Ю -> {target}"
                    self.ids.transfer_target.text = ""
                    self.ids.transfer_amount.text = ""
                else:
                    self.ids.transfer_status.text = "Недостатньо коштів!"
            except ValueError:
                self.ids.transfer_status.text = "Некоректна сума!"

class CasinoScreen(Screen):
    def play(self):
        bet_text = self.ids.casino_bet.text.strip()
        app = App.get_running_app()

        if bet_text:
            try:
                bet = float(bet_text)
                if bet <= 0:
                    self.ids.casino_result.text = "Ставка має бути більше 0!"
                    return
                if app.balance < bet:
                    self.ids.casino_result.text = "Недостатньо Юнітів на балансі!"
                    return

                # Знімаємо ставку
                app.balance -= bet
                
                # Логіка рулетки
                rand = random.random()
                if rand < 0.30: # 30% виграш x2
                    win = bet * 2
                    app.balance += win
                    self.ids.casino_result.text = f"[color=00ff00]ВИГРАШ x2! (+{win} Ю)[/color]"
                elif rand < 0.60: # 30% повернення 0.5x
                    win = bet * 0.5
                    app.balance += win
                    self.ids.casino_result.text = f"[color=ffcc00]Повернення 50% (+{win} Ю)[/color]"
                else: # 40% банкрут
                    self.ids.casino_result.text = "[color=ff0000]БАНКРУТ! Ставка згоріла.[/color]"
                
                self.ids.casino_result.markup = True
                self.ids.casino_bet.text = ""

            except ValueError:
                self.ids.casino_result.text = "Введіть число!"

class ShopScreen(Screen):
    def buy(self, item_name, price):
        app = App.get_running_app()
        if app.balance >= price:
            app.balance -= price
            self.ids.shop_status.text = f"Успішно придбано {item_name}!"
        else:
            self.ids.shop_status.text = "Недостатньо коштів!"

class AdminScreen(Screen):
    def ban(self):
        user = self.ids.admin_target.text.strip()
        if user:
            self.ids.admin_status.text = f"Гравець {user} забанений!"
            self.ids.admin_target.text = ""

    def unban(self):
        user = self.ids.admin_target.text.strip()
        if user:
            self.ids.admin_status.text = f"Гравець {user} розбанений!"
            self.ids.admin_target.text = ""

class InfoScreen(Screen):
    pass

class MainLayout(BoxLayout):
    def change_tab(self, tab_name):
        self.ids.sm.current = tab_name

# --- ГОЛОВНИЙ ДОДАТОК ---

class AsgardApp(App):
    balance = 1000.0  # Початковий баланс гравця

    def build(self):
        Builder.load_string(KV)
        return MainLayout()

if __name__ == '__main__':
    AsgardApp().run()
