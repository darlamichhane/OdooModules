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

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            service_charge_amount = self.env['ir.values'].get_default('account.config.settings', 'service_charge_amount')
            service_charge_tax = (service_charge_amount * (13 / 100.0))
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':

                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    service_charge_tax = (service_charge_amount * (13 / 100.0))
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax

            amount_total = amount_untaxed + amount_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax) + service_charge_tax,
                'amount_total': amount_total + service_charge_amount + service_charge_tax,
                'service_charge_amount': service_charge_amount,
            })

    service_charge_amount = fields.Monetary(string="ST Charge Amount", compute='_amount_all', readonly=True, store=True)
    service_charge_tax = fields.Monetary(compute='_amount_all', string='ST Charge Tax')
