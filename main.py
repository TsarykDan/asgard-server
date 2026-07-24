import sys
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toast import toast

# Адаптація розміру під мобільний екран при тестуванні на ПК
# Window.size = (360, 740)

KV = '''
<MainScreen>:
    md_bg_color: 0.05, 0.07, 0.12, 1

    BoxLayout:
        orientation: 'vertical'

        # --- ВЕРХНЯ ПАНЕЛЬ: ІНФОРМАЦІЯ ПРО ГРАВЦЯ ---
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            md_bg_color: 0.02, 0.03, 0.06, 1
            padding: ["8dp", "4dp"]
            spacing: "5dp"

            ScrollView:
                do_scroll_y: False
                do_scroll_x: True
                MDBoxLayout:
                    adaptive_width: True
                    spacing: "10dp"
                    alignment: "center"
                    
                    MDLabel:
                        id: player_info
                        text: "[color=ffcc00][Гравець: test (ID: --)][/color] | [color=ffffff][Титул: Громадянин][/color] | [color=ffcc00][Капітал: 1000000.00][/color] | [color=00ffcc][Баланс: 0.00 юнітів][/color]"
                        markup: True
                        font_style: "Caption"
                        adaptive_width: True

        # --- ВЕРХНІ КНОПКИ ДІЙ (ПОШТА, АДМІН, ВИХІД) ---
        MDBoxLayout:
            size_hint_y: None
            height: "40dp"
            md_bg_color: 0.08, 0.1, 0.15, 1
            padding: ["5dp", "2dp"]
            spacing: "5dp"

            MDRaisedButton:
                text: "✉ Пошта"
                md_bg_color: 0.1, 0.4, 0.6, 1
                font_size: "11sp"
                on_release: app.show_toast("Розділ Пошта у розробці")

            MDRaisedButton:
                id: btn_admin
                text: "Пульт Адміна"
                md_bg_color: 0.8, 0.1, 0.1, 1
                font_size: "11sp"
                on_release: root.change_tab("admin")

            Widget:

            MDRaisedButton:
                text: "Вихід"
                md_bg_color: 0.7, 0.1, 0.1, 1
                font_size: "11sp"
                on_release: app.stop()

        # --- ГОРИЗОНТАЛЬНЕ МЕНЮ ВКЛАДОК (НАВІГАЦІЯ) ---
        MDBoxLayout:
            size_hint_y: None
            height: "45dp"
            md_bg_color: 0.1, 0.14, 0.22, 1

            ScrollView:
                do_scroll_y: False
                do_scroll_x: True
                bar_width: 0

                MDBoxLayout:
                    adaptive_width: True
                    spacing: "2dp"
                    padding: ["2dp", "2dp"]

                    MDRaisedButton:
                        text: "Чат"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("chat")
                    MDRaisedButton:
                        text: "Карта"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("map")
                    MDRaisedButton:
                        text: "Політична"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("politics")
                    MDRaisedButton:
                        text: "ЛС"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("pm")
                    MDRaisedButton:
                        text: "Перекази"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("transfers")
                    MDRaisedButton:
                        text: "Казино"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("casino")
                    MDRaisedButton:
                        text: "Магазин"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("shop")
                    MDRaisedButton:
                        text: "Ринок"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("market")
                    MDRaisedButton:
                        text: "Громадяни"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("citizens")
                    MDRaisedButton:
                        text: "Закони"
                        md_bg_color: 0.18, 0.24, 0.35, 1
                        on_release: root.change_tab("laws")

        # --- ОСНОВНИЙ КОНТЕНТ (SCREEN MANAGER) ---
        ScreenManager:
            id: sm

            # 1. ЧАТ
            MDScreen:
                name: "chat"
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: "8dp"
                    spacing: "8dp"

                    MDLabel:
                        text: "[БЕЗПЕКА]: Немає активних указів верхівки."
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 0.8, 0, 1
                        font_style: "Caption"
                        size_hint_y: None
                        height: "20dp"

                    ScrollView:
                        MDBoxLayout:
                            id: chat_logs
                            orientation: 'vertical'
                            adaptive_height: True
                            spacing: "5dp"
                            MDLabel:
                                text: "Ласкаво просимо до загального чату Азгарду!"
                                theme_text_color: "Hint"
                                font_style: "Body2"

                    MDBoxLayout:
                        size_hint_y: None
                        height: "50dp"
                        spacing: "5dp"

                        MDTextField:
                            id: chat_input
                            hint_text: "Напишіть повідомлення в бесіду..."
                            mode: "fill"
                            fill_color: 0.12, 0.16, 0.24, 1

                        MDRaisedButton:
                            text: "Надіслати"
                            md_bg_color: 0.8, 0.6, 0.1, 1
                            on_release: root.send_chat_msg()

                    MDRaisedButton:
                        text: "[УВАГА] Подати скаргу на порушника закону"
                        md_bg_color: 0.5, 0.1, 0.1, 1
                        size_hint_x: 1
                        size_hint_y: None
                        height: "40dp"
                        on_release: app.show_toast("Скаргу надіслано модерації")

            # 2. ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС)
            MDScreen:
                name: "pm"
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: "10dp"
                    spacing: "10dp"

                    MDLabel:
                        text: "=== ПРИВАТНІ ПОВІДОМЛЕННЯ (ЛС) ==="
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 0.8, 0, 1
                        font_style: "Subtitle1"
                        size_hint_y: None
                        height: "30dp"

                    MDTextField:
                        id: pm_target
                        hint_text: "Уведіть нікнейм або ID отримувача..."
                        mode: "rectangle"

                    ScrollView:
                        MDBoxLayout:
                            id: pm_logs
                            orientation: 'vertical'
                            adaptive_height: True

                    MDBoxLayout:
                        size_hint_y: None
                        height: "50dp"
                        spacing: "5dp"

                        MDTextField:
                            id: pm_input
                            hint_text: "Текст приватного повідомлення..."
                            mode: "fill"

                        MDRaisedButton:
                            text: "Надіслати ЛС"
                            md_bg_color: 0.8, 0.6, 0.1, 1
                            on_release: root.send_pm_msg()

            # 3. ПЕРЕКАЗИ (КІБЕР-БАНКІНГ)
            MDScreen:
                name: "transfers"
                ScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        adaptive_height: True
                        padding: "15dp"
                        spacing: "15dp"

                        MDLabel:
                            text: "=== КІБЕР-БАНКІНГ: ПЕРЕКАЗ ЮНІТІВ ==="
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1
                            font_style: "H6"

                        MDTextField:
                            id: transfer_target
                            hint_text: "Нікнейм або ID отримувача..."
                            mode: "rectangle"

                        MDTextField:
                            id: transfer_amount
                            hint_text: "Сума переказу (Ю)..."
                            input_filter: "float"
                            mode: "rectangle"

                        MDRaisedButton:
                            text: "🖩 ПЕРЕКАЗАТИ КОШТИ 🖩"
                            size_hint_x: 1
                            height: "50dp"
                            md_bg_color: 0.8, 0.6, 0.1, 1
                            on_release: root.make_transfer()

                        MDLabel:
                            text: "Миттєвий переказ грошей підданим Азгарду."
                            halign: "center"
                            theme_text_color: "Hint"

            # 4. КАЗИНО
            MDScreen:
                name: "casino"
                ScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        adaptive_height: True
                        padding: "15dp"
                        spacing: "12dp"

                        MDLabel:
                            text: "=== КАЗИНО АЗГАРДУ: КОЛЕСО ФОРТУНИ ==="
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1
                            font_style: "Subtitle1"

                        MDLabel:
                            text: "СЕКТОРИ КОЛЕСА:\\n• 2x (Подвоєння) — Шанс 10%\\n• x0.5 (Повернення 50%) — Шанс 20%\\n• 4x БАНКРУТ (Втрата) — Шанс 70%"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0.8, 0.8, 0.8, 1

                        MDTextField:
                            id: casino_bet
                            hint_text: "Введіть суму ставки (Ю)..."
                            input_filter: "float"
                            mode: "rectangle"

                        MDRaisedButton:
                            text: "🎲 КРУТИТИ КОЛЕСО 🎲"
                            size_hint_x: 1
                            height: "50dp"
                            md_bg_color: 0.8, 0.6, 0.1, 1
                            on_release: root.play_casino()

            # 5. ДЕРЖАВНИЙ МАГАЗИН
            MDScreen:
                name: "shop"
                ScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        adaptive_height: True
                        padding: "10dp"
                        spacing: "10dp"

                        MDLabel:
                            text: "=== ДЕРЖАВНИЙ МАГАЗИН АЗГАРДУ ==="
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1
                            font_style: "H6"

                        MDLabel:
                            text: "--- ВІП СТАТУСИ ---"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1

                        # Елементи магазину
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "10dp"
                            MDBoxLayout:
                                orientation: 'vertical'
                                MDLabel:
                                    text: "Вiпка (Рiвень 1)"
                                    bold: True
                                MDLabel:
                                    text: "+10% до зарплати"
                                    font_style: "Caption"
                            MDLabel:
                                text: "700 Ю"
                                adaptive_width: True
                            MDRaisedButton:
                                text: "Купити"
                                md_bg_color: 0.8, 0.6, 0.1, 1
                                on_release: app.show_toast("Придбано VIP 1")

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "10dp"
                            MDBoxLayout:
                                orientation: 'vertical'
                                MDLabel:
                                    text: "Вiпка 2 (Рiвень 2)"
                                    bold: True
                                MDLabel:
                                    text: "+20% до зарплати"
                                    font_style: "Caption"
                            MDLabel:
                                text: "1000 Ю"
                                adaptive_width: True
                            MDRaisedButton:
                                text: "Купити"
                                md_bg_color: 0.8, 0.6, 0.1, 1
                                on_release: app.show_toast("Придбано VIP 2")

                        MDLabel:
                            text: "--- ДЕРЖАВНІ ДОЗВОЛИ ---"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "10dp"
                            MDLabel:
                                text: "Дозвiл на продаж"
                            MDLabel:
                                text: "500 Ю"
                                adaptive_width: True
                            MDRaisedButton:
                                text: "Придбати"
                                md_bg_color: 0.8, 0.6, 0.1, 1
                                on_release: app.show_toast("Отримано дозвіл на продаж")

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "10dp"
                            MDLabel:
                                text: "Дозвiл на зброю"
                            MDLabel:
                                text: "250 Ю"
                                adaptive_width: True
                            MDRaisedButton:
                                text: "Придбати"
                                md_bg_color: 0.8, 0.6, 0.1, 1
                                on_release: app.show_toast("Отримано дозвіл на зброю")

            # 6. ПУЛЬТ АДМІНА
            MDScreen:
                name: "admin"
                ScrollView:
                    MDBoxLayout:
                        orientation: 'vertical'
                        adaptive_height: True
                        padding: "10dp"
                        spacing: "10dp"

                        MDLabel:
                            text: "=== ПУЛЬТ АБСОЛЮТНОГО АДМІНІСТРУВАННЯ ==="
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 0.2, 0.2, 1
                            font_style: "Subtitle1"

                        # Дисциплінарний комітет
                        MDLabel:
                            text: "Дисциплiнарний Комiтет (Бан/Розбан):"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1
                        MDTextField:
                            id: admin_target_ban
                            hint_text: "Нiк або ID..."
                            mode: "rectangle"
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "5dp"
                            MDRaisedButton:
                                text: "Забанити"
                                md_bg_color: 0.8, 0.1, 0.1, 1
                                size_hint_x: 0.5
                                on_release: app.show_toast("Гравця забанено")
                            MDRaisedButton:
                                text: "Розбанити"
                                md_bg_color: 0.1, 0.6, 0.1, 1
                                size_hint_x: 0.5
                                on_release: app.show_toast("Гравця розбанено")

                        # Казначея
                        MDLabel:
                            text: "Державна Казначея (Юнiти):"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1
                        MDTextField:
                            id: admin_target_money
                            hint_text: "Нiк або ID..."
                            mode: "rectangle"
                        MDTextField:
                            id: admin_amount_money
                            hint_text: "Сума..."
                            input_filter: "float"
                            mode: "rectangle"
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: "5dp"
                            MDRaisedButton:
                                text: "+ Дати"
                                md_bg_color: 0.1, 0.6, 0.1, 1
                                size_hint_x: 0.33
                                on_release: app.show_toast("Кошти додано")
                            MDRaisedButton:
                                text: "- Забрати"
                                md_bg_color: 0.6, 0.3, 0.1, 1
                                size_hint_x: 0.33
                                on_release: app.show_toast("Кошти забрано")
                            MDRaisedButton:
                                text: "= Встановити"
                                md_bg_color: 0.1, 0.4, 0.7, 1
                                size_hint_x: 0.33
                                on_release: app.show_toast("Баланс встановлено")

                        MDRaisedButton:
                            text: "Закрити пульт керування"
                            size_hint_x: 1
                            md_bg_color: 0.2, 0.2, 0.2, 1
                            on_release: root.change_tab("chat")

            # Інші пусті/запасні розділи
            MDScreen:
                name: "map"
                MDLabel:
                    text: "Карта Азгарду завантажується..."
                    halign: "center"
            MDScreen:
                name: "politics"
                MDLabel:
                    text: "Політична система у розробці."
                    halign: "center"
            MDScreen:
                name: "market"
                MDLabel:
                    text: "Вільний ринок порожній."
                    halign: "center"
            MDScreen:
                name: "citizens"
                MDLabel:
                    text: "Список громадян Азгарду..."
                    halign: "center"
            MDScreen:
                name: "laws"
                MDLabel:
                    text: "Конституція та закони Азгарду."
                    halign: "center"
'''

