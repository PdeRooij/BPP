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
        self.version = 0.21
        self.icon = 'BPP+_icon.png'
        self.logic = BppLogic()

        # Prepare settings
        self.settings_cls = SettingsWithSidebar

        # Prepare screen (only declared, initialised at .run()
        self.screen = None

    def build(self):
        # Give neat name to app
        self.title = 'BPP+ (Blue Photon Processor+)'
        # Prepare GUI
        self.screen = BppScreen()
        self.screen.populate_dropdown(self.logic.get_all_blueprints())
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

    def calculate_exe_setup(self, **kwargs):
        """
        Calculates optimal configuration of an ExE kit, given skill level, kit tech and extraction slots.

        Args:
            kwargs (any, optional): ExE information, including:
                tech (str, optional): Tech level of the kit.
                met (str, optional): Metals slots available on celestial body.
                nuc (str, optional): Nuclear Waste slots available on celestial body.
                sil (str, optional): Silicon slots available on celestial body.
                oat (str, optional): Space Oats slots available on celestial body.
                bao (str, optional): Baobabs slots available on celestial body.

        """
        # Convert all given strings into numbers
        nums = {}   # Empty dictionary to copy numbers into
        for com, n in kwargs.items():
            if n == '':
                nums[com] = 0
            else:
                nums[com] = int(n)

        # Pass information on to logic module and return setup dictionary to UI
        self.screen.update_setup(self.logic.calculate_exe_setup(**nums))

    @staticmethod
    def print_debug_text(text):
        print(text)

    def get_db_version(self):
        """Retrieves version of connected database.

        Returns:
            str: Database version in string format.
        """
        return self.logic.get_db_version()

    def on_stop(self):
        """Whenever the application is closed, ensure it quits gracefully."""
        self.logic.stop()   # Signal logic module to wrap up
        return True


if __name__ == '__main__':
    """ Starting BPP+. """

    # Start application
    BPP().run()
