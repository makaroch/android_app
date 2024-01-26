import threading
import asynckivy
import requests
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen

KV = '''
<UserCard>
    adaptive_height: True
    radius: 16

    MDListItem:
        radius: 16
        theme_bg_color: "Custom"
        md_bg_color: self.theme_cls.secondaryContainerColor

        MDListItemLeadingAvatar:
            size_hint_y: 1

            source: root.img

        MDListItemHeadlineText:
            text: root.name

        MDListItemSupportingText:
            text: f"Цена: {root.price}  Рейтинг: {root.rate}  Кол-во отзывов: {root.feedbacks}"

        MDListItemTertiaryText:
            text: root.date_delivery

        MDListItemTrailingIcon:
            icon: "bookmark-minus"

<BaseMDNavigationItem>

    MDNavigationItemIcon:
        icon: root.icon

    MDNavigationItemLabel:
        text: root.text


<BaseScreen>

    MDLabel:
        text: root.name
        halign: "center"


MDBoxLayout:
    orientation: "vertical"
    md_bg_color: self.theme_cls.backgroundColor

    MDScreenManager:
        id: screen_manager

        BaseScreen:
            name: "Закладки"

        BaseScreen:
            name: "Найдено"

            RecycleView:
                id: card_list
                viewclass: "UserCard"
                bar_width: 0

                RecycleBoxLayout:
                    orientation: 'vertical'
                    spacing: "16dp"
                    padding: "16dp"
                    default_size: None, dp(72)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
        BaseScreen:
            name: "Поиск"

            MDScrollView:

                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    spacing: "20dp"
                    padding: [8,20,8,0]

                    MDLabel:
                        adaptive_height: True
                        text: "Фильтры"
                        theme_font_style: "Custom"
                        font_style: "Display"
                        role: "small"

                    MDTextField:
                        mode: "filled"
                        on_focus: app.set_query(self)

                        MDTextFieldLeadingIcon:
                            icon: "magnify"

                        MDTextFieldHelperText:
                            text: "Что искать? Для поиска нескольких товаров сразу введите искомое черз запятую"
                            mode: "on_focus"

                    MDTextField:
                        mode: "filled"
                        on_focus: app.set_city(self)

                        MDTextFieldLeadingIcon:
                            icon: "city"

                        MDTextFieldHelperText:
                            text: "Город для доставки"
                            mode: "on_focus"


                    MDTextField:
                        mode: "filled"
                        on_focus: app.set_quantity(self)

                        MDTextFieldLeadingIcon:
                            icon: "clippy"

                        MDTextFieldHelperText:
                            text: "Количество карт товара с каждой площадки(до 100 едениц)"
                            mode: "on_focus"

                    MDLabel:
                        adaptive_height: True
                        text: "Срок доставки"
                        role: "small"
                        halign: "center"

                    MDSegmentedButton:
                        adaptive_height: True

                        MDSegmentedButtonItem:
                            on_press: app.two_days()
                            MDSegmentButtonLabel:
                                text: "до 2 дней"

                        MDSegmentedButtonItem:
                            on_press: app.three_days()
                            MDSegmentButtonLabel:
                                text: "до 3 дней"

                        MDSegmentedButtonItem:
                            on_press: app.five_days()
                            MDSegmentButtonLabel:
                                text: "до 5 дней"
                    MDLabel:
                        adaptive_height: True
                        text: "Сортировать по:"
                        halign: "center"
                        role: "small"

                    MDSegmentedButton:

                        MDSegmentedButtonItem:
                            on_press: app.set_sort_popular()
                            MDSegmentButtonLabel:
                                text: "Популярности"

                        MDSegmentedButtonItem:
                            on_press: app.set_sort_rate()
                            MDSegmentButtonLabel:
                                text: "Рейтингу"


                    MDSegmentedButton:

                        MDSegmentedButtonItem:
                            on_press: app.set_sort_price_down()
                            MDSegmentButtonLabel:
                                text: "Убыванию цены"
                        MDSegmentedButtonItem:
                            on_press: app.set_sort_price_up()
                            MDSegmentButtonLabel:
                                text: "Возрастанию цены"


                    # цены   
                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "20dp"

                        MDTextField:
                            mode: "filled"
                            on_focus: app.set_min_price(self)
                            MDTextFieldLeadingIcon:
                                icon: "currency-rub"

                            MDTextFieldHelperText:
                                text: "Минимальная цена, только цифры"
                                mode: "on_focus"

                        MDTextField:
                            mode: "filled"
                            on_focus: app.set_max_price(self)
                            MDTextFieldLeadingIcon:
                                icon: "currency-rub"

                            MDTextFieldHelperText:
                                text: "Максимальная цена, только цифры"
                                mode: "on_focus"
                    #кнопочка        
                    MDBoxLayout:
                        orientation: 'vertical'
                        adaptive_height: True

                        MDButton:
                            style: "tonal"
                            pos_hint: {"center_x": .5, "center_y": .1}
                            on_press: app.start_search(self)
                            MDButtonText:
                                text: "Искать"


    MDNavigationBar:
        on_switch_tabs: app.on_switch_tabs(*args)

        BaseMDNavigationItem
            icon: "gmail"
            text: "Закладки"
            active: True

        BaseMDNavigationItem
            icon: "twitter"
            text: "Найдено"
        BaseMDNavigationItem
            icon: "magnify"
            text: "Поиск"
'''


