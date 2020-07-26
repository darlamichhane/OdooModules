# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _

from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import  timedelta, date, time
import datetime

import logging
_logger = logging.getLogger(__name__) 


class ReportGeneralLedger(models.AbstractModel):
    _name = 'report.general_ledger.report_general_ledger'
    
    @api.model
    def render_html(self, ledgerids, data=None):
        self.model = self.env.context.get('active_model')
        ledgers = self.env[self.model].browse(self.env.context.get('active_id'))
        dt1 = datetime.datetime.strptime(ledgers.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(ledgers.date_to, "%Y-%m-%d").date()
        tm = datetime.time(23, 59, 59)
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        cur_group_id = str(ledgers.group_id.id)
        self._cr.execute("""SELECT DISTINCT
                    aml.date,
                    aa.name, 
                    COALESCE(aml.debit,0) AS debit, 
                    COALESCE(aml.credit,0) AS credit,
                    rp.name parnter_name, 
                    am.name move_name,
                    aml.ref
                    FROM account_move_line aml 
                    LEFT JOIN account_move am ON am.id = aml.move_id
                    LEFT JOIN account_account aa ON aml.account_id = aa.id
                    LEFT JOIN account_group ag ON ag.parent_id = aa.group_id 
                    LEFT JOIN res_partner rp ON rp.id = aml.partner_id 
                    WHERE 
                    aa.group_id = %s
                    AND aml.date >= %s 
                    AND aml.date <= %s """, (cur_group_id, m_date_from, m_date_to,))
        result = self._cr.dictfetchall()
        
        _logger.error('%s', result) 
        _logger.error('%s', cur_group_id) 
        
        ledgerargs = {
            'ledger_ids': self.ids,
            'ledger_model': self.model,
            'ledgers': ledgers,
            'time': time,
            'orders': result
        }
        return self.env['report'].render('general_ledger.report_general_ledger', ledgerargs)


class GeneralLedgerReportWizard(models.TransientModel):
    _name = "general.ledger.wizard"
    _description = "General Ledger Date"
    
    date_from = fields.Date(string='Start Date', required=True, default=date.today())
    date_to = fields.Date(string='End Date', required=True, default=date.today())
    group_id = fields.Many2one('account.group', string='Account Group', required=True)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'group_id' , 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'group_id' , 'date_to'])[0])
        return self.env['report'].get_action(self, 'general_ledger.report_general_ledger', data=data)
