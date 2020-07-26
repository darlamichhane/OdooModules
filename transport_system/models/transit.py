# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class Transit(models.Model):
    _name = "transit"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Transit"

    name = fields.Char(string='Transit')
    code = fields.Char(string='Code')
    # from_number = fields.Integer(string='From Number', compute="set_from_number")

    # @api.depends("from_number")
    # def set_from_number(self):
    #     last_numberf = self.env['transit'].search([], limit=1, order='from_number desc')
    #     for rec in self:
    #         rec.from_number = rec.last_number + 1