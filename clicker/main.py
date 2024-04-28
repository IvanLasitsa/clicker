from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.animation import Animation
from random import randint
from kivy.clock import Clock
from datetime import datetime
import json

class MenuScreen(Screen):
    pass

class GameScreen(Screen):
    points = NumericProperty(0)

    def on_enter(self, *args):
        self.ids.fruit.new_fruit()
        return super().on_enter(*args)

class Fruit(Image):
    is_anim = False
    hp = None
    fruit = None
    fruit_index = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            global points
            app = App.get_running_app()
            shop_screen = app.root.get_screen('shop')  
            points += 1 + shop_screen.click_points 
            app.root.get_screen('game').points = points
            self.hp -= 1 + shop_screen.click_points
            if self.hp <= 0:
                self.new_fruit()

            x = self.x
            y = self.y
            anim = Animation(x=x-5, y=y-5, duration=0.05) + Animation(x=x, y=y, duration=0.0005)
            anim.start(self)
            self.is_anim = True
            anim.on_complete = lambda *args: setattr(self, 'is_anim', False)
        return super().on_touch_down(touch)

    def Auto_Clicker(self, switch):
        if switch.active:
            Clock.schedule_interval(self.auto_click, 1)
        else:
            Clock.unschedule(self.auto_click)

    def auto_click(self, dt):
        global points
        points += 1
        self.parent.parent.parent.points = points
        self.hp -= 1
        if self.hp <= 0:
            self.new_fruit()

        x = self.x
        y = self.y
        anim = Animation(x=x-5, y=y-5, duration=0.05) + Animation(x=x, y=y, duration=0.005)
        anim.start(self)
        self.is_anim = True
        anim.on_complete = lambda *args: setattr(self, 'is_anim', False)

    def new_fruit(self):
        self.fruit = self.LEVELS[randint(0, len(self.LEVELS))-1]
        self.source = self.FRUIT[self.fruit]['source']
        self.hp = self.FRUIT[self.fruit]['hp']

    LEVELS = ['Apple', 'Banana','Pear']

    FRUIT = {
        'Apple': {"source": 'assets/images/apple.png', 'hp': 10},
        'Banana': {"source": 'assets/images/banana.png', 'hp': 20},
        'Pear': {"source": 'assets/images/pear.png', 'hp': 30},
    }

class Shop(Screen):
    points = NumericProperty(0)
    click_points = NumericProperty(0)
    price = NumericProperty(0) 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.price = 10

    def update_points(self, instance, value):
        self.points = value

    def buy(self):
        global points
        if points >= self.price:
            points -= self.price
            self.click_points += 1
            self.points = points
            self.price += 10 
            self.ids.price_label.text = "Price: " + str(self.price)
            


class MainApp(App):
    def build(self):
        sm = ScreenManager()
        game_screen = GameScreen(name='game')
        shop_screen = Shop(name='shop', points=game_screen.points)
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(game_screen)
        sm.add_widget(shop_screen)

        game_screen.bind(points=shop_screen.update_points)

        loaded_points = self.load_points()
        game_screen.points = loaded_points
        global points  
        points = loaded_points
        load_click_points = self.load_click_points()
        shop_screen.click_points = load_click_points
        price = self.load_price()
        shop_screen.price = price

        return sm

    def on_stop(self):
        self.save_points()
        self.save_click_points()
        self.save_price()

    def save_points(self):
        game_screen = self.root.get_screen('game')
        points_data = {'points': game_screen.points}
        with open('data/points.json', 'w') as f:
            json.dump(points_data, f)


    def load_points(self):
        try:
            with open('data/points.json', 'r') as f:
                points_data = json.load(f)
                loaded_points = points_data.get('points', 0)
                return loaded_points
        except FileNotFoundError:
            return 0 
        
    def save_click_points(self):
        Shop_screen = self.root.get_screen('shop')
        click_points_data = {'click_points': Shop_screen.click_points}
        with open('data/click_points.json', 'w') as f:
            json.dump(click_points_data, f)

    def load_click_points(self):
        try:
            with open('data/click_points.json', 'r') as f:
                click_points_data = json.load(f)
                click_loaded_points = click_points_data.get('click_points', 0)
                return click_loaded_points
        except FileNotFoundError:
            return 0
        
    def save_price(self):
        Shop_screen = self.root.get_screen('shop')
        price_data = {'price': Shop_screen.price}
        with open('data/price.json', 'w') as f:
            json.dump(price_data, f)

    def load_price(self):
        try:
            with open('data/price.json', 'r') as f:
                price_data = json.load(f)
                price = price_data.get('price', 10)
                return price
        except FileNotFoundError:
            return 0

if platform != 'android':
    Window.size = (400, 800)
    Window.left = +500
    Window.top = 100

points = 0  
app = MainApp().run()
