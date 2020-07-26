from odoo import api, fields, models, _

from datetime import  timedelta,date,time
import datetime
class JournalReportWizard(models.TransientModel):
    _name = "journal.wizard"
    _description = "Journal Wizard"


    date_from = fields.Date(string='Start Date', required=True,default=date.today())
    date_to = fields.Date(string='End Date', required=True,default=date.today())

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'journal_qweb.report_journal', data=data)