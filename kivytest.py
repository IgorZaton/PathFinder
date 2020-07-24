from kivy.app import App
from functools import partial
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse, Line, Rectangle
from random import random
from kivy.core.window import Window
from image_to_rgb_matrix import image_to_rgb_matrix


class Menu(Widget):

    def build(self):
        pass


class Paint(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 1)

    def on_touch_down(self, touch):
        with self.canvas:
            Color(*self.color, mode='hsv')
            d = 10.
            if touch.y > self.height:
                Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                if self.color == (0.3, 1, 1):
                    self.starting_point = (touch.x, touch.y)
                elif self.color == (1, 1, 1):
                    self.goal_point = (touch.x, touch.y)
                touch.ud['line'] = Line(points=[touch.x, touch.y], width=5)
            else:
                pass

    def on_touch_move(self, touch):
        if 'line' in touch.ud and touch.y > self.height:
            touch.ud['line'].points += [touch.x, touch.y]
        else:
            pass


class MainApp(App):

    def build(self):
        layout = GridLayout(rows=2)
        self.menu = Menu()
        self.paint = Paint()
        layout.add_widget(self.paint)
        layout.add_widget(self.menu)
        return layout

    def clear(self):
        if hasattr(self.paint, 'starting_point'):
            delattr(self.paint, 'starting_point')
        if hasattr(self.paint, 'goal_point'):
            delattr(self.paint, 'goal_point')
        self.paint.canvas.clear()

    def start(self):
        if hasattr(self.paint, 'starting_point') and hasattr(self.paint, 'goal_point'):
            self.paint.export_to_png(filename="drw.png")
            data_matrix = image_to_rgb_matrix("drw.png", delete_a_in_rgba=True)


        else:
            print("We dont do that here")
            pass



    def wall(self):
        self.paint.color = (0, 0, 1)

    def start_point(self):
        self.paint.color = (0.3, 1, 1)

    def stop_point(self):
        self.paint.color = (1, 1, 1)

    def rubber(self):
        self.paint.color = (0, 0, 0)


MainApp().run()