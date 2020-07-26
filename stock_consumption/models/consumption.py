# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _

from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import  timedelta, date, time
import datetime


class ReportStockConsumption(models.AbstractModel):
    _name = 'report.stock_consumption.report_stock_consumption'
    
    @api.model
    def render_html(self, consumptionids, data=None):
        self.model = self.env.context.get('active_model')
        consumptions = self.env[self.model].browse(self.env.context.get('active_id'))
        dt1 = datetime.datetime.strptime(consumptions.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(consumptions.date_to, "%Y-%m-%d").date()
        tm = datetime.time(23, 59, 59)
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        self._cr.execute("""SELECT sl.name department, SUM(aml.debit - aml.credit) amount FROM account_move am LEFT JOIN account_move_line aml ON am.id = aml.move_id 
                        LEFT JOIN product_product pp LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id ON aml.product_id = pp.id 
                        LEFT JOIN product_category pc ON pc.id = pt.categ_id LEFT JOIN stock_picking sp ON sp.name = aml.ref LEFT JOIN stock_location sl 
                        ON sl.id = sp.location_dest_id LEFT JOIN account_account aa ON aa.id = aml.account_id WHERE am.date >= %s AND am.date <= %s 
                        AND aa.code between '41111' and '41160' OR aa.code between '42211' and '42220' GROUP BY sl.name""", (m_date_from, m_date_to,))
        result = self._cr.dictfetchall()
        
        consumptionargs = {
            'consumption_ids': self.ids,
            'consumption_model': self.model,
            'consumptions': consumptions,
            'time': time,
            'orders': result
        }
        return self.env['report'].render('stock_consumption.report_stock_consumption', consumptionargs)


class StockConsumptionReportWizard(models.TransientModel):
    _name = "stock.consumption.wizard"
    _description = "Stock Consumption Wizard"

    date_from = fields.Date(string='Start Date', required=True, default=date.today())
    date_to = fields.Date(string='End Date', required=True, default=date.today())

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'stock_consumption.report_stock_consumption', data=data)
