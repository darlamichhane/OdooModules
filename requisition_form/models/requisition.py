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


class RequisitionForm(models.Model):
    _name = 'requisition.form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Requisition Form"
    _order = 'id desc'
    
    READONLY_STATES = {
        'requisition': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)]
    }
    
    def action_confirm(self):
        for rec in self:
            rec.state = 'requisition'
            if not rec.requisition_ids:
                raise UserError(_('Please create some requisition lines.'))
           
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('requisition.form.sequence') or _('New')
        result = super(RequisitionForm, self).create(vals)
        return result
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'requisition':
                raise UserError(_('The Requisition Order cannot be deleted in confirm state. Only draft state requisition order can be deleted'))
        return super(RequisitionForm, self).unlink()
    
    @api.depends('state')
    def _get_transferred(self):
        for form in self:
            if form.state in ('requisition'):
                form.transfer_status = 'to transfer'
                continue
            elif form.state in ('draft', 'cancel'):
                form.transfer_status = 'no'
            else:
                form.transfer_status = 'transferred'

    @api.onchange('job_card_no')
    def onchange_job_card_no(self):
        for rec in self:
            if rec.job_card_no:
                rec.vehicle_no = rec.job_card_no.vehicle_id.vehicle_no
                rec.model = rec.job_card_no.vehicle_id.name
                rec.engine_no = rec.job_card_no.vehicle_id.engine_no
                rec.chasis_no = rec.job_card_no.vehicle_id.chasis_no
                rec.customer_name = rec.job_card_no.customer_id.name

                  
    
    name = fields.Char(string="Requisition Form", required=True, copy=False, readonly=True, index=True,
                            default=lambda self:_('New'))
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.id)
    date_request = fields.Date('Request Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now)
    date_approve = fields.Date('Approve Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
        ('requisition', 'Requisition Order'),
        ], string='Status', readonly=True, default='draft', track_visibility='onchange')
    form_line = fields.One2many('requisition.form.line', 'requisition_id', string='Requisition Lines', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    notes = fields.Text(string="Notes")
    user_id = fields.Many2one('res.users', string='Store Keeper', track_visibility='onchange',
        readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user)
    requisition_ids = fields.One2many('requisition.form.line', 'requisition_id', string='Requisition Form Line', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    transfer_status = fields.Selection([
        ('no', 'Nothing to Transfer'),
        ('to transfer', 'Waiting Transfers'),
        ('transferred', 'Transferred'),
        ], string='Transfer Status', compute='_get_transferred', store=True, readonly=True, copy=False, default='no')
    vehicle_no = fields.Char(string='Vehicle No.', readonly=True, states={'draft': [('readonly', False)]}, copy=True, track_visibility='onchange')
    model = fields.Char(string='Model', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    customer_name = fields.Char(string='Customer Name', readonly=True, copy=True)
    engine_no = fields.Char(string='Engine No.', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    chasis_no = fields.Char(string='Chasis No.', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    job_card_no = fields.Many2one('job.order', string='JOB CARD NO.', readonly=True, states={'draft': [('readonly', False)]}, copy=True, required=1, track_visibility='onchange')


    @api.multi
    def print_requisition(self):
        return self.env["report"].get_action(self, 'requisition_form.report_requisition')


class RequisitionFormLine(models.Model):
    _name = 'requisition.form.line'
    _description = "Requisition Form Line"
    
    product_id = fields.Many2one(
        'product.product', 'Product', domain=[('type', 'in', ['product', 'consu'])], required=True, ondelete="cascade")
    requisition_id = fields.Many2one('requisition.form', string='Requisition ID')
    state = fields.Selection(related='requisition_id.state', store=True)
    company_id = fields.Many2one('res.company', related='requisition_id.company_id', string='Company', store=True, readonly=True)
    date_request = fields.Date(related='requisition_id.date_request', string='Request Date', readonly=True)
    product_uom_qty = fields.Float(string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0, required=True, states={'requisition': [('readonly', True)]})
    remarks = fields.Char(string='Remarks')
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=True, states={'done': [('readonly', True)]},
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")

    on_hand_stock = fields.Float(string="On Hand Stock", compute="_compute_on_hand_total")
    # remaining_stock = fields.Float(string="Remaining Stock", compute="_compute_on_hand_total")

    @api.depends('product_id', 'product_uom_qty')
    def _compute_on_hand_total(self):
        for record in self:
            if record.product_id and record.state != 'done':
                actual_qty = record.product_id.with_context(
                    {'location': record.location_id.id}).qty_available
                outgoing_qty = record.product_id.with_context(
                    {'location': record.location_id.id}).outgoing_qty
                record.on_hand_stock = actual_qty - outgoing_qty
                # record.remaining_stock = record.on_hand_stock - record.product_uom_qty
