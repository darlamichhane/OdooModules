# -*- coding: utf-8 -*-

import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from odoo.tools import amount_to_text_en

from odoo.exceptions import UserError, RedirectWarning, ValidationError

import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _description = "Invoice"

    count = fields.Integer(string='Count', readonly=True)
    mode_of_payment = fields.Selection([
        ('cash', 'CASH'),
        ('cheque', 'CHEQUE'),
        ('credit', 'CREDIT'),
        ('other', 'OTHERS'),
        ], string='Mode of Payment',  readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always', default='cash')

    @api.multi
    def invoice_reprint(self):
        """ Print the duplicate invoice and add counter to the button, so that we can see more
            easily the next step of the workflow """
        self.ensure_one()
        self.count = self.count + 1
        return self.env['report'].get_action(self, 'abgroup_invoice.invoice_report_duplicate_main')

    @ api.multi
    def amount_to_text (self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='np', currency='Rupees')
        convert_amount_in_words = convert_amount_in_words.replace('and Zero Paisa', 'Only')
        return convert_amount_in_words
