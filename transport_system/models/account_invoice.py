# -*- coding: utf-8 -*-

import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from odoo.tools import amount_to_text_en
import num2words

from odoo.exceptions import UserError, RedirectWarning, ValidationError

import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Vendor Refund
}

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _description = "Invoice"

    topay_company_id = fields.Many2one('res.company', 'Company')
    consignor_id = fields.Many2one('res.partner', string='Consignor', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always')
    consignee_id = fields.Many2one('res.partner', string='Consignee', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always')
    send_from = fields.Many2one('res.address.local', string='From', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always')
    send_to = fields.Many2one('res.address.local', string='To', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},  track_visibility='always')
    document_type = fields.Selection([
        ('bill', 'बिल'),
        ('nikasi bill', 'निकासी बिल'),
        ('pragyapan patra', 'प्रज्ञापन पत्र'),
        ('chalan', 'चलान'),
        ('dr note', 'DR नोट'),
        ('cr note', 'CR नोट'),
        ('others', 'Others'),
        ], string='Document Type', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always', default='bill')
    custom_office_id = fields.Many2one('custom.office', string='Custom Office', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},  track_visibility='always')
    manifest_status = fields.Selection([
        ('no', 'Nothing to Manifest'),
        ('to manifest', 'Waiting Manifests'),
        ('manifested', 'Manifests Done'),
        ('transit', 'Transit'),
        ], string='Manifest Status', compute='_get_manifest', store=True, readonly=True, copy=False, default='no')
    count = fields.Integer(string='Count', readonly=True)
    bill_no = fields.Char(string='Bill No.', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    bill_amount = fields.Char(string='Bill Amount', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    load_type = fields.Selection([
        ('full', 'Full Trip'),
        ('half', 'Half Trip'),
        ], string='Load Type', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always', default='half')
    vehicle_id = fields.Many2one('vehicle.info', string='Vehicle No', readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                 track_visibility='always')
    driver_id = fields.Many2one('hr.employee', string='Driver Name', readonly=True,
                                states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                track_visibility='always')
    pay_status = fields.Selection([
        ('due', 'Dues'),
        ('to_pay', 'To Pay'),
        ('paid', 'Paid'),
        ], string='Pay Status', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always', default='due')

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'transport_system.tax_invoice_template_report_id')

    @api.multi
    def tax_invoice_reprint(self):
        """ Print the duplicate invoice and add counter to the button, so that we can see more
            easily the next step of the workflow """
        self.ensure_one()
        self.count = self.count + 1
        return self.env['report'].get_action(self, 'transport_system.tax_invoice_report_duplicate_main')

    @api.depends('state')
    def _get_manifest(self):
        for order in self:
            if order.state in ('draft') and order.type in ('out_invoice'):
                order.manifest_status = 'no'
                continue
            if order.state in ('open', 'paid') and order.type in ('out_invoice'):
                order.manifest_status = 'to manifest'
            else:
                order.manifest_status

    @api.multi
    def action_invoice_paid(self):
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
            raise UserError(_('Invoice must be validated in order to set it to register payment.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        return to_pay_invoices.write({'state': 'paid',
                                      'pay_status': 'paid'})


    # @api.depends('state')
    # def _get_pay_status(self):
    #     for order in self:
    #         if order.state in ('paid') and order.type in ('out_invoice'):
    #             order.write({'pay_status': 'paid'})

    @ api.multi
    def amount_to_text (self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='np', currency='Rupees')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Paisa', 'Only') # Ugh
        return convert_amount_in_words

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new refund from the invoice.
            This method may be overridden to implement custom
            refund generation (making sure to call super() to establish
            a clean extension chain).
            :param record invoice: invoice to refund
            :param string date_invoice: refund creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the refund from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the refund
        """
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids)
        tax_lines = invoice.tax_line_ids
        taxes_to_change = {
            line.tax_id.id: line.tax_id.refund_account_id.id
            for line in tax_lines.filtered(lambda l: l.tax_id.refund_account_id != l.tax_id.account_id)
        }
        cleaned_tax_lines = self._refund_cleanup_lines(tax_lines)
        values['tax_line_ids'] = self._refund_tax_lines_account_change(cleaned_tax_lines, taxes_to_change)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['payment_term_id'] = False
        values['refund_invoice_id'] = invoice.id
        #=============Customized code starts=========
        values['consignor_id'] = invoice.consignor_id.id
        values['consignee_id'] = invoice.consignee_id.id
        values['send_from'] = invoice.send_from.id
        values['send_to'] = invoice.send_to.id
        values['document_type'] = invoice.document_type
        values['custom_office_id'] = invoice.custom_office_id.id
        values['manifest_status'] = invoice.manifest_status
        values['bill_no'] = invoice.bill_no
        values['bill_amount'] = invoice.bill_amount
        values['load_type'] = invoice.load_type
        values['vehicle_id'] = invoice.vehicle_id.id
        values['driver_id'] = invoice.driver_id.id
        #===========Customized code ends=============

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    _description = "Invoice Line"

    consignor_id = fields.Many2one('res.partner', string='Consignor',
        related='invoice_id.consignor_id', store=True, readonly=True, related_sudo=False)
    consignee_id = fields.Many2one('res.partner', string='Consignee',
                                   related='invoice_id.consignee_id', store=True, readonly=True, related_sudo=False)
