from odoo import api, fields, models, _


class PurchaseOrderInherited(models.Model):
    _inherit = 'purchase.order.line'
    
    unit_amount = fields.Float(string="Unit Amount", compute="_compute_unit_amount")
    
    @api.depends('product_qty', 'price_unit')
    def _compute_unit_amount(self):
         for record in self:
            record.unit_amount = record.product_qty * record.price_unit
            
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_subtotal': taxes['total_included'],
            })
