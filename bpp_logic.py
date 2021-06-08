# Project stuff
from bpp_db import BppDb

# OS stuff to work with files etc.
from os.path import isfile


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
        # Keep track whether the database has changed this session
        self.db_change = False
        # Use standard database location if no location is provided
        if db_file is None:
            db_file = 'bpp.db'
        # Determine whether given file is a database or dump
        if db_file[-3:] != '.db':
            # The file doesn't end with .db, so it's probably a dump
            if isfile(db_file):
                # Dump exists, so read that into standard database location
                dump_file = db_file
                db_file = 'bpp.db'
            else:
                # Dump doesn't even exist... Just fail.
                raise FileNotFoundError('Cannot find specified dump file ({})!'.format(db_file))
        else:
            # If database exists, just connect, otherwise resort to standard dump location
            if isfile(db_file):
                dump_file = None
            else:
                # Database does not exist yet, resort to standard dump location
                print('Database not found, resorting to default dump location.')
                dump_file = 'bpp_db.sql'

        # Prepare database module
        self.db = BppDb(db_file)
        self.db.create_connection()     # Also creates database if it doesn't exist yet
        # Initialise database in case of dump
        if dump_file:
            self.db.initialise_database()

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
