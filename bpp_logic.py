from bpp_db import BppDb


class BppLogic:
    """
    Class handling all calculations required by the application.
    Also acts as intermediary between application and database.
    """

    def __init__(self, db_file=None):
        """
        Class is initialised by initialising the database.

        Args:
            db_file (str, optional): Name (and location) of the database file
        """
        # Connect to provided or standard database
        if db_file is None:
            self.db = BppDb('bpp.db')
        else:
            self.db = BppDb(db_file)
        self.db.create_connection()

        # Initialise cost dictionaries of blueprint under review
        self.init_cost = {}
        self.per_cost = {}
        self.total_cost = {}

    def check_db_version(self):
        """ Placeholder to check whether there is a new database available. """
        pass

    def get_all_blueprints(self):
        """ Query all blueprints from the blueprints table.

        Returns:
            A list of all blueprints in the database.
        """
        return self.db.get_all_blueprints()

    def find_blueprint(self, bp_name):
        """ Retrieves all information about a specified blueprint.

        Args:
            bp_name (str): Name of the blueprint to find.
        Returns:
            Complete results found for specified blueprint name.
        """
        # Returns dictionary with column names as keys and corresponding values
        return self.db.find_blueprint(bp_name)

    def calculate_cost(self, bp_name):
        """
        Calculates the cost of a specified blueprint in basic commodities.

        Args:
            bp_name (str): Name of the blueprint to calculate cost for in basic commodities.

        Returns:
            Dictionary of total costs in basic commodities for the blueprint's product.
        """
        # Retrieve (dictionary of) blueprint
        bp = self.db.find_blueprint(bp_name)
        # Extract initial costs and put into dict
        self.init_cost = dict(
            zip(bp['init_materials'][1:-1].split(', '),
                [int(x) for x in bp['init_materials_n'][1:-1].split(', ')]))
        # Extract periodic costs and put into dict
        self.per_cost = dict(
            zip(bp['per_materials'][1:-1].split(', '),
                [int(x) for x in bp['per_materials_n'][1:-1].split(', ')]))
        # Construct total costs dictionary by adding periodic to initial materials
        self.total_cost = self.init_cost.copy()     # Copy entire init_cost. Dict is reference by default.
        for mat, n in self.per_cost.items():
            if mat in self.init_cost:
                self.total_cost[mat] += n
            else:
                self.total_cost[mat] = n

        # Return dictionary of total costs
        return self.total_cost

    def stop(self):
        """Close database connection when application is stopped."""
        self.db.close_connection()
