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
    _inherit = 'account.invoice'
    _description = "Invoice"

    agreement_id = fields.Many2one(
        'agreement', string='Agreement', ondelete='restrict',
        readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='onchange')

    count = fields.Integer(string='Count', readonly=True)
    mode_of_payment = fields.Selection([
        ('cash', 'CASH'),
        ('cheque', 'CHEQUE'),
        ('credit', 'CREDIT'),
        ('other', 'OTHERS'),
        ],
        string='Mode of Payment', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        track_visibility='always', default='cash')

    @api.multi
    def invoice_reprint(self):
        """ Print the duplicate invoice and add counter to the button, so that we can see more
            easily the next step of the workflow """
        self.ensure_one()
        self.count = self.count + 1
        return self.env['report'].get_action(self, 'petrol_station_system.invoice_report_duplicate_main')

    @api.multi
    def invoice_print(self):
        """ Print the duplicate invoice and add counter to the button, so that we can see more
            easily the next step of the workflow """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'petrol_station_system.invoice_template_report_id')

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='np', currency='Rupees')
        convert_amount_in_words = convert_amount_in_words.replace('and Zero Paisa', 'Only')
        return convert_amount_in_words

    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if invoice.agreement_id:
            values['agreement_id'] = invoice.agreement_id.id
        return values

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _description = "Invoice Line"

    price_without_vat = fields.Float(string="Price Without Tax", compute="_compute_unit_amount", store=True)
    # source = fields.Char(string='Source', help="Reference of the document that generated this sales order request.")

    @api.depends('quantity', 'price_subtotal')
    def _compute_unit_amount(self):
        for record in self:
            record.price_without_vat = float(record.price_subtotal) / float(record.quantity)


