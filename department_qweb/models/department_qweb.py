# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import  timedelta, date, time
import datetime


class ReportDepartment(models.AbstractModel):
    _name = 'report.department_qweb.report_department'
    
    @api.model
    def render_html(self, departmentids, data=None):
        self.model = self.env.context.get('active_model')
        departments = self.env[self.model].browse(self.env.context.get('active_id'))
        dt1 = datetime.datetime.strptime(departments.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(departments.date_to, "%Y-%m-%d").date()
        tm = datetime.time(23, 59, 59)
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        self._cr.execute("""with dep_total AS (SELECT * from (SELECT pc.name, ail.price_subtotal,ai.date_invoice FROM account_invoice_line ail LEFT JOIN 
                        account_invoice ai ON ail.invoice_id = ai.id  LEFT JOIN product_product pp LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id 
                        ON ail.product_id = pp.id LEFT JOIN product_category pc ON pc.id = pt.categ_id WHERE ail.product_id NOT IN (2060,2052) AND ai.state IN ('open','paid') AND 
                        ai.type = 'out_invoice' UNION ALL SELECT pc.name department_name, - ail.price_subtotal,ai.date_invoice FROM account_invoice_line ail 
                        LEFT JOIN account_invoice ai ON ail.invoice_id = ai.id  LEFT JOIN product_product pp LEFT JOIN product_template pt ON 
                        pt.id = pp.product_tmpl_id ON ail.product_id = pp.id LEFT JOIN product_category pc ON pc.id = pt.categ_id WHERE ail.product_id NOT IN (2060,2052) AND 
                        ai.state IN ('open','paid') AND ai.type = 'out_refund')b where date_invoice>=%s and date_invoice<=%s) 
                        SELECT name,price_subtotal,ord FROM (SELECT name, SUM(price_subtotal)price_subtotal,0 ord 
                        FROM dep_total GROUP BY name UNION ALL SELECT 'TOTAL',sum(price_subtotal),1 FROM dep_total) AS a order by ord, name""", (m_date_from, m_date_to,))
        result = self._cr.dictfetchall()
        
        departmentargs = {
            'department_ids': self.ids,
            'department_model': self.model,
            'departments': departments,
            'time': time,
            'orders': result
        }
        return self.env['report'].render('department_qweb.report_department', departmentargs)
