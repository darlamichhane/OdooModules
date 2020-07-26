# -*- coding: utf-8 -*-
from datetime import datetime, date

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

            
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    consignor_id = fields.Many2one('res.partner', string='Consignor', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    consignee_id = fields.Many2one('res.partner', string='Consignee', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    send_from = fields.Many2one('res.address.local', string='From', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    send_to = fields.Many2one('res.address.local', string='To', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
    document_type = fields.Selection([
        ('bill', 'बिल'),
        ('nikasi bill', 'निकासी बिल'),
        ('pragyapan patra', 'प्रज्ञापन पत्र'),
        ('chalan', 'चलान'),
        ('dr note', 'DR नोट'),
        ('cr note', 'CR नोट'),
        ('others', 'Others'),
        ], string='Document Type', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always', default='bill')
    custom_office_id = fields.Many2one('custom.office', string='Custom Office', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                       track_visibility='always')
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
        ('paid', 'Paid')
        ], readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, track_visibility='always', default='due')
    topay_company_id = fields.Many2one('res.company', 'Company')

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'consignor_id': self.consignor_id.id,
            'consignee_id': self.consignee_id.id,
            'document_type': self.document_type,
            'custom_office_id': self.custom_office_id.id,
            'send_from': self.send_from.id,
            'send_to': self.send_to.id,
            'bill_no': self.bill_no,
            'bill_amount': self.bill_amount,
            'load_type': self.load_type,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'pay_status': self.pay_status,
            'topay_company_id': self.topay_company_id.id,
            'service_charge_account': self.company_id.service_charge_account.id,
            'service_charge_amount': self.company_id.service_charge_amount,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    item_lines = fields.Integer(compute='get_number', store=True)

    @api.multi
    @api.depends('order_id')
    def get_number(self):
        for order in self.mapped('order_id'):
            item_lines = 1
            for line in order.order_line:
                line.item_lines = item_lines
                item_lines += 1
            max_item = 5
            if item_lines > max_item + 1:
                raise UserError((
                    'Maximum Product line allowed is 5 items only..'))
