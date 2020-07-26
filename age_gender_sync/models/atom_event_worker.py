# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import json
import uuid
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AtomEventWorkerInherit(models.Model):
    _inherit = 'atom.event.worker'
    
    def _get_customer_vals(self, vals):
        res = {}
        res.update({'ref': vals.get('ref'),
                    'name': vals.get('name'),
                    'gender': vals.get('gender'),
                    'birthdate': vals.get('birthdate'),
                    'local_name': vals.get('local_name'),
                    'uuid': vals.get('uuid')})
        address_data = vals.get('preferredAddress')
        # get validated address details
        address_details = self._get_address_details(json.loads(address_data))
        # update address details
        res.update(address_details)
        # update other details : for now there is only scope of updating contact.
        if vals.get('primaryContact'):
            res.update({'phone': vals['primaryContact']})
        return res
 
