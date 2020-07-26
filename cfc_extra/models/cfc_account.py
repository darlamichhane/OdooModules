from odoo import models, fields, api, _
 

class AccountJournalInherited(models.Model):
    _inherit = 'account.journal'
 
    type = fields.Selection(selection_add=[('voucher', 'Voucher')])


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'
    
    def _get_default_journal(self):
        return self.env['account.journal'].search([('name', 'ilike', 'Voucher')])[0].id

    journal_id = fields.Many2one('account.journal', domain=[('type', '=', 'voucher')], default=_get_default_journal)
    
