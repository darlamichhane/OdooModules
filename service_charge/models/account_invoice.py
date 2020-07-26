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


TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Vendor Refund
}

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _description = "Invoice"

    @api.multi
    def get_taxes_values(self):
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        if self.type in ['out_invoice', 'out_refund']:
            service_charge_amount = self.company_id.service_charge_amount
            service_charge_tax = (service_charge_amount * (13 / 100.0))
            for key, value in tax_grouped.items():
                value['amount'] += service_charge_tax
                value['base'] += service_charge_amount
        # tax_grouped['3-31-False'] = {
        #             'amount': 7.15,
        #             'base': 55.0,
        #             'name': u'Service Charge VAT',
        #             'sequence': 1,
        #             'account_analytic_id': False,
        #             'invoice_id': ,
        #             'manual': False,
        #             'account_id': 31,
        #             'tax_id': 3
        # }
        return tax_grouped

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id',
                 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.service_charge_amount = self.company_id.service_charge_amount
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)

        if self.type in ('out_invoice', 'out_refund'):
            self.amount_total = self.amount_untaxed + self.amount_tax + self.service_charge_amount
        else:
            self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    service_charge_amount = fields.Monetary(string="ST Charge Amount", compute='_compute_amount', readonly=True, store=True)
    service_charge_tax = fields.Monetary(compute='_compute_amount', string='ST Charge Tax')

    @api.multi
    def action_move_create(self):
        #This method is overriden to pass the Discount Journal Entry.
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv._get_currency_rate_date()
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            #=============Customized code starts=========
            if inv.type in ['out_invoice', 'out_refund']:
                if inv.type == 'out_invoice':
                    move_line = move.line_ids.filtered(lambda l: l.name == '/')
                    move_line.debit += inv.service_charge_amount
                    move_line_vals = {
                        'name': 'Stationery Charge',
                        'company_id': move.company_id.id,
                        'account_id': move.company_id.service_charge_account.id,
                        'credit': inv.service_charge_amount,
                        'date_maturity': date,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id,
                        'partner_id': move_line.partner_id.id,
                        'move_id': move.id,
                    }
                    self.env['account.move.line'].create(move_line_vals)
                else:
                    move_line = move.line_ids.filtered(lambda l: l.name == inv.name)
                    move_line.credit += inv.service_charge_amount
                    move_line_vals = {
                        'name': 'Stationery Charge',
                        'company_id': move.company_id.id,
                        'account_id': move.company_id.service_charge_account.id,
                        'debit': inv.service_charge_amount,
                        'date_maturity': date,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id,
                        'partner_id': move_line.partner_id.id,
                        'move_id': move.id,
                    }
                    self.env['account.move.line'].create(move_line_vals)
            #===========Customized code ends=============
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True
