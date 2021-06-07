"""Blue Photon Processor+

Application to consult blueprints, calculate required materials
and discounts for bulk builds for the game Star Sonata.
"""

# Project stuff
from bpp_screen import BppScreen  # GUI
from bpp_db import BppDb          # Database

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
        self.db = BppDb()

        # Prepare settings
        self.settings_cls = SettingsWithSidebar

        # Prepare screen (only declared, initialised at .run()
        self.screen = None

    def build(self):
        # Connect to database
        self.db.create_connection()
        # self.db.initialise_database()

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
        # Retrieve (dictionary of) blueprint
        bp = self.db.find_blueprint(bp_name)
        # Extract single costs and put into dict
        cost_dict = dict(
            zip(bp['init_materials'][1:-1].split(', '),
                [int(x) for x in bp['init_materials_n'][1:-1].split(', ')]))
        for mat, n in zip(bp['per_materials'][1:-1].split(', '),
                          [int(x) for x in bp['per_materials_n'][1:-1].split(', ')]):
            if mat in cost_dict:
                cost_dict[mat] += n
            else:
                cost_dict[mat] = n
        # Propagate cost dictionary for display
        self.screen.update_cost_dict(cost_dict)

    @staticmethod
    def print_debug_text(text):
        print(text)

    def on_stop(self):
        self.db.close_connection()  # Close database connection
        return True


if __name__ == '__main__':
    """ Starting BPP+. Connect to database and start application. """

    # Start application
    BPP().run()
