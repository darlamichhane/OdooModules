# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _default_service_charge_account(self):
        return self.env.user.company_id.service_charge_account

    def _default_service_charge_amount(self):
        return self.env.user.company_id.service_charge_amount

    service_charge = fields.Boolean(string='Allow ST charge to invoice amount', help="Allow ST charge to invoice amount")
    service_charge_account = fields.Many2one('account.account', string='ST charge Account', related='company_id.service_charge_account', default=lambda self: self._default_service_charge_account())
    service_charge_amount = fields.Monetary(string='ST charge Amount', related='company_id.service_charge_amount', default=lambda self: self._default_service_charge_amount())
