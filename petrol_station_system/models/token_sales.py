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

import odoo.addons.decimal_precision as dp


class TokenSales(models.Model):
    _name = 'token.sales'
    _description = "Token Sales"
    _rec_name = 'receipt_id'

    @api.onchange('partner_id')
    def onchange_partner(self):
        res = {
            'domain': {
                'number': [('partner_id', '=', self.partner_id.id), ('status', '=', 'available')],
                'ref_number': [('partner_id', '=', self.partner_id.id), ('state', '=', 'done')],
            }
        }
        return res

    name = fields.Char(string="Sales Receipt Name:")
    receipt_id = fields.Char(string="Sales Receipt No", copy=False, readonly=True, index=True, track_visibility='onchange',
                             help='The no that will be used on credit token sales and claim lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Confirmed'),
        ('done', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='draft', track_visibility='onchange')
    sales_status = fields.Selection([
        ('no', 'Nothing to Order'),
        ('to order', 'Waiting Order'),
        ('ordered', 'Order Received'),
    ], string='Sales Status', compute='_get_claim', store=True, readonly=True, copy=False, default='no')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, domain=[('customer', '=', 'true')])
    company_id = fields.Many2one('res.company', 'Company', store=True, track_visibility='onchange', copy=False,
                                 index=True, default=lambda self: self.env.user.company_id.id)
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              readonly=True, states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user)
    ref_number = fields.Many2one('token.management', string='Ref Number',)
    number = fields.Many2one('token.management.line', string='Token Number', ondelete='restrict', copy=False, track_visibility='onchange', domain=[('status', '=', 'available')],)
    claim_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    token_sales_ids = fields.One2many('token.sales.line', 'sales_id', string='Token Line', copy=True)
    vehicle_no = fields.Many2one('vehicle.info', string='Vehicle No',)
    message = fields.Text('Message')
    status = fields.Many2one('token.management.line', string='Status')
    agreement_id = fields.Many2one('token.management', String='Agreement', ondelete='restrict')
    sales_mode = fields.Selection([
        ('token', 'Token'),
        ('credit', 'Credit'),
        ], string='Sales Type', track_visibility='always', default='token')
    sale_remarks = fields.Char(string= 'Remarks', change_default=True, index=True, track_visibility='always')

    @api.model
    def create(self, vals):
        if vals.get('receipt_id', _('New')) == _('New'):
            vals['receipt_id'] = self.env['ir.sequence'].next_by_code('token.sales.sequence') or _('New')
        result = super(TokenSales, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(
                    'Sales Receipt cannot be deleted in confirm state. Only draft state Token can be deleted'))
        return super(TokenSales, self).unlink()

    def action_approved(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def action_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
                    easily the next step of the workflow """
        self.ensure_one()
        return self.env['report'].get_action(self, 'petrol_station_system.report_token_receipt')

    @api.depends('state')
    def _get_claim(self):
        for order in self:
            if order.state in ('draft'):
                order.sales_status = 'no'
                continue
            if order.state in ('open', 'done'):
                order.sales_status = 'to order'
            else:
                order.sales_status

    @api.multi
    def confirm_button(self):
        for rec in self:
            rec.state = 'done'
        for lines in self.token_sales_ids:
            tok_obj = self.env['token.management.line'].search([('id', '=', lines.number.id)])
            if not lines.number:
                return
            else:
                tok_obj.status = 'sold'

    # Load single Available Token
    @api.onchange('number')
    def onchange_number(self):

        for rec in self:
            lines = []

            vals = {
                'number': self.number.id,
                'status': self.number.status,
            }

            lines.append((vals))
            rec.token_sales_ids = lines

class TokenSalesLine(models.Model):
    _name = 'token.sales.line'
    _description = "Token Sales Line"
    _rec_name = 'number'

    name = fields.Char(string='Token Number')
    number = fields.Many2one('token.management.line', string='Token Number', readonly=True, ondelete='restrict', store=True, index=True, copy=False, track_visibility='onchange',)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', string='UoM', ondelete='set null', index=True, store=True,)
    order_qty = fields.Float(string='Ordered Qty', digits=dp.get_precision('Unit of Measure'), required=True)
    product_qty = fields.Float(string='Delivered Qty', digits=dp.get_precision('Unit of Measure'),
                             required=True)
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'), store=True, required=True)
    price_total = fields.Float(string='Amount(without Tax)', store=True, help="Total amount without taxes")
    sales_id = fields.Many2one('token.sales', string='Token Sales Reference', ondelete='cascade', index=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 related='sales_id.partner_id', store=True, readonly=True, related_sudo=False)
    unit_amount = fields.Char(string="Unit Amount")



    @api.onchange('order_qty')
    def _onchange_order_qty(self):
        if self.order_qty:
            self.product_qty = self.order_qty


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

            if not self.product_id:
                return {}
            for rec in self:
                rec.price_unit = rec.product_id.product_tmpl_id.list_price
                rec._update_price_with_quantity()

    @api.onchange('product_qty')
    def _update_price_with_quantity(self):
        self.price_total = self.product_id.product_tmpl_id.list_price * self.order_qty
