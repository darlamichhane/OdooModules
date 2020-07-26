# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import  timedelta, date, time
import datetime


class ReportSalesperson(models.AbstractModel):
    _name = 'report.salesperson_qweb.report_salesperson'
    
    @api.model
    def render_html(self, salespersonids, data=None):
        self.model = self.env.context.get('active_model')
        salespersons = self.env[self.model].browse(self.env.context.get('active_id'))
        dt1 = datetime.datetime.strptime(salespersons.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(salespersons.date_to, "%Y-%m-%d").date()
        tm = datetime.time(23, 59, 59)
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        self._cr.execute("""with calc_amount AS( SELECT * FROM (
                        SELECT ai.number,rp.name,ai.user_id, ai.amount_total, ai.date_invoice FROM account_invoice ai LEFT JOIN res_users ru ON ru.id = ai.user_id
                        LEFT JOIN res_partner rp ON rp.id = ru.partner_id where ai.state IN ('open','paid') AND ai.type = 'out_invoice' UNION ALL SELECT ai.origin,
                        rp.name,ai.user_id, - ai.amount_total, ai.date_invoice FROM account_invoice ai LEFT JOIN res_users ru ON ru.id = ai.user_id LEFT JOIN res_partner rp 
                        ON rp.id = ru.partner_id WHERE ai.state IN ('open','paid') AND ai.type = 'out_refund')b where date_invoice>=%s and date_invoice<=%s) 
                        SELECT name,amount_total,ord FROM (SELECT name,sum(amount_total)amount_total,0 ord FROM calc_amount group by name, user_id UNION ALL select 'TOTAL',sum(amount_total),1 
                        FROM calc_amount)as a order by ord,name""", (m_date_from, m_date_to,))
        result = self._cr.dictfetchall()
        
        salespersonargs = {
            'salesperson_ids': self.ids,
            'salesperson_model': self.model,
            'salespersons': salespersons,
            'time': time,
            'orders': result,
        }
        return self.env['report'].render('salesperson_qweb.report_salesperson', salespersonargs)
