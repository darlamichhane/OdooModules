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


class TransportManifest(models.Model):
    _name = "transport.manifest"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Transport Manifest"
    _order = 'id desc'
    _rec_name = 'number'

    number = fields.Char(string="Manifest", copy=False, readonly=True, index=True, track_visibility='onchange',
                         help='The name that will be used on account move lines')
    vehicle_id = fields.Many2one('vehicle.info', string='Vehicle Name', readonly=True, required=True,
                                 states={'draft': [('readonly', False)]}, change_default=True, index=True, track_visibility='always')
    driver_id = fields.Many2one('hr.employee', string='Driver Name', readonly=True, required=True,
                                states={'draft': [('readonly', False)]}, change_default=True, index=True, track_visibility='always')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    date_manifest = fields.Date('Manifest Date', states={'draft': [('readonly', False)]}, change_default=True, readonly=True, required=True, index=True, copy=False,
                               default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user)
    notes = fields.Text('Terms and Conditions')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
        ('manifest', 'Manifest Order'),
        ], string='Status', readonly=True, default='draft', track_visibility='onchange')
    manifest_line_ids = fields.One2many('transport.manifest.line','manifest_id', string='Manifest Lines',
                                        readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    send_from = fields.Many2one('res.address.local', string='From', readonly=True, states={'draft': [('readonly', False)]}, required=True,
                                change_default=True, index=True, track_visibility='always')
    send_to = fields.Many2one('res.address.local', string='To', readonly=True, states={'draft': [('readonly', False)]}, required=True,
                              change_default=True, index=True, track_visibility='always')


    @api.multi
    def print_manifest(self):
        return self.env["report"].get_action(self, 'transport_system.report_manifest')

    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('transport.manifest.sequence') or _('New')
        result = super(TransportManifest, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'manifest':
                raise UserError(_('The Manifest Order cannot be deleted in confirm state. Only draft state Manifest order can be deleted'))
        return super(TransportManifest, self).unlink()

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.state = 'manifest'

        for lines in self.manifest_line_ids:
            inv_obj = self.env['account.invoice'].search([('id', '=', lines.invoice_id.id)])
            if not lines.transit_id:
                inv_obj.manifest_status = 'manifested'
            else:
                inv_obj.manifest_status = 'transit'
            #_logger.error('%s', inv_obj)
            #_logger.error('%s', lines)

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class TransportManifestLine(models.Model):
    _name = 'transport.manifest.line'
    _description = "Transport Manifest Line"
    _order = 'id'

    name = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Quantity'), required=True)
    uom_id = fields.Many2one('product.uom', string='Unit of Measure', ondelete='set null', index=True)
    vat_amount = fields.Float(string='Vat Amount', required=True, digits=dp.get_precision('Total Amount'))
    due_amount = fields.Float(string='Due Amount')
    topay_amount = fields.Float(string='ToPay Amount')
    paid_amount = fields.Float(string='Paid Amount')
    manifest_id = fields.Many2one('transport.manifest', string='Manifest Reference', ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='manifest_id.company_id', string='Company', store=True,
                                 readonly=True)
    consignor_id = fields.Many2one('res.partner', string='Consignor')
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    invoice_id = fields.Many2one('account.invoice', string='Invoice', domain = [('type','=','out_invoice'),('manifest_status', '=', 'to manifest')],
                                 help='Encoding help. When selected, the associated Invoice lines are added to the Manifest. Several Manifest Number can be selected.')
    address = fields.Char(string='Address')
    remarks = fields.Char(string='Remarks')
    transit_id = fields.Many2one('transit', string='Transit')

    @api.onchange('invoice_id')
    def _load_manifest_line(self):
        if not self.invoice_id:
            return {}
        for rec in self:
            rec.consignor_id = rec.invoice_id.consignor_id.id
            rec.consignee_id = rec.invoice_id.consignee_id.id
            rec.vat_amount = rec.invoice_id.amount_total
            if rec.invoice_id.pay_status == 'due':
                rec.due_amount = rec.invoice_id.amount_total
            elif rec.invoice_id.pay_status == 'to_pay':
                rec.topay_amount = rec.invoice_id.amount_total
            elif rec.invoice_id.pay_status == 'paid':
                rec.paid_amount = rec.invoice_id.amount_total
            rec.address = rec.invoice_id.consignee_id.street_name

    @api.onchange('invoice_id')
    def _onchange_name(self):
        manifest_ids = self.invoice_id.invoice_line_ids.mapped('invoice_id.invoice_line_ids')
        if manifest_ids:
            self.name = ', '.join(manifest_ids.mapped('name'))
            self.quantity = sum(manifest_ids.mapped('quantity'))
        #_logger.error('%s', manifest_ids)

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        domain = {}
        if not self.manifest_id:
            return
        part = self.manifest_id.vehicle_id
        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a Vehicle and Driver!'),
                }
            return {'warning': warning}