class BaseScreen(MDScreen):
    pass


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class UserCard(MDBoxLayout):
    name = StringProperty()
    price = StringProperty()
    rate = StringProperty()
    feedbacks = StringProperty()
    date_delivery = StringProperty()
    link = StringProperty()
    img = StringProperty()


class Temporary(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.days: int = 124
        self.is_search_running = False
        self.query: str = ""
        self.city: str = "Москва"
        self.min_price: int = 1
        self.max_price = 10000
        self.sort = "popular"
        self.quantity = 5

    def set_sort_popular(self):
        self.sort = "popular"

    def set_sort_rate(self):
        self.sort = "rate"

    def set_sort_price_up(self):
        self.sort = "price_up"

    def set_sort_price_down(self):
        self.sort = "price_down"

    def set_quantity(self, label):
        if label.text != "":
            self.quantity = label.text

    def set_query(self, label):
        if label.text != "":
            self.query = label.text

    def set_city(self, label):
        if label.text != "":
            self.city = label.text

    def set_min_price(self, label):
        if label.text != "":
            self.min_price = label.text

    def set_max_price(self, label):
        if label.text != "":
            self.max_price = label.text

    def generate_card(self):
        one_product_url = (f"http://91.107.125.146:8080/get_product?search={self.query}&city={self.city}"
                           f"&sorting={self.sort}&delivery_time={self.days}&min_price={self.min_price}"
                           f"&max_prise={self.max_price}&quantity={self.quantity}")

        response = requests.get(url=one_product_url)

        self.__generate_card(response.json())

    @mainthread
    def __generate_card(self, data: list):
        self.is_search_running = False
        self.button.opacity = 1

        async def generate_card():
            for item in data:
                await asynckivy.sleep(0)
                self.root.ids.card_list.data.append(
                    {
                        "name": item.get("name"),
                        "price": str(item.get("price")),
                        "rate": str(item.get("rate")),
                        "feedbacks": str(item.get("feedbacks")),
                        "date_delivery": item.get("date_delivery"),
                        "link": item.get("link"),
                        "img": item.get("img")
                    }
                )

        self.root.ids.card_list.data = []
        Clock.schedule_once(lambda x: asynckivy.start(generate_card()))

    def start_search(self, button):
        self.button = button
        if self.is_search_running:
            return
        self.is_search_running = True

        self.on_switch_tabs(None, None, None, "Найдено")
        button.opacity = 0

        threading.Thread(target=self.generate_card).start()

    def two_days(self):
        self.days = 52

    def three_days(self):
        self.days = 76

    def five_days(self):
        self.days = 124

    def on_switch_tabs(
            self,
            bar: MDNavigationBar,
            item: MDNavigationItem,
            item_icon: str,
            item_text: str,
    ):
        self.root.ids.screen_manager.current = item_text

    def build(self):
        return Builder.load_string(KV)


Temporary().run()
