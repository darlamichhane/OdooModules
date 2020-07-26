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


class CreateTransitManifest(models.TransientModel):
    _name = 'transit.manifest'

    state = fields.Selection([('choose', 'choose'), ('get', 'get'), ('done', 'Done')],
                             default='get')
    number = fields.Char(string="Manifest", copy=False, readonly=True, index=True, track_visibility='onchange',
                         help='The name that will be used on account move lines')
    vehicle_id = fields.Many2one('vehicle.info', string='Vehicle Name', required=True,)
    driver_id = fields.Many2one('hr.employee', string='Driver Name', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    date_manifest = fields.Date('Manifest Date', required=True, index=True, copy=False,
                                default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    #invoice_id = fields.Many2one('account.invoice', string='Invoice', required=True)
    notes = fields.Text('Terms and Conditions')
    manifest_ids = fields.One2many('transit.manifest.line', 'manifest_id', string='Manifest Lines', copy=True)
    send_from = fields.Many2one('res.address.local', string='From', required=True)
    send_to = fields.Many2one('res.address.local', string='To', required=True)
    message = fields.Text('Message')

    @api.multi
    def create_transit_manifest(self):
        manifest_lines = [
                (0, 0, {
                    'name': self.manifest_ids.name,
                    'quantity': self.manifest_ids.quantity,
                    'vat_amount': self.manifest_ids.vat_amount,
                    'due_amount': self.manifest_ids.due_amount,
                    'topay_amount': self.manifest_ids.topay_amount,
                    'paid_amount': self.manifest_ids.vat_amount,
                    'invoice_id': self.manifest_ids.invoice_id.id,
                    'consignor_id': self.manifest_ids.consignor_id.id,
                    'consignee_id': self.manifest_ids.consignee_id.id,
                    'transit_id': self.manifest_ids.transit_id.id,
                    'address': self.manifest_ids.address,
                    'remarks': self.manifest_ids.remarks,
                })
        ]
        k = self.env['transport.manifest'].create({
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'send_from': self.send_from.id,
            'send_to': self.send_to.id,
            'notes': self.notes,
            'date_manifest': self.date_manifest,
            'manifest_line_ids': manifest_lines,  # this is one2many field to transport.manifest.line
        })
        k.action_confirm()

        self.write({'message': _("Transit Manifest Created Successfully")})
        self.write({'state': 'choose'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'transit.manifest',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }

class CreateTransportManifestLine(models.TransientModel):
    _name = 'transit.manifest.line'

    name = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Quantity'), required=True)
    uom_id = fields.Many2one('product.uom', string='Unit of Measure', ondelete='set null', index=True)
    vat_amount = fields.Float(string='Vat Amount', required=True, digits=dp.get_precision('Total Amount'))
    due_amount = fields.Float(string='Due Amount')
    topay_amount = fields.Float(string='ToPay Amount')
    paid_amount = fields.Float(string='Paid Amount')
    manifest_id = fields.Many2one('transit.manifest', string='Manifest Reference', ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='manifest_id.company_id', string='Company', store=True,
                                 readonly=True)
    consignor_id = fields.Many2one('res.partner', string='Consignor')
    consignee_id = fields.Many2one('res.partner', string='Consignee')
    invoice_id = fields.Many2one('account.invoice', string='Invoice', domain = [('type','=','out_invoice')],
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
