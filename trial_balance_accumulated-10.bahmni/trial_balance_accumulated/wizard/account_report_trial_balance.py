# -*- coding: utf-8 -*-
# (C)opyright Aadarsha Shrestha, 2019. See LICENSE for full copyright and licensing details.

from odoo import models, fields

class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'

    is_accumulated_balance = fields.Boolean(string='Show Accumulated Balance', default=True)

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form']['is_accumulated_balance'] = self.is_accumulated_balance
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'account.report_trialbalance', data=data)
