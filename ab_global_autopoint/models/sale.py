from odoo import models, fields, api, _

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'


    transfer_id= fields.Many2one('stock.picking', string='Add Transfer ID', help='When selected, the associated transfer lines are added to the Sale Order Line.')

    @api.onchange('transfer_id')
    def onchange_workorder_id(self):
        for rec in self:
            lines=[]
            for line in self.transfer_id.move_lines:
                vals = {
                    'product_id': line.product_id,
                    'name': line.product_id.name,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_id.product_tmpl_id.uom_id,
                    'price_unit': line.product_id.product_tmpl_id.list_price
                    # 'order_id': line.id
                    # 'customer_lead': 0.0
                }
                lines.append((vals))
            rec.order_line = lines











