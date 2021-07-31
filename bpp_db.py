from sqlite3 import connect, Error


class BppDb:
    """
    Class handling interactions between the application and its SQLite database.
    """

    def __init__(self, db_file):
        """
        Class is initialised by preparing a connection to a given database file.

        Args:
            db_file (str): Name (and location) of the database file
        """
        self.db_file = db_file
        self.connection = None

    def create_connection(self):
        """Try to connect to existing SQLite database."""
        try:
            self.connection = connect(self.db_file)
        except Error as e:
            print(e)
            raise

    def get_db_version(self):
        """Queries the version of the current database.

        Returns:
            str: Version of connected database.
        """
        cur = self.connection.cursor()
        # Version is contained in variable 'db_version' in the bpp_variables table. Query and return result.
        cur.execute("SELECT value FROM bpp_variables WHERE variable = 'db_version'")
        return cur.fetchone()[0]

    def create_table(self, create_table_sql):
        """ Create a table from the create_table_sql statement

        Args:
            create_table_sql (str): a CREATE TABLE statement

        Returns:
        """
        self.connection.cursor().execute(create_table_sql)

    def get_variable(self, variable):
        """ Retrieves value of a BPP+ specific variable.

        Args:
            variable (str): Name of variable to look for.

        Returns:
            str: Value of requested variable.
        """
        cur = self.connection.cursor()
        cur.execute(f"SELECT value FROM bpp_variables WHERE variable = '{variable}'")

        return cur.fetchone()[0]

    def replace_variable(self, variable, value):
        """Replace (add or change) BPP+ specific variable in table of variables.

        Args:
            variable (str): Name of variable to replace.
            value (str): Value to associate with variable.
        """
        sql = "REPLACE INTO bpp_variables (variable, value) VALUES ('{}', '{}')".\
            format(variable, value)
        self.connection.cursor().execute(sql)

    def insert_blueprint(self, bp, products, **kwargs):
        """
        Add a (new) blueprint to the blueprints table

        Args:
            bp (str): blueprint name
            products (str): name(s) of thing(s) produced by the blueprint
            **kwargs (any, optional): Values for additional columns, namely:
                source (str, optional): Where/how the blueprint can be obtained.
                tech (int, optional): Tech level.
                bp_cost (int, optional): Cost of the blueprint if bought.
                weight (int, optional): Weight of the blueprint itself.
                size (int, optional): Size of the blueprint itself
                max_uses (int, optional): Number of uses on one blueprint (if applicable).
                manhours (int, optional): Manhours required to build one product.
                max_workforce (int, optional): Maximum amount of workers who can be dedicated to production.
                init_credits (int, optional): Credits required to start building one product.
                init_materials (str, optional): Materials required to start building one product.
                init_materials_n (str, optional): Number of each material required to start building one product.
                init_materials_discount (str, optional): Whether or not initial materials receive bulk discounts.
                per_credits (int, optional): Credits required during building one product.
                per_materials (str, optional): Materials required during building one product.
                per_materials_n (str, optional): Number of each material required during building one product.
                per_materials_discount (str, optional): Whether or not periodic materials receive bulk discounts.
                products_n (str, optional): Number produced of each product.

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

    def initialise_database(self, dump_file):
        """
        Initialise database based on an exported SQLite database.

        Args:
            dump_file (str): Location of the exported SQLite database.

        """
        # Don't try to populate the database if there is no connection
        if self.connection is not None:
            # Read from given dump file
            with open(dump_file, 'r') as df:
                self.connection.cursor().executescript(df.read())
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

    def dump(self, dump_file):
        """
        Dumps database to specified file.

        Args:
            dump_file (str): Location of the file to dump the database to.
        """
        with open(dump_file, 'w') as df:
            for line in self.connection.iterdump():
                df.write(line + '\n')

    def close_connection(self):
        """ Close connection to current SQLite database. """
        if self.connection:
            self.connection.close()
