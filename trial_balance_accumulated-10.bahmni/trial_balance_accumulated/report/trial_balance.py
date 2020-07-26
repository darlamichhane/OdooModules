# -*- coding: utf-8 -*-
# (C)opyright Aadarsha Shrestha, 2019. See LICENSE for full copyright and licensing details.

from odoo import models, api, fields

class TrialBalance(models.TransientModel):
    _inherit = 'report_trial_balance_qweb'

    is_accumulated_balance = fields.Boolean('Show Accumulated Balance', default=True)

    @api.multi
    def print_report(self, report_type):
        self.ensure_one()
        if report_type == 'xlsx':
            report_name = 'trial_balance_accumulated.' \
                          'report_trial_balance_xlsx'
        else:
            report_name = 'account_financial_report_qweb.' \
                          'report_trial_balance_qweb'
        return self.env['report'].get_action(docids=self.ids,
                                             report_name=report_name)


    @api.multi
    def compute_data_for_report(self):
        super(TrialBalance, self).compute_data_for_report()

        if self.is_accumulated_balance:
            for account in self.account_ids:
                if account.period_balance >= 0:
                    account.debit = abs(account.period_balance)
                    account.credit = 0.0
                else:
                    account.debit = 0.0
                    account.credit = abs(account.period_balance)
