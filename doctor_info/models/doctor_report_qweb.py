# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import  timedelta,date,time
import datetime

class ReportDoctorate(models.AbstractModel):
    _name = 'report.doctor_info.report_doctor'
    
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        dt1 = datetime.datetime.strptime(docs.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(docs.date_to, "%Y-%m-%d").date()
        tm = datetime.time(23, 59, 59)
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        self._cr.execute("""select ail.doctor_id,ds.name as doc_name,sum(ail.price_subtotal),count(distinct(ai.partner_id)) from account_invoice_line ail 
            left join doctor_setup ds on ail.doctor_id = ds.id left join account_invoice ai on ail.invoice_id = ai.id  where ai.state in ('open','paid') and ai.date_invoice>=%s and ai.date_invoice<=%s 
            and ail.doctor_id is not null group by ds.name,ail.doctor_id order by ail.doctor_id""", (m_date_from,m_date_to,))
        result =  self._cr.dictfetchall()
        # inv_records = []
        # orders = self.env['account.invoice.line'].search([('user_id', '=', docs.salesperson_id.id)])
        # if docs.date_from and docs.date_to:
        #     for order in orders:
        #         if parse(docs.date_from) <= parse(order.date_order) and parse(docs.date_to) >= parse(order.date_order):
        #             sales_records.append(order);

        # else:
        #     raise UserError("Please enter duration")
        
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'orders': result
        }
        return self.env['report'].render('doctor_info.report_doctor', docargs)
