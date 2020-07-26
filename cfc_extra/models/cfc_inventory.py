from odoo import api, fields, models, _


class StockMoveInherited(models.Model):
    _inherit = 'stock.move'
    
    on_hand_stock = fields.Float(string="On Hand Stock", compute="_compute_on_hand_total")
    
    @api.depends('product_id', 'product_uom_qty')
    def _compute_on_hand_total(self):
         for record in self:
            if record.product_id and record.state != 'done':
                actual_qty = record.product_id.with_context(
                    {'location': record.location_id.id}).qty_available
                outgoing_qty = record.product_id.with_context(
                    {'location': record.location_id.id}).outgoing_qty
                record.on_hand_stock = actual_qty - outgoing_qty


class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'
    
    received_by = fields.Char(string="Received By")
   
