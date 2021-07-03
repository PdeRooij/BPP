# Make display locale aware
import locale

# Kivy stuff
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button


class BpDropButton(Button):
    """Special button for a blueprint in the blueprint dropdown menu."""

    def __init__(self, **kwargs):
        """
        Merely pass on to super to include all regular button behaviour.
        """
        super().__init__(**kwargs)


class BppScreen(TabbedPanel):
    """
    Class handling all graphical interactions.
    """

    def __init__(self, **kwargs):
        """
        Initialise with a (temporary) dictionary that holds the cost
        of producing one of the currently selected blueprint.

        Args:
            **kwargs:
        """
        super().__init__(**kwargs)
        locale.setlocale(locale.LC_ALL, '')     # Autodetect and set locale
        self.cost_dict = {}

    def populate_dropdown(self, bp_list):
        """
        Adds all given blueprints as buttons to the dropdown menu.

        Args:
            bp_list (list): All blueprint names in the database.
        """
        # Loop through blueprints and add each as button
        for bp in bp_list:
            # Construct button
            bp_btn = BpDropButton(text=bp)
            bp_btn.bind(on_release=lambda btn: self.ids['bp_drop'].select(btn.text))
            # Add button to dropdown list
            self.ids['bp_drop'].add_widget(bp_btn)

    def update_cost_dict(self, new_cost):
        """

        Args:
            new_cost:

        Returns:

        """
        self.cost_dict = new_cost
        # Also display costs
        self.update_cost(1)

    def update_cost(self, number):
        """
        Updates the material cost summary display, based on a given desired amount.

        Args:
            number (int): Amount of products that need to be built.

        Returns:

        """
        # Only calculate if base materials are known
        if self.cost_dict:
            # Construct summary string
            mat_sum = 'Summary of required materials:'
            mat_sum += ''.join(['\n' + f'{number * n:n}' + ' ' + mat for mat, n in self.cost_dict.items()])
            # Display constructed summary
            self.ids['build_info'].text = mat_sum
        else:
            # Empty dictionary, display error
            self.ids['build_info'].text = 'Please select a blueprint first!'

    def update_setup(self, setup):
        """
        Updates the material cost summary display, based on a given desired amount.

        Args:
            setup (str): String of optimal ExE kit setup

        Returns:

        """
        # Display constructed summary
        self.ids['exe_info'].text = setup
