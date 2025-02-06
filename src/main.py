from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from recognition.face_recognition import start_recognition
from widgets.calendar_widget import CalendarWidget
from widgets.grid_overlay import GridOverlay
from widgets.upcoming_events_widget import UpcomingEventsWidget

# Explicitly load the KV file if its name does not follow auto-load conventions.
Builder.load_file('src/main.kv')

class DashboardScreen(Screen):
    def on_kv_post(self, base_widget):
        # Confirm IDs are loaded.
        print("DashboardScreen IDs:", self.ids)

    def update_profile(self, profile_name):
        # Update the background image based on the profile.
        if profile_name == "user1":
            bg_source = "assets/user1_bg.jpg"
        else:
            bg_source = "assets/guest_bg.jpg"
        self.ids.bg_image.source = bg_source
        self.ids.profile_label.text = f"Profile: {profile_name}"

class SettingsScreen(Screen):
    pass

class MirrorMindApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.dashboard = DashboardScreen(name='dashboard')
        self.settings = SettingsScreen(name='settings')
        self.sm.add_widget(self.dashboard)
        self.sm.add_widget(self.settings)
        
        start_recognition(self.on_profile_update)
        Clock.schedule_interval(lambda dt: self.check_for_profile_update(), 1)
        return self.sm

    def on_start(self):
        # Create a single overlay and size it to cover the window
        grid_overlay = GridOverlay(grid_size=(12, 12))
        grid_overlay.size = Window.size
        grid_overlay.pos = (0, 0)
        grid_overlay.opacity = 0

        # Add overlay to dashboard so it is drwan above other widgets
        self.dashboard.add_widget(grid_overlay)

        # Ensure that widget_grid exists before accessing it.
        widget_grid = self.dashboard.ids.get('widget_grid')
        if widget_grid:
            cal1 = CalendarWidget(grid_size=(12, 12), grid_width=6, grid_height=6,)
            widget_grid.add_widget(cal1)
            cal1.overlay = grid_overlay
            
            cal2 = UpcomingEventsWidget(grid_size=(12, 12), grid_width=3, grid_height=12)
            widget_grid.add_widget(cal2)
            cal2.overlay = grid_overlay
        else:
            print("widget_grid not found in dashboard.ids")

    def on_profile_update(self, profile_name):
        # Schedule the UI update to run on the main thread
        Clock.schedule_once(lambda dt: self.dashboard.update_profile(profile_name))

    def check_for_profile_update(self):
        pass

if __name__ == '__main__':
    MirrorMindApp().run()