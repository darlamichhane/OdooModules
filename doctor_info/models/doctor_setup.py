import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

from odoo.exceptions import UserError, RedirectWarning, ValidationError

import logging


class DoctorSetup(models.Model):
    _name = 'doctor.setup'

    name = fields.Char(string='Doctor Name')
    code = fields.Char(string='Doctor Code')
    address = fields.Char(string='Address')
    phone = fields.Char(string='Contact Number')
    profile = fields.Char(string='Doctor Profile')
    related_partner = fields.Many2one('res.partner', string='Related Partner')
    active = fields.Boolean(string="Active", default=True)
