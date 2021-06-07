from sqlite3 import connect, Error


class BppDb:
    """
    Class handling interactions between the application and its SQLite database.
    """

    def __init__(self, db_file=None):
        """
        Class is initialised by preparing a connection to a given database file.

        Args:
            db_file (str, optional): Name (and location) of the database file
        """
        if db_file is None:
            self.db_file = 'bpp.db'

        self.connection = None

    def create_connection(self):
        """ Connect to existing SQLite database. """
        try:
            self.connection = connect(self.db_file)
        except Error as e:
            print(e)
            raise

    def check_db_version(self):
        """ Placeholder to check whether there is a new database available. """
        pass

    def create_table(self, create_table_sql):
        """ Create a table from the create_table_sql statement

        Args:
            create_table_sql (str): a CREATE TABLE statement

        Returns:
        """
        try:
            self.connection.cursor().execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_blueprint(self, bp, products, **kwargs):
        """
        Add a (new) blueprint to the blueprints table

        Args:
            bp (str): blueprint name
            products (str): name(s) of thing(s) produced by the blueprint
            **kwargs (any, optional): Values for additional columns, namely:
                source (str, optional):
                tech (int, optional):
                bp_cost (int, optional):
                weight (int, optional):
                size (int, optional):
                max_uses (int, optional):
                manhours (int, optional):
                max_workforce (int, optional):
                init_credits (int, optional):
                init_materials (str, optional):
                init_materials_n (str, optional):
                init_materials_discount (str, optional):
                per_credits (int, optional):
                per_materials (str, optional):
                per_materials_n (str, optional):
                per_materials_discount (str, optional):
                products_n (str, optional):

        Returns:
        """
        # Construct sql statement and corresponding values
        sql = """INSERT INTO blueprints(blueprint, tech, source, bp_cost, weight, size,
                                        max_uses, manhours, max_workforce,
                                        init_credits, init_materials, init_materials_n, init_materials_discount,
                                        per_credits, per_materials, per_materials_n, per_materials_discount,
                                        products, products_n)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        values = (bp,
                  kwargs['tech'] if 'tech' in kwargs.keys() else None,
                  kwargs['source'] if 'source' in kwargs.keys() else None,
                  kwargs['bp_cost'] if 'bp_cost' in kwargs.keys() else None,
                  kwargs['weight'] if 'weight' in kwargs.keys() else None,
                  kwargs['size'] if 'size' in kwargs.keys() else None,
                  kwargs['max_uses'] if 'max_uses' in kwargs.keys() else None,
                  kwargs['manhours'] if 'manhours' in kwargs.keys() else None,
                  kwargs['max_workforce'] if 'max_workforce' in kwargs.keys() else None,
                  kwargs['init_credits'] if 'init_credits' in kwargs.keys() else None,
                  kwargs['init_materials'] if 'init_materials' in kwargs.keys() else None,
                  kwargs['init_materials_n'] if 'init_materials_n' in kwargs.keys() else None,
                  kwargs['init_materials_discount'] if 'init_materials_discount' in kwargs.keys() else None,
                  kwargs['per_credits'] if 'per_credits' in kwargs.keys() else None,
                  kwargs['per_materials'] if 'per_materials' in kwargs.keys() else None,
                  kwargs['per_materials_n'] if 'per_materials_n' in kwargs.keys() else None,
                  kwargs['per_materials_discount'] if 'per_materials_discount' in kwargs.keys() else None,
                  products,
                  kwargs['products_n'] if 'products_n' in kwargs.keys() else None)

        # Execute and commit insert
        if self.connection is not None:
            self.connection.cursor().execute(sql, values)
            self.connection.commit()
        else:
            raise FileNotFoundError("Error! No database connection.")

    def initialise_database(self):
        """ Initialise database based on an exported SQLite database

        Returns:

        """
        # Create tables
        if self.connection is not None:
            # Create blueprints table
            self.create_table("""CREATE TABLE IF NOT EXISTS blueprints (
                                        blueprint text PRIMARY KEY,
                                        tech integer,
                                        source text,
                                        bp_cost integer,
                                        weight integer,
                                        size integer,
                                        max_uses integer,
                                        manhours integer,
                                        max_workforce integer,
                                        init_credits integer,
                                        init_materials text,
                                        init_materials_n text,
                                        init_materials_discount text,
                                        per_credits integer,
                                        per_materials text,
                                        per_materials_n text,
                                        per_materials_discount text,
                                        products text NOT NULL,
                                        products_n text
                                    );""")
            # Create factories table
            self.create_table("""CREATE TABLE IF NOT EXISTS factories (
                                        factory text PRIMARY KEY,
                                        tech integer,
                                        mobile bool NOT NULL,
                                        source text,
                                        factory_cost integer,
                                        weight integer,
                                        size integer,
                                        workers integer NOT NULL,
                                        credits integer,
                                        materials text,
                                        materials_n text,
                                        products text NOT NULL,
                                        products_n text
                                    );""")
            # Add two blueprints
            self.insert_blueprint(bp='Zombie Bunny Stop Fragment',
                                  products='Zombie Bunny Stop',
                                  products_n='1',
                                  tech=21,
                                  source='Easter',
                                  manhours=200000000,
                                  weight=100000,
                                  size=150,
                                  init_materials='[Metals, Zombie Bunny Stop Fragment]',
                                  init_materials_n='[25000, 4]',
                                  init_materials_discount='[Y, Y]',
                                  per_credits=5000000000)
            self.insert_blueprint(bp='Darkness Warmed Over Blueprint',
                                  products='Darkness Warmed Over',
                                  products_n='1',
                                  tech=21,
                                  source='Infernal Darkness, Dark Scorch',
                                  max_uses=1,
                                  manhours=500000000,
                                  weight=1000,
                                  size=1,
                                  init_credits=1500000000,
                                  init_materials="[Metals, Promethium, Dark Scorch's Remains]",
                                  init_materials_n='[1000, 50, 1]',
                                  init_materials_discount='[Y, Y, Y]',
                                  per_credits=1500000000,
                                  per_materials='[Metals, Dark Cell, Promethium, '
                                                'Dark Isotope, Dark Neutron Rod, Death Warmed Over]',
                                  per_materials_n='[100000, 10, 500, 10, 10, 2]',
                                  per_materials_discount='[Y, Y, Y, Y, Y, Y]')
        else:
            raise FileNotFoundError("Error! No database connection.")

    def get_all_blueprints(self):
        """ Query all blueprints from the blueprints table.

        Returns:
            A list of all blueprints in the database.
        """
        cur = self.connection.cursor()
        cur.execute("SELECT DISTINCT blueprint FROM blueprints")

        return [row[0] for row in cur.fetchall()]

    def find_blueprint(self, bp_name):
        """ Retrieves all information about a specified blueprint.

        Args:
            bp_name (str): Name of the blueprint to find.
        Returns:
            Complete results found for specified blueprint name.
        """
        cur = self.connection.cursor()
        cur.execute("SELECT * FROM blueprints WHERE blueprint = '" + bp_name + "'")
        # TODO handle situations with 0 or >1 results

        # Returns dictionary with column names as keys and corresponding values
        return dict(zip([desc[0] for desc in cur.description], cur.fetchone()))

    def close_connection(self):
        """ Close connection to current SQLite database. """
        if self.connection:
            self.connection.close()
