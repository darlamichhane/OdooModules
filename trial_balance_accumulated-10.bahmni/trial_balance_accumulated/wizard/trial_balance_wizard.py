# -*- coding: utf-8 -*-
# (C)opyright Aadarsha Shrestha, 2019. See LICENSE for full copyright and licensing details.

from odoo import models, fields

class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "trial.balance.report.wizard"

    is_accumulated_balance = fields.Boolean(string='Show Accumulated Balance', default=True)

    def _prepare_report_trial_balance(self):
        self.ensure_one()
        data = super(TrialBalanceReportWizard, self)._prepare_report_trial_balance()
        data['is_accumulated_balance'] = self.is_accumulated_balance
        return data

