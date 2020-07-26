# -*- coding: utf-8 -*-
##############################################################################
import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from odoo.tools import amount_to_text_en
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner(self):
        res = {
            'domain': {
                'receipt_id': [('partner_id', '=', self.partner_id.id), ('sales_status', '=', 'to order')],

            }
        }
        return res

    name = fields.Char(string='Sales Receipt No')
    agreement_id = fields.Many2one(
        'agreement', string='Agreement', ondelete='restrict',
        track_visibility='onchange', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    receipt_id = fields.Many2one('token.sales', string="Sales Receipt No")
    source = fields.Char(string='Source Document')

    # @api.onchange('receipt_id')
    # def _onchange_receipt_id(self):
    #     if self.receipt_id:
    #             self.source = self.receipt_id

    # @api.onchange('order_line')
    # def _onchange_receipt(self):
    #     receipt_ids = self.order_line.mapped('receipt_id')
    #     if receipt_ids:
    #         self.source = ', '.join(receipt_ids.mapped('receipt_id'))

    # @api.onchange('invoice_line_ids')
    # def _onchange_origin(self):
    #     purchase_ids = self.invoice_line_ids.mapped('purchase_id')
    #     if purchase_ids:
    #         self.origin = ', '.join(purchase_ids.mapped('name'))

    @api.multi
    def action_confirm(self):
        for res in self:
            res.state = 'sale'

        for rec in self:
            sale_obj = self.env['token.sales'].search([('id', '=', self.receipt_id.id)])
            if rec.receipt_id:
                sale_obj.sales_status = 'ordered'


    # @api.onchange('invoice_line_ids')
    # def _onchange_origin(self):
    #     purchase_ids = self.invoice_line_ids.mapped('purchase_id')
    #     if purchase_ids:
    #         self.origin = ', '.join(purchase_ids.mapped('name'))

    #Load all sold Token lines

    @api.onchange('receipt_id')
    def onchange_receipt_id(self):
        if not self.receipt_id:
            return {}

        new_lines = self.env['sale.order.line']
        for line in self.receipt_id.token_sales_ids:
            data = {
                    'product_id': line.product_id,
                    'name': line.product_id.name,
                    'product_uom_qty': line.order_qty,
                    'product_uom': line.product_id.product_tmpl_id.uom_id,
                    'price_unit': line.product_id.product_tmpl_id.list_price,
            }
            new_line = new_lines.new(data)
            new_lines += new_line

        self.order_line += new_lines
        self.receipt_number = False
        return {}


    def _prepare_invoice(self):
            vals = super(SaleOrder, self)._prepare_invoice()
            vals['agreement_id'] = self.agreement_id.id or False
            return vals

    # @api.multi
    # def _prepare_invoice(self):
    #     """
    #     Prepare the dict of values to create the new invoice for a sales order. This method may be
    #     overridden to implement custom invoice generation (making sure to call super() to establish
    #     a clean extension chain).
    #     """
    #     self.ensure_one()
    #     journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
    #     if not journal_id:
    #         raise UserError(_('Please define an accounting sale journal for this company.'))
    #     invoice_vals = {
    #         'name': self.client_order_ref or '',
    #         'origin': self.name,
    #         'type': 'out_invoice',
    #         'account_id': self.partner_invoice_id.property_account_receivable_id.id,
    #         'partner_id': self.partner_invoice_id.id,
    #         'partner_shipping_id': self.partner_shipping_id.id,
    #         'journal_id': journal_id,
    #         'currency_id': self.pricelist_id.currency_id.id,
    #         'comment': self.note,
    #         'payment_term_id': self.payment_term_id.id,
    #         'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
    #         'company_id': self.company_id.id,
    #         'user_id': self.user_id and self.user_id.id,
    #         'team_id': self.team_id.id
    #     }
    #     return invoice_vals

        # # Load all sold Token lines
        # @api.onchange('number')
        # def number_change(self):
        #     if not self.number:
        #         return {}
        #
        #     new_lines = self.env['token.claim.line']
        #     for line in self.number:
        #         data = {
        #                 'number': line.number,
        #                 'status': line.status,
        #                 'claim_id': self.id,
        #             }
        #         new_line = new_lines.new(data)
        #         new_lines += new_line
        #
        #     # self.token_claim_ids += new_lines
        #     self.number = False
        #     return {}

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    unit_amount = fields.Char(string="Unit Amount")
    sales_id = fields.Many2one('token.sales', string='Token Sales')
    receipt_id = fields.Many2one('token.sales.line', string="Sales Receipt No")

    @api.multi
    @api.onchange('unit_amount')
    def _compute_unit_amount(self):
        if self.unit_amount:
            self.product_uom_qty = float(self.unit_amount) / float(self.price_unit)


    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.project_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res
