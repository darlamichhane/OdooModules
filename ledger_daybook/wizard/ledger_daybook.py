
import time
from odoo import api, fields, models, _

from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import  timedelta, date, time
import datetime

import logging
_logger = logging.getLogger(__name__) 


class ReportLedgerDaybook(models.AbstractModel):
    _name = 'report.ledger_daybook.report_ledger_daybook'
    
    @api.model
    def render_html(self, ledgerids, data=None):
        self.model = self.env.context.get('active_model')
        ledgers = self.env[self.model].browse(self.env.context.get('active_id'))
        dt1 = datetime.datetime.strptime(ledgers.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(ledgers.date_to, "%Y-%m-%d").date()
        tm = datetime.time(23, 59, 59)
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        cur_account_id = str(ledgers.account_id.id)
        self._cr.execute("""SELECT 
                        aml.date, 
                        aa.code,
                        aa.name, 
                        COALESCE(SUM(aml.debit),0) AS debit, 
                        COALESCE(SUM(aml.credit),0) AS credit,
                        SUM(aml.debit - aml.credit) AS balance 
                        FROM 
                        account_move_line aml 
                        LEFT JOIN account_move am ON am.id = aml.move_id 
                        LEFT JOIN account_account aa ON aml.account_id = aa.id 
                        WHERE 
                        aml.account_id = %s 
                        AND aml.date >= %s 
                        AND aml.date <= %s 
                        AND am.state = 'posted'
                        GROUP BY 
                        aml.date, 
                        aa.name, 
                        aa.code
                        ORDER BY 
                        aml.date """, (cur_account_id, m_date_from, m_date_to,))
        result = self._cr.dictfetchall()
        
        # _logger.error('%s', result) 
        _logger.error('%s', cur_account_id) 
        
        ledgerargs = {
            'ledger_ids': self.ids,
            'ledger_model': self.model,
            'ledgers': ledgers,
            'time': time,
            'orders': result
        }
        return self.env['report'].render('ledger_daybook.report_ledger_daybook', ledgerargs)


class LedgerDaybookWizard(models.TransientModel):
    _name = "ledger.daybook.wizard"
    _description = "General Ledger Date"
    
    date_from = fields.Date(string='Start Date', required=True, default=date.today())
    date_to = fields.Date(string='End Date', required=True, default=date.today())
    account_id = fields.Many2one('account.account', string='Account', required=True)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'account_id' , 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'account_id' , 'date_to'])[0])
        return self.env['report'].get_action(self, 'ledger_daybook.report_ledger_daybook', data=data)

