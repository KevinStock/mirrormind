from widgets.base_widget import WidgetCard

class CalendarWidget(WidgetCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Calendar"
        # Additional initialization for calendar functionality