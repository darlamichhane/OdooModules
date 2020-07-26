from odoo import models, fields

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'


    vehicle_no = fields.Many2one('vehicle.info', string="Vehicle Number", required=True)
    owner_name = fields.Many2one('res.partner',  string='Vehicle Owner Name', required=True)
    agreement_id = fields.Many2one('agreement', string='Agreement No')



