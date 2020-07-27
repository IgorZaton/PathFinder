from kivy.app import App
from functools import partial
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse, Line, Rectangle
from random import random
from kivy.properties import ObjectProperty
from kivy.core.window import Window
import pathfinding_algorithms as pa
from PIL import Image
import os


class Menu(Widget):

    algorithm = ObjectProperty(None)
    start_button = ObjectProperty(None)
    stop_button = ObjectProperty(None)
    wall_button = ObjectProperty(None)
    rubber_button = ObjectProperty(None)
    diagonal_move_btn = ObjectProperty(None)
    diagonal_move = False
    alg_list = ["Dijkstra", "A*"]
    list_idx = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.algorithm.text = self.alg_list[self.list_idx]
        self.wall_button.background_color = [0, 0, 1, 1]

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
                    self.starting_point = (touch.x, self.height-(touch.y-self.height))
                elif self.color == (1, 1, 1):
                    self.goal_point = (touch.x, self.height-(touch.y-self.height)) #so it would later match with data_matrix
                touch.ud['line'] = Line(points=[touch.x, touch.y], width=5)

    def on_touch_move(self, touch):
        if 'line' in touch.ud and touch.y > self.height:
            touch.ud['line'].points += [touch.x, touch.y]

    def paint_solution(self):
        self.canvas.clear()
        with self.canvas:
            Rectangle(source="sol.png", pos=self.pos, size=self.size)


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
            if self.menu.list_idx == 0:
                self.paint.export_to_png(filename="drw.png")
                data_matrix = pa.image_to_matrix("drw.png", delete_a_in_rgba=True)
                self.path = pa.dijkstra(data_matrix, self.paint.starting_point, self.paint.goal_point,
                                        diagonal_move=self.menu.diagonal_move)
                data_matrix = pa.paint_path(data_matrix, self.path)
                img = Image.fromarray(data_matrix)
                #os.remove("sol.png")
                img.save("sol.png")
                self.paint.paint_solution()
            else:
                pass
        else:
            print("We dont do that here")
            pass

    def wall(self):
        self.paint.color = (0, 0, 1)
        self.menu.wall_button.background_color = [0, 0, 1, 1]
        self.menu.start_button.background_color = [1, 1, 1, 1]
        self.menu.stop_button.background_color = [1, 1, 1, 1]
        self.menu.rubber_button.background_color = [1, 1, 1, 1]

    def start_point(self):
        self.paint.color = (0.3, 1, 1)
        self.menu.wall_button.background_color = [1, 1, 1, 1]
        self.menu.start_button.background_color = [0, 0, 1, 1]
        self.menu.stop_button.background_color = [1, 1, 1, 1]
        self.menu.rubber_button.background_color = [1, 1, 1, 1]

    def stop_point(self):
        self.paint.color = (1, 1, 1)
        self.menu.wall_button.background_color = [1, 1, 1, 1]
        self.menu.start_button.background_color = [1, 1, 1, 1]
        self.menu.stop_button.background_color = [0, 0, 1, 1]
        self.menu.rubber_button.background_color = [1, 1, 1, 1]

    def rubber(self):
        self.paint.color = (0, 0, 0)
        self.menu.wall_button.background_color = [1, 1, 1, 1]
        self.menu.start_button.background_color = [1, 1, 1, 1]
        self.menu.stop_button.background_color = [1, 1, 1, 1]
        self.menu.rubber_button.background_color = [0, 0, 1, 1]

    def prev(self):
        idx = self.menu.list_idx
        if idx == 0:
            self.menu.algorithm.text = self.menu.alg_list[len(self.menu.alg_list)-1]
            self.menu.list_idx = len(self.menu.alg_list)-1
        else:
            self.menu.algorithm.text = self.menu.alg_list[idx-1]
            self.menu.list_idx -= 1

    def next(self):
        idx = self.menu.list_idx
        if idx == len(self.menu.alg_list)-1:
            self.menu.algorithm.text = self.menu.alg_list[0]
            self.menu.list_idx = 0
        else:
            self.menu.algorithm.text = self.menu.alg_list[idx+1]
            self.menu.list_idx += 1

    def diagonal_move(self):
        if self.menu.diagonal_move:
            self.menu.diagonal_move = False
            self.menu.diagonal_move_btn.background_color = [1, 1, 1, 1]
        else:
            self.menu.diagonal_move = True
            self.menu.diagonal_move_btn.background_color = [0, 0, 1, 1]

    def exit(self):
        exit()


MainApp().run()
