# -*- coding: utf-8 -*-
import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import  timedelta, date, time
import datetime
from odoo.http import request
import re
import logging

_logger = logging.getLogger(__name__)


class StockConsumptionReport(models.TransientModel):
    _name = "stock.consumption.report"
    
    stock_data = fields.Char('Name',)
    file_name = fields.Binary('Stock Consumption Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
   
    location_dest_id = fields.Many2one('stock.location', string='Department', domain=[('usage', '=', 'inventory')])
    date_from = fields.Date('Start Date', required='True', default=date.today())
    date_to = fields.Date('End date', required='True', default=date.today())

    @api.multi
    def action_stock_report(self):
        
        tm = datetime.time(23, 59, 59)
        dt1 = datetime.datetime.strptime(self.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(self.date_to, "%Y-%m-%d").date()
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        workbook = xlwt.Workbook()
        format0 = xlwt.easyxf('font:height 500,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        format1 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
        
        format3 = xlwt.easyxf('align: horiz left')
        format4 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
       
        sheet = workbook.add_sheet("Stock_Consumption_Report", cell_overwrite_ok=True)
        sheet.col(0).width = int(15 * 260)
        sheet.col(1).width = int(20 * 260)    
        sheet.col(2).width = int(25 * 260)    
        sheet.col(3).width = int(28 * 260) 
        sheet.col(4).width = int(19 * 260)   
        sheet.col(5).width = int(10 * 260)
        sheet.col(6).width = int(12 * 260)
        sheet.col(7).width = int(10 * 260)
        sheet.col(8).width = int(10 * 260)
        sheet.col(9).width = int(15 * 260)   
        sheet.col(10).width = int(30 * 260)
        sheet.col(11).width = int(30 * 260)   
        sheet.write_merge(0, 1, 0, 6, 'Stock Consumption Report', format0)
        sheet.write(3, 0, str("Date From" + ":"), format1)
        sheet.write(3, 1, str(self.date_from), format1)
        sheet.write(4, 0, str("Date Upto"), format1)
        sheet.write(4, 1, str(self.date_to), format1)
        
        sheet.write(6, 0, "Date", format1)
        sheet.write(6, 1, "Issue Number", format1)
        sheet.write(6, 2, "Department", format1)
        sheet.write(6, 3, "Product Category", format1)
        sheet.write(6, 4, "Product", format1)
        sheet.write(6, 5, "Quantity", format1)
        sheet.write(6, 6, "Amount", format1)
    
        if self.location_dest_id:
            curdest_id = self.location_dest_id.id
            self._cr.execute("""SELECT am.date, sp.location_dest_id, sl.name consumption, pc.name category, pt.name product,aml.quantity, aml.debit, aml.credit, am.ref FROM account_move am 
            LEFT JOIN account_move_line aml ON am.id = aml.move_id LEFT JOIN product_product pp Left join product_template pt 
            ON pt.id = pp.product_tmpl_id ON aml.product_id = pp.id LEFT JOIN product_category pc ON pc.id = pt.categ_id LEFT JOIN
            stock_picking sp ON sp.name = aml.ref LEFT JOIN stock_location sl ON sl.id = sp.location_dest_id LEFT JOIN account_account aa ON aa.id = aml.account_id where 
            am.date >= %s and am.date <= %s and sp.location_dest_id = %s AND aa.code between '41111' and '41160' OR aa.code between '42211' and '42220' ORDER BY am.date, am.ref""", (m_date_from, m_date_to, curdest_id,))
            result = self._cr.dictfetchall()
            _logger.error('%s', result)

        else:
            self._cr.execute("""SELECT am.date, sp.location_dest_id, sl.name consumption, pc.name category, pt.name product,aml.quantity, aml.debit, aml.credit, am.ref FROM account_move am 
            LEFT JOIN account_move_line aml ON am.id = aml.move_id LEFT JOIN product_product pp LEFT JOIN product_template pt 
            ON pt.id = pp.product_tmpl_id ON aml.product_id = pp.id LEFT JOIN product_category pc on pc.id = pt.categ_id LEFT JOIN
            stock_picking sp ON sp.name = aml.ref LEFT JOIN stock_location sl on sl.id = sp.location_dest_id LEFT JOIN account_account aa ON aa.id = aml.account_id where 
            am.date >= %s and am.date <= %s AND aa.code between '41111' and '41160' OR aa.code between '42211' and '42220' ORDER BY am.date, am.ref""", (m_date_from, m_date_to,))
            result = self._cr.dictfetchall()
            _logger.error('%s', result)
        row = 7
        total = 0.00
        for data in result:
            
            amount = float(data['debit']) - float(data['credit']) 
            
#             amount = float(data['amount']) 
            total = total + amount
            
            sheet.write(row, 0, str(data['date']), format3)
            sheet.write(row, 1, str(data['ref']), format3)
            sheet.write(row, 2, str(data['consumption']), format3)
            sheet.write(row, 3, str(data['category']), format3)
            sheet.write(row, 4, str(data['product']), format3)
            sheet.write(row, 5, str(data['quantity']), format3)
            sheet.write(row, 6, str(amount), format3)
            row = row + 1
        sheet.write(row + 1, 5, "Total", format4)
        sheet.write(row + 1, 6, total, format4)
        path = ("/home/reports/Stock_consumption_report.xls")
        workbook.save(path)
        file = open(path, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        self.write({'state': 'get', 'file_name': out, 'stock_data':'Stock_consumption_report.xls'})
        return {
               'type': 'ir.actions.act_window',
               'res_model': 'stock.consumption.report',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': self.id,
               'target': 'new',
            }                
                  
