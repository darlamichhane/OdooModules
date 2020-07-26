# -*- coding: utf-8 -*-

import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang

from odoo.exceptions import UserError, RedirectWarning, ValidationError

import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class CustomOffice(models.Model):
    _name = "custom.office"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Custom Office"

    name = fields.Char(string='Custom Office Name')
    code = fields.Char(string='Code')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s (%s)' % (rec.name, rec.code)))
        return res

