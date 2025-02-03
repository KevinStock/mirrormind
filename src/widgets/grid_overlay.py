from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.core.window import Window
from kivy.graphics import Color, Line

class GridOverlay(Widget):
    grid_size = ObjectProperty((12, 12))
    line_color = (1, 0, 0, 0.3)

    def on_size(self, *args):
        self.update_grid()

    def on_pos(self, *args):
        self.update_grid()

    def on_grid_size(self, *args):
        self.update_grid()

    def update_grid(self):
        self.canvas.clear()
        with self.canvas:
            Color(*self.line_color)

            cols, rows = self.grid_size
            total_width = Window.width
            total_height = Window.height
            cell_w = max(total_width / cols, 1)
            cell_h = max(total_height / rows, 1)

            # Draw vertical lines
            for c in range(cols + 1):
                x = c * cell_w
                Line(points=[x, 0, x, Window.height])
            
            # Draw horizontal lines
            for r in range(rows + 1):
                y = r * cell_h
                Line(points=[0, y, Window.width, y])