"""Blue Photon Processor+

Application to consult blueprints, calculate required materials
and discounts for bulk builds for the game Star Sonata.
"""

# Project stuff
from bpp_screen import BppScreen    # GUI
from bpp_logic import BppLogic      # Logic module

# Kivy stuff
from kivy.app import App
from kivy.uix.settings import SettingsWithSidebar


class BPP(App):
    """Blue Photon Processor+

    Governing class of the BPP+ application. Handling interaction between GUI, logic and database.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.version = 0.1
        self.icon = 'BPP+_icon.png'
        self.logic = BppLogic()

        # Prepare settings
        self.settings_cls = SettingsWithSidebar

        # Prepare screen (only declared, initialised at .run()
        self.screen = None

    def build(self):
        # Prepare GUI
        self.screen = BppScreen()
        return self.screen

    def calculate_cost(self, bp_name):
        """
        Calculates the cost of a specified blueprint in basic commodities.

        Args:
            bp_name (str): Name of the blueprint to calculate cost for in basic commodities.

        Returns:

        """
        # Propagate cost dictionary for display
        self.screen.update_cost_dict(self.logic.calculate_cost(bp_name))

    @staticmethod
    def print_debug_text(text):
        print(text)

    def on_stop(self):
        """Whenever the application is closed, ensure it quits gracefully."""
        self.logic.stop()   # Signal logic module to wrap up
        return True


if __name__ == '__main__':
    """ Starting BPP+. """

    # Start application
    BPP().run()
