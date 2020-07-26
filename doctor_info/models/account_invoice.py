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

class AccountInvoiceInherited(models.Model):
    _inherit = 'account.invoice'


    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        self.user_id = self.env.user
        return to_open_invoices.invoice_validate()

class AccountInvoiceLineInherited(models.Model):
    _inherit = 'account.invoice.line'

    
    doctor_id = fields.Many2one('doctor.setup',string='Doctor', required=True)
    # tax_exem = 

