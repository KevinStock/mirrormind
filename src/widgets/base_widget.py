from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.core.window import Window

class WidgetCard(BoxLayout):
    title = StringProperty("Widget")
    grid_size = ObjectProperty((12, 12))
    grid_width = NumericProperty(1)
    grid_height = NumericProperty(1)
    widget_padding = NumericProperty(10)  # Add padding property
    widget_width = NumericProperty(Window.width * 0.5)
    widget_height = NumericProperty(Window.height * 0.75)
    _resizing = False
    _resizing_corner_size = 30
    overlay = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.update_size)
        self.update_size(Window, Window.width, Window.height)
        self._dragging = False
        self._drag_offset_x = 0
        self._drag_offset_y = 0

    def update_size(self, instance, width, height):
        cols, rows = self.grid_size

        total_width = width
        total_height = height
        cell_w = max(total_width / cols, 1)
        cell_h = max(total_height / rows, 1)

        self.widget_width = min(cell_w * self.grid_width, width) - 2 * self.widget_padding
        self.widget_height = min(cell_h * self.grid_height, height) - 2 * self.widget_padding

    def on_touch_down(self, touch):
        corner_x = self.right
        corner_y = self.y
        if (abs(corner_x - touch.x) < self._resizing_corner_size and
            abs(corner_y - touch.y) < self._resizing_corner_size):
            self._resizing = True
            return True
        elif self.collide_point(*touch.pos):
            self._drag_offset_x = touch.x - self.x
            self._drag_offset_y = touch.y - self.y
            self._dragging = True
            if self.overlay:
                self.overlay.opacity = 1
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._resizing:
            cols, rows = self.grid_size

            total_width = Window.width
            total_height = Window.height
            cell_w = max(total_width / cols, 1)
            cell_h = max(total_height / rows, 1)

            new_w = (touch.x - self.x) / cell_w
            new_h = (self.height + self.y - touch.y) / cell_h
            self.grid_width = max(1, round(new_w))
            self.grid_height = max(1, round(new_h))
            self.update_size(Window, Window.width, Window.height)
            return True
        elif self._dragging:
            self.x = touch.x - self._drag_offset_x
            self.y = touch.y - self._drag_offset_y
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        was_resizing = self._resizing
        was_dragging = self._dragging
        self._resizing = False
        self._dragging = False

        if was_resizing or was_dragging:
            cols, rows = self.grid_size

            total_width = Window.width
            total_height = Window.height
            cell_w = max(total_width / cols, 1)
            cell_h = max(total_height / rows, 1)

            closest_col = round(self.x / cell_w)
            closest_row = round(self.y / cell_h)
            closest_col = max(min(closest_col, cols - 1), 0)
            closest_row = max(min(closest_row, rows - 1), 0)

            snapped_x = closest_col * cell_w + self.widget_padding
            snapped_y = closest_row * cell_h + self.widget_padding

            max_x = Window.width - self.width - self.widget_padding
            max_y = Window.height - self.height - self.widget_padding
            self.x = min(max(snapped_x, self.widget_padding), max_x)
            self.y = min(max(snapped_y, self.widget_padding), max_y)

            if self.overlay:
                self.overlay.opacity = 0

        return super().on_touch_up(touch)