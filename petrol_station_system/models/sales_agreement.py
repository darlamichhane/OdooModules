# -*- coding: utf-8 -*-
##############################################################################
import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from odoo.tools import amount_to_text_en
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo import models, fields, api, _

import odoo.addons.decimal_precision as dp


class Agreement(models.Model):
    _name = 'agreement'
    _description = "Sale Agreement"
    _order = 'id desc'
    _rec_name = 'code'

    name = fields.Char(required=True)
    code = fields.Char(copy=False, readonly=True, index=True, track_visibility='onchange')
    origin = fields.Char(string='Source Document')
    active = fields.Boolean(default=True)
    signature_date = fields.Datetime(string='Signature Date', required=True, index=True, copy=False,
                               default=fields.Datetime.now)
    amount_deposit = fields.Float(string='Deposited Amount', digits=dp.get_precision('Product Price'), required=True)
    date_end = fields.Date(string='Agreement Deadline', index=True, copy=False)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    description = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Confirmed'),
        ('done', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='draft', track_visibility='onchange')
    agreement_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    ], string='Type', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True,
        domain=[('parent_id', '=', False)])
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'agreement'))

    out_invoice_ids = fields.One2many(
        'account.invoice', 'agreement_id', string='Customer Invoices',
        readonly=True, domain=[('type', 'in', ('out_invoice', 'out_refund'))])
    in_invoice_ids = fields.One2many(
        'account.invoice', 'agreement_id', string='Supplier Invoices',
        readonly=True, domain=[('type', 'in', ('in_invoice', 'in_refund'))])
    sale_ids = fields.One2many(
        'sale.order', 'agreement_id', string='Sale Orders', readonly=True,
        domain=[('state', 'not in', ('draft', 'sent', 'cancel'))])
    agreement_line_ids = fields.One2many('sale.agreement.line', 'agreement_id', string='Agreement Lines', copy=True, track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('sale.agreement.sequence') or _('New')
        result = super(Agreement, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('The Sales Agreement Order cannot be deleted in confirm state. Only draft state Agreement order can be deleted'))
        return super(Agreement, self).unlink()

    @api.multi
    def print_agreement(self):
        self.ensure_one()
        self.sent = True
        return self.env["report"].get_action(self, 'petrol_station_system.report_salesagreement')

    @api.multi
    def action_confirm(self):
        if not all(obj.agreement_line_ids for obj in self):
            raise UserError(_('You cannot confirm because there is no Agreement order line.'))
        self.write({'state': 'open'})

    def action_approved(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.code:
                name = u'[%s] %s' % (agr.code, agr.name)
            res.append((agr.id, name))
        return res

    _sql_constraints = [(
        'code_partner_company_unique',
        'unique(code, partner_id, company_id)',
        'This agreement code already exists for this partner!'
    )]

class SaleAgreementLine(models.Model):
    _name = 'sale.agreement.line'
    _description = "Sale Agreement Line"
    _order = 'id'
    _rec_name = 'product_id'

    name = fields.Char(string='Description')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Expected Qty', digits=dp.get_precision('Unit of Measure'),
                                default=0.0)
    agreement_id = fields.Many2one('agreement', string='Agreement Reference', ondelete='cascade', index=True)
    uom_id = fields.Many2one('product.uom', string='UoM', store=True, ondelete='set null', track_visibility='onchange')
    qty_ordered = fields.Float(string='Ordered Qty', track_visibility='onchange')
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'), store=True, track_visibility='onchange')
    price_total = fields.Float(string='Amount(without Tax)', store=True, help="Total amount without taxes", track_visibility='onchange')
    order_id = fields.Many2one('sale.order', string='Purchase Agreement', ondelete='cascade', track_visibility='onchange', index=True)
    unit_amount = fields.Char(string="Unit Amount")

    @api.multi
    @api.onchange('unit_amount')
    def _compute_unit_amount(self):
        if self.unit_amount:
            self.qty_ordered = float(self.unit_amount) / float(self.price_unit)
            self.product_qty = float(self.unit_amount) / float(self.price_unit)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.product_qty = 1.0

            if not self.product_id:
                return {}
            for rec in self:
                rec.price_unit = rec.product_id.product_tmpl_id.list_price
                rec._update_price_with_quantity()

    @api.onchange('product_qty')
    def _update_price_with_quantity(self):
        self.price_total = self.product_id.product_tmpl_id.list_price * self.product_qty
        # rec._update_price_with_quantity()


    # @api.onchange('product_id')1.00
    # def _load_product_attributes(self):
    #     if not self.product_id:
    #         return {}
    #     for rec in self:
    #         rec.product_price = rec.product_id.product_tmpl_id.list_price
    #         rec._update_price_with_quantity()
    #
    # @api.onchange('product_qty')
    # def _update_price_with_quantity(self):
    #     self.product_price = self.product_id.product_tmpl_id.list_price * self.product_qty