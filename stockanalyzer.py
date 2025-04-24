from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import os, threading
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

Window.clearcolor = (1, 1, 1, 1)
Window.size = (360, 640)

if os.name == 'nt':
    emoji_font_path = 'C:/Windows/Fonts/seguiemj.ttf'
    if os.path.exists(emoji_font_path):
        LabelBase.register(name='EmojiFont', fn_regular=emoji_font_path)

recommendations = [
    {"symbol": "AAPL", "name": "Apple Inc.", "risk": "Safe"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "risk": "Moderate"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "risk": "Risky"},
]

safe_stocks = [
    {"symbol": "MSFT", "name": "Microsoft Corp."},
    {"symbol": "JNJ", "name": "Johnson & Johnson"},
]

def get_live_news():
    return [
        "🗞️ Apple hits new high amid strong earnings",
        "🗞️ Tesla shares dip as delivery numbers fall short",
        "🗞️ Google unveils new AI features for search",
        "🗞️ Microsoft invests further in cloud infrastructure",
        "🗞️ Johnson & Johnson announces new vaccine study",
        "🗞️ Stock market closes higher on Fed optimism",
        "🗞️ Tech stocks rally amid investor confidence",
        "🗞️ Wall Street analysts upgrade major stocks",
        "🗞️ Economic indicators show signs of recovery",
        "🗞️ Market volatility expected to rise in Q2"
    ]

def colored_card(bg_color, content_widgets):
    card = BoxLayout(orientation='vertical', padding=6, spacing=4, size_hint_y=None)
    card.height = sum(widget.height for widget in content_widgets) + 20
    with card.canvas.before:
        Color(*bg_color)
        card.rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[10])
    card.bind(pos=lambda *a: setattr(card.rect, 'pos', card.pos),
              size=lambda *a: setattr(card.rect, 'size', card.size))
    for widget in content_widgets:
        card.add_widget(widget)
    return card

def fetch_price(symbol, label):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        price = data['Close'].iloc[-1] if not data.empty else 'N/A'
        label.text = f"Price: ${price:.2f}" if price != 'N/A' else "Price: N/A"
    except Exception:
        label.text = "Price: Error"

def create_chart(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1mo')
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.plot(data.index, data['Close'], color='dodgerblue')
        ax.set_title(f"{symbol} - 30 Days", fontsize=10)
        ax.tick_params(labelsize=8)
        fig.tight_layout()
        return FigureCanvasKivyAgg(fig)
    except Exception as e:
        return Label(text="Chart error", color=(1,0,0,1), size_hint_y=None, height=30)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.bg = Rectangle(source='assets/background.jpg', size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='📈 Stock Market Analyzer', font_size='24sp', font_name='EmojiFont', size_hint_y=None, height=60, color=(0, 0, 0, 1)))
        layout.add_widget(Button(text='🔄 Get Recommendations', font_name='EmojiFont', background_color=(0.2, 0.6, 1, 1), color=(1,1,1,1), on_press=self.show_recommendations))
        layout.add_widget(Button(text='🛡️ Safe Stocks', font_name='EmojiFont', background_color=(0.1, 0.8, 0.6, 1), color=(1,1,1,1), on_press=self.show_safe_stocks))
        layout.add_widget(Button(text='🔁 Refresh', font_name='EmojiFont', background_color=(0.8, 0.8, 0.2, 1), color=(0,0,0,1), size_hint_y=None, height=40, on_press=lambda x: self.display_stocks(recommendations, include_risk=True)))

        self.result_area = ScrollView(size_hint=(1, 1))
        layout.add_widget(self.result_area)

        self.add_widget(layout)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def show_recommendations(self, instance):
        self.display_stocks(recommendations, include_risk=True)

    def show_safe_stocks(self, instance):
        self.display_stocks(safe_stocks, include_risk=False)

    def display_stocks(self, stocks, include_risk):
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        grid.bind(minimum_height=grid.setter('height'))

        for stock in stocks:
            price_label = Label(text="Loading...", font_size='14sp', font_name='EmojiFont', color=(0,0,0,1), size_hint_y=None, height=20)
            threading.Thread(target=fetch_price, args=(stock['symbol'], price_label)).start()

            widgets = [
                Label(text=f"{stock['symbol']} - {stock['name']}", font_size='16sp', font_name='EmojiFont', color=(0,0,0,1), size_hint_y=None, height=25),
                price_label
            ]

            if include_risk:
                risk = stock['risk']
                risk_color = {
                    'Safe': (0.1, 0.6, 0.2, 0.9),
                    'Moderate': (0.9, 0.6, 0.1, 0.9),
                    'Risky': (0.8, 0.2, 0.2, 0.9),
                }.get(risk, (0.5, 0.5, 0.5, 0.9))
                widgets.append(Label(text=f"Risk Level: {risk}", font_name='EmojiFont', color=risk_color, size_hint_y=None, height=20))
                widgets.append(Button(text='More Info', font_name='EmojiFont', background_color=risk_color, color=(1,1,1,1), size_hint_y=None, height=30, on_press=lambda x, s=stock: self.show_popup(s)))

            card = colored_card(bg_color=(0.9, 0.9, 0.95, 1), content_widgets=widgets)
            card.size_hint_y = None
            card.height = 110
            grid.add_widget(card)

        self.result_area.clear_widgets()
        self.result_area.add_widget(grid)

    def show_popup(self, stock):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=f"Detailed info for {stock['symbol']}", font_name='EmojiFont', color=(0,0,0,1)))
        popup_layout.add_widget(Label(text=f"Company: {stock['name']}", font_name='EmojiFont', color=(0,0,0,1)))
        popup_layout.add_widget(Label(text=f"Risk Level: {stock.get('risk', 'N/A')}", font_name='EmojiFont', color=(0,0,0,1)))
        popup_layout.add_widget(create_chart(stock['symbol']))
        popup_layout.add_widget(Button(text='Close', font_name='EmojiFont', background_color=(0.3, 0.3, 0.3, 1), color=(1,1,1,1), size_hint_y=None, height=40, on_press=lambda x: popup.dismiss()))
        popup = Popup(title='Stock Details', content=popup_layout, size_hint=(0.95, 0.95))
        popup.open()

class NewsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='📰 News Feed', font_size='24sp', font_name='EmojiFont', size_hint_y=None, height=60, color=(0, 0, 0, 1)))
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        grid.bind(minimum_height=grid.setter('height'))

        headlines = get_live_news()
        for headline in headlines:
            grid.add_widget(colored_card((0.95, 0.95, 0.98, 1), [Label(text=headline, font_name='EmojiFont', color=(0,0,0,1), size_hint_y=None, height=30)]))

        scroll.add_widget(grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

class StockApp(App):
    def build(self):
        self.icon = 'assets/stock_icon.png'
        self.title = 'Stock Analyzer'
        root_layout = BoxLayout(orientation='vertical')
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(NewsScreen(name='news'))
        nav_bar = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=5)
        nav_bar.add_widget(Button(text='🏠 Home', font_name='EmojiFont', on_press=lambda x: setattr(sm, 'current', 'home')))
        nav_bar.add_widget(Button(text='📰 News', font_name='EmojiFont', on_press=lambda x: setattr(sm, 'current', 'news')))
        root_layout.add_widget(sm)
        root_layout.add_widget(nav_bar)
        return root_layout

if __name__ == '__main__':
    StockApp().run()
