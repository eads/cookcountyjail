
import logging
from django.db.utils import DatabaseError

from countyapi.management.commands.utils import just_empty_lines, strip_the_lines, yesterday

log = logging.getLogger('main')


class Charges:

    def __init__(self, inmate, inmate_details):
        self._inmate = inmate
        self._inmate_details = inmate_details

    def save(self):
        """
        Stores the inmates charges if they are new or if they have been changes
        Charges: charges come on two lines. The first line is a citation and the
        # second is an optional description of the charges.
        """
        charges = strip_the_lines(self._inmate_details.charges().splitlines())
        if just_empty_lines(charges):
            return

        # Capture Charges and Citations if specified
        parsed_charges_citation = charges[0]
        parsed_charges = charges[1] if len(charges) > 1 else ''
        create_new_charge = True
        if len(self._inmate.charges_history.all()) != 0:
            inmate_latest_charge = self._inmate.charges_history.latest('date_seen')  # last known charge
            # if the last known charge is different than the current info then create a new charge
            if inmate_latest_charge.charges == parsed_charges and \
               inmate_latest_charge.charges_citation == parsed_charges_citation:
                create_new_charge = False
        if create_new_charge:
            try:
                new_charge = self._inmate.charges_history.create(charges=parsed_charges,
                                                                 charges_citation=parsed_charges_citation)
                new_charge.date_seen = yesterday()
                new_charge.save()
            except DatabaseError as e:
                log.debug("Could not save charges '%s' and citation '%s'\nException is %s" % (parsed_charges,
                                                                                              parsed_charges_citation,
                                                                                              str(e)))
