from odoo import fields, models, api, _


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'
    
    invoices_count = fields.Integer(string="Sales", compute="get_invoices_count")
  
    @api.multi
    def open_account_invoice_lines(self):
        return {
            'name': _('Account Invoice Lines'),
            'domain': [('product_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'account.invoice.line',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            }
    
    def get_invoices_count(self):
        # cur_product_id = self.product_id.id
        report = self.env['account.invoice.line']
        count = report.search_count([('product_id', '=', self.id)])
        self.invoices_count = count
