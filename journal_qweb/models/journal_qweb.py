# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import  timedelta, date, time
import datetime


class ReportJournal(models.AbstractModel):
    _name = 'report.journal_qweb.report_journal'
    
    @api.model
    def render_html(self, journalids, data=None):
        self.model = self.env.context.get('active_model')
        journals = self.env[self.model].browse(self.env.context.get('active_id'))
        dt1 = datetime.datetime.strptime(journals.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(journals.date_to, "%Y-%m-%d").date()
        tm = datetime.time(23, 59, 59)
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        self._cr.execute("""with journal AS(SELECT * FROM(
                    SELECT aa.name, aml.debit, aml.credit,aml.date FROM account_move_line aml INNER JOIN account_account aa 
                    ON aml.account_id = aa.id WHERE aa.id in (7,17,27,30,31))b WHERE date>=%s AND date<=%s) SELECT name,debit,credit,ord FROM 
                    (SELECT name,SUM(debit) debit,SUM(credit) credit,0 ord FROM journal GROUP BY name UNION ALL 
                    SELECT 'TOTAL', SUM(debit),SUM(credit),1 FROM journal)a ORDER BY ord,name""", (m_date_from, m_date_to,))
        result = self._cr.dictfetchall()
        
        journalargs = {
            'journal_ids': self.ids,
            'journal_model': self.model,
            'journals': journals,
            'time': time,
            'orders': result
        }
        return self.env['report'].render('journal_qweb.report_journal', journalargs)
