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


class TokenManagement(models.Model):
    _name = 'token.management'
    _description = "Token Management"
    _rec_name = 'ref_number'

    name = fields.Char(string="Token Name")
    ref_number = fields.Char(string="Ref Number", copy=False, readonly=True, index=True, track_visibility='onchange',
                         help='The name that will be used on token lines and claim limes')

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, domain=[('customer', '=', 'true')])
    company_id = fields.Many2one('res.company', 'Company', store=True, track_visibility='onchange', copy=False, index=True, default=lambda self: self.env.user.company_id.id)
    user_id = fields.Many2one('res.users', string='User', track_visibility='onchange',
                              readonly=True, states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user)
    token_date = fields.Date('Token Issue Date', required=True, index=True, copy=False, default=fields.Datetime.now)
    quantity = fields.Integer('Token Quantity', required=True)
    sent = fields.Boolean(readonly=True, default=False, copy=False,
                          help="It indicates that the Token has been sent.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Confirmed'),
        ('done', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='draft', track_visibility='onchange')
    token_line_ids = fields.One2many('token.management.line', 'token_id', string='Token Lines', copy=True, readonly=True)
    template = fields.Selection(
        selection=[
            ('petrol.station.system.report_token', 'Label (A4: 4 pcs on sheet, 2x4)')],
        string='Token Template',
        default='petrol.station.system.report_token')
    qty_per_token = fields.Integer(
        string='Label quantity per product',
        default=1, readonly= True,
    )
    agreement_id = fields.Many2one(
        'agreement', string='Agreement', ondelete='restrict', required=True, track_visibility='onchange', domain=[('state', '=', 'done')])


    @api.model
    def create(self, vals):
        if vals.get('ref_number', _('New')) == _('New'):
            vals['ref_number'] = self.env['ir.sequence'].next_by_code('token.ref.number.sequence') or _('New')
        result = super(TokenManagement, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(
                    'Token cannot be deleted in confirm state. Only draft state Token can be deleted'))
        return super(TokenManagement, self).unlink()

    # @api.multi
    # def action_confirm(self):
    #     if not all(obj.token_line_ids for obj in self):
    #         raise UserError(_('You cannot confirm because there is no token line.'))
    #     self.write({'state': 'open'})

    def action_approved(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.company_id = self.partner_id.company_id

    @api.multi
    def action_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
                    easily the next step of the workflow """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'petrol_station_system.report_token')

    @api.multi
    def action_restore_initial_qty(self):
        self.ensure_one()
        for token in self.token_line_ids:
            if token.qty_initial:
                token.update({'qty': token.qty_initial})

    @api.multi
    def action_set_qty(self):
        self.ensure_one()
        self.token_line_ids.write({'qty': self.qty_per_token})

    @api.multi
    def show_lines_token(self):
        TokenManagement = self.env['token.management.line']

        common_vals = {

                'company_id': self.company_id.id,
                'status': 'available',
                'token_id': self.id,
            }
        for number in range(self.quantity):
                vals = dict(common_vals, quantity=number)
                TokenManagement.create(vals)

                action = self.env.ref('petrol_station_system.token_management_action')
        self.write({'state': 'open'})
        return {
            'name': _(action.name),
            'type': action.type,
            'res_model': 'token.management',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'current',

            }


class TokenManagementLine(models.Model):
    _name = 'token.management.line'
    _description = "Token Management Line"
    _rec_name = 'number'

    number = fields.Char(string='Token Number', copy=False, readonly=True, track_visibility='onchange' ,default=lambda self: self.env['ir.sequence'].next_by_code('token.number'))
    status = fields.Selection(
        [('available', 'Available'), ('sold', 'Sold'), ('lost', 'Lost'),
        ('stolen', 'Stolen'), ('cancelled', 'Cancelled'),],
        'Status', required=True, default='available', track_visibility='onchange')
    token_id = fields.Many2one('token.management', string='Token Number', ondelete='cascade', index=True)
    selected = fields.Boolean(string='Select', compute='_compute_selected')
    qty_initial = fields.Integer('Initial Qty', default=1)
    qty = fields.Integer('Label Qty', default=1, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 related='token_id.partner_id', store=True, readonly=True, related_sudo=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 related='token_id.company_id', store=True, readonly=True, related_sudo=False)

    @api.depends('qty')
    def _compute_selected(self):
        for record in self:
            if record.qty > 0:
                record.update({'selected': True})
            else:
                record.update({'selected': False})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.status != 'cancelled':
                raise UserError(_(
                    'Token cannot be deleted in confirm state. Only draft state Token can be deleted'))
        return super(TokenManagement, self).unlink()

    _sql_constraints = [(
        'number_partner_unique',
        'unique(number, partner_id)',
        'This Token code already exists for this partner!'
    )]








