# -*- coding: utf-8 -*-
# (C)opyright Aadarsha Shrestha, 2019. See LICENSE for full copyright and licensing details.

from odoo.addons.account_financial_report_qweb.report.trial_balance_xlsx import TrialBalanceXslx
from odoo.report import report_sxw

class TrialBalanceXslx(TrialBalanceXslx):
    
    def _get_report_columns(self, report):
        res = super(TrialBalanceXslx, self)._get_report_columns(report)
        if report.is_accumulated_balance:
            for key, value in res.items():
                if value['field'] in ['period_balance', 'final_balance']:
                    del res[key]
        return res

    def _generate_report_content(self, workbook, report):
        super(TrialBalanceXslx, self)._generate_report_content(workbook, report)
        if report.is_accumulated_balance and not report.show_partner_details:
            self.write_ending_balance(report)

    def write_ending_balance(self, report):
        self.sheet.merge_range(self.row_pos, 0, self.row_pos, 2, 'Total', self.format_header_left)
        self.sheet.write_number(
                        self.row_pos, 3, sum(report.account_ids.mapped('debit')),
                        self.format_header_amount
                    )
        self.sheet.write_number(
                        self.row_pos, 4, sum(report.account_ids.mapped('credit')),
                        self.format_header_amount
                    )


TrialBalanceXslx(
    'report.trial_balance_accumulated.report_trial_balance_xlsx',
    'report_trial_balance_qweb',
    parser=report_sxw.rml_parse
)
