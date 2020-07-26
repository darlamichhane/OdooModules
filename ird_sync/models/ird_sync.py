# -*- coding: utf-8 -*-
from odoo import fields, models, api

class IrdSync(models.Model):
    _inherit = 'account.invoice'
    
    sync_with_ird = fields.Boolean(string='Sync with IRD', default=False)
    is_realtime = fields.Boolean(string='Is Realtime', default=True)
    