class MainScreen(MDScreen):
    def change_tab(self, tab_name):
        self.ids.sm.current = tab_name

    def send_chat_msg(self):
        msg = self.ids.chat_input.text.strip()
        if msg:
            lbl = MDLabel(
                text=f"[color=00ffcc]Ви:[/color] {msg}",
                markup=True,
                adaptive_height=True
            )
            self.ids.chat_logs.add_widget(lbl)
            self.ids.chat_input.text = ""

    def send_pm_msg(self):
        target = self.ids.pm_target.text.strip()
        msg = self.ids.pm_input.text.strip()
        if target and msg:
            lbl = MDLabel(
                text=f"[color=ffcc00]До {target}:[/color] {msg}",
                markup=True,
                adaptive_height=True
            )
            self.ids.pm_logs.add_widget(lbl)
            self.ids.pm_input.text = ""
            MDApp.get_running_app().show_toast("Повідомлення надіслано!")

    def make_transfer(self):
        target = self.ids.transfer_target.text.strip()
        amount = self.ids.transfer_amount.text.strip()
        if target and amount:
            MDApp.get_running_app().show_toast(f"Успішно переказано {amount} Ю гравцю {target}")
            self.ids.transfer_target.text = ""
            self.ids.transfer_amount.text = ""

    def play_casino(self):
        bet = self.ids.casino_bet.text.strip()
        if bet:
            MDApp.get_running_app().show_toast(f"Ставка {bet} Ю прийнята! Ставимо...")


class AsgardApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        return Builder.load_string(KV)

    def show_toast(self, text):
        toast(text)

if __name__ == '__main__':
    AsgardApp().run()
