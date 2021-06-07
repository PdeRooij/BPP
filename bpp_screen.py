# Kivy stuff
from kivy.uix.tabbedpanel import TabbedPanel


class BppScreen(TabbedPanel):

    def __init__(self, **kwargs):
        """
        Initialise with a (temporary) dictionary that holds the cost
        of producing one of the currently selected blueprint.

        Args:
            **kwargs:
        """
        super().__init__(**kwargs)
        self.cost_dict = {}

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
            mat_sum += ''.join(['\n' + str(number * n) + ' ' + mat for mat, n in self.cost_dict.items()])
            # Display constructed summary
            self.ids['build_info'].text = mat_sum
        else:
            # Empty dictionary, display error
            self.ids['build_info'].text = 'Please select a blueprint first!'
