# -*- coding: utf-8 -*-

from odoo import api, models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'note': ui_order.get('note'),
        })
        return res
