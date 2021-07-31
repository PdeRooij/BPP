from math import ceil


class KitSetup:
    """
    All logic for calculating kit setups.
    """

    def __init__(self, db):
        """
        Define characteristics for setup calculations.
        """
        # Retrieve calculation variables from database
        self.db = db    # Store database module
        self.ee_lvl_bonus = float(self.db.get_variable('exe_level_bonus'))
        self.rat_cons = float(self.db.get_variable('worker_ration_consumption'))

        # Some constants
        self.MINUTES_PER_DAY = 24 * 60
        self.COMMODS = ("metals", "nuclear waste", "silicon", "space oats", "baobabs")

        # Additional extractor info
        self.extractor_techs = (12, 14, 16, 18, 20)
        self.EXTRACTOR_STATS = {   # Fusion extractor rates by tech (per day)
            "metals": {"extraction_rate": {12: 21600, 14: 28080, 16: 34560, 18: 43200, 20: 51840}},
            "nuclear waste": {"extraction_rate": {12: 6480, 14: 8424, 16: 10386, 18: 12960, 20: 15552}},
            "silicon": {"extraction_rate": {12: 21600, 14: 28080, 16: 34560, 18: 43200, 20: 51840}},
            "space oats": {"extraction_rate": {12: 21600, 14: 28080, 16: 34560, 18: 43200, 20: 51840}},
            "baobabs": {"extraction_rate": {12: 21600, 14: 28080, 16: 34560, 18: 43200, 20: 51840}}
        }
        self.FACTORY_STATS = {
            "metals": {"name": "Steel Foundry", "conversion_rate": 1000},
            "nuclear waste": {"name": "Star Bottling Plant", "conversion_rate": 300},
            "silicon": {"name": "Sentient Machine Learning Institute", "conversion_rate": 500},
            "space oats": {"name": "Giant Space Still", "conversion_rate": 350},
            "baobabs": {"name": "Figurine Workshop", "conversion_rate": 250},
        }
        for commod in self.COMMODS:
            self.EXTRACTOR_STATS[commod]["workers_to_equip"] = 1     # All extractors take 1 worker to equip
            self.FACTORY_STATS[commod]["workers_to_equip"] = 100     # All factories take 100 workers to equip
        self.FACTORY_STATS["silicon"]["workers_to_equip"] = 50       # Except silicon

    def rations_per_hour(self, num_workers):
        """
        Calculates the amount of rations consumed per hour by a given amount of workers.

        Args:
            num_workers (int): Number of workers on a kit.

        Returns:
            int: Rations consumed per hour (rounded up) by the workers on a kit.
        """
        return ceil(num_workers * self.rat_cons)

    def hydros_needed(self, num_workers):
        """
        Calculates number of hydroponics required to support the given number of workers.

        Args:
            num_workers (int): Amount of workers that need to be supported by hydroponics.

        Returns:
            int: Number of hydroponics required to support the given number of workers.
        """
        # Each Hydro produces 360 oats per hour,
        # MRE turns 2 oats into 1 ration,
        # each worker consumes 0.6 rations per hour
        return ceil(self.rations_per_hour(num_workers) * 2 / 360)

    def mres_needed(self, num_workers):
        """
        Calculates number of MRE factories required to support the given number of workers.

        Args:
            num_workers (int): Amount of workers that need to be supported by MRE factories.

        Returns:
            int: Number of MRE factories required to support the given number of workers.
        """
        # Each MRE produces 300 rations per hour, while each worker consumes 0.6 rations per hour
        return ceil(self.rations_per_hour(num_workers) / 300)

    def mre_creds_per_day(self, num_mres):
        """
        Calculates the amount of credits a given number of MRE factories consume per day.

        Args:
            num_mres (int): Number of MRE factories to calculate credit consumption for.

        Returns:
            int: Total amount of credits consumed by given MRE factories per day.
        """
        # Each MRE consumes 5 credits every 12 seconds (1/5 min.)
        return num_mres * 5 * self.MINUTES_PER_DAY * 60 / 12

    def best_extractor_tech(self, base_tech):
        """
        Determines what the best extractor tech is for a given kit level.

        Args:
            base_tech (int): Kit tech level for which setup is being calculated.

        Returns:
            int: Highest extractor tech level that can be equipped on the kit.
        """
        best_tech = None
        # Loop through available extractor techs until it exceeds kit tech
        for tech in self.extractor_techs:
            if tech > base_tech:
                break
            best_tech = tech

        return best_tech

    def calculate_workforce(self, extractors, factories):
        """
        Calculates how many workers a kit needs, based on equipped extractors and factories.

        Args:
            extractors (dict): Dictionary with number of extractors for each commodity.
            factories (dict): Dictionary with number of IC factories for each commodity.

        Returns:
            tuple: (Workers needed, hydroponics needed, MRE factories needed)
        """
        # Include initial workforce (for shield, trading bay etc.)
        workers = 40
        # Add workers needed to equip given extractors and factories
        for commod in self.COMMODS:
            workers += self.EXTRACTOR_STATS[commod]["workers_to_equip"] * extractors.get(commod, 0)
            workers += self.FACTORY_STATS[commod]["workers_to_equip"] * factories.get(commod, 0)

        # Add workers for hydros and MREs until stable
        hydros = 0
        mres = 1
        workers += hydros + mres
        h_new = self.hydros_needed(workers)
        mre_new = self.mres_needed(workers)
        while [hydros, mres] != [h_new, mre_new]:
            # Not stable yet, calculate new workforce
            hydros = h_new
            mres = mre_new
            workers += hydros + mres
            h_new = self.hydros_needed(workers)
            mre_new = self.mres_needed(workers)

        # Return total amount of workers, hydroponics and MRE factories required for the kit
        return workers, hydros, mres

    def factories_needed(self, extractor_tech, ee=30, slots=None):
        """
        Calculate the number of IC factories required, given extractor tech level,
        Extraction Expert level and available extraction slots.

        Args:
            extractor_tech (int): Tech level of equipped extractors.
            ee (int): Extraction Expert level of character holding the kit.
            slots (dict): Dictionary with available slots per commodity.

        Returns:
            dict: Dictionary of IC factories required per commodity to convert all extracted resources.
        """
        if slots is None:
            slots = {}

        factories = {}
        for commod in self.COMMODS:
            if slots.get(commod, 0) > 0:
                commods_per_min = slots[commod]\
                                  * self.EXTRACTOR_STATS[commod]["extraction_rate"][extractor_tech]\
                                  * (1 + self.ee_lvl_bonus * ee)\
                                  / self.MINUTES_PER_DAY
                factories[commod] = ceil(commods_per_min / self.FACTORY_STATS[commod]["conversion_rate"])

        return factories

    def exe_base_setup(self, base_tech, ee_level=30, metals=0, nukes=0, silicon=0, oats=0, baobabs=0):
        slots = {}
        if metals > 0:
            slots["metals"] = metals
        if nukes > 0:
            slots["nuclear waste"] = nukes
        if silicon > 0:
            slots["silicon"] = silicon
        if oats > 0:
            slots["space oats"] = oats
        if baobabs > 0:
            slots["baobabs"] = baobabs

        tech = self.best_extractor_tech(base_tech)
        if tech is None:
            return "Base tech is too low!"

        factories = self.factories_needed(tech, ee_level, slots)
        workers, hydros, mres = self.calculate_workforce(slots, factories)

        # Construct result string
        res = "Workforce:\n"
        res += f"  Workers: {workers}\n"
        res += f"  Hydros: {hydros}\n"
        res += f"  MREs: {mres}\n"
        res += f"  Credits/month: {self.mre_creds_per_day(mres) * 30 / 1000000 :.1f}m\n"
        res += "Factories:\n"

        lines = []
        for commod in slots:
            lines.append(f"  {self.FACTORY_STATS[commod]['name']}: {factories[commod]}")
        res += "\n".join(sorted(lines)) + '\n'
        res += f"Extractors (tech {tech}):\n"
        lines = []
        for commod in slots:
            lines.append(f"  {commod.capitalize()}: {slots[commod]}")
        res += "\n".join(sorted(lines))
        return res
