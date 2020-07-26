from odoo import models, fields, api, _


class AccountInvoiceConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "account.invoice.reprint"
    _description = "Update the selected invoices print sent from true to false "

    @api.multi
    def invoice_reprint(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            record.sent = False
        return {'type': 'ir.actions.act_window_close'}
