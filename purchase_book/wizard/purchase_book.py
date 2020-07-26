# -*- coding: utf-8 -*-
import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime


class PurchaseBookReport(models.TransientModel):
    _name = "purchase.book"
    
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    salesperson_id = fields.Many2one('res.users', string="Storekeeper")
    invoice_data = fields.Char('Name',)
    file_name = fields.Binary('Purchase Book Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    
    _sql_constraints = [
            ('check', 'CHECK((start_date <= end_date))', "End date must be greater then start date")  
    ]
   
    @api.multi
    def action_purchase_book(self):
        if self.salesperson_id:
             domain = [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date),
                                                    ('state', 'in', ('open', 'paid')), ('type', '=', 'in_invoice'), ('user_id', '=', self.salesperson_id.id)]
        
        else:
            domain = [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date),
                                                    ('state', 'in', ('open', 'paid')), ('type', '=', 'in_invoice')]

        invoice = self.env['account.invoice'].search(domain)
        record = []
        if invoice:
            for rec in invoice:
                
                record.append(rec)
            
            file = StringIO()        
            self.record = record.sort(key=lambda p: (p.date_invoice, p.number))
            data1 = {}
            data1['start'] = str(self.start_date)
            data1['end'] = str(self.end_date)
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('sale001')
            sheet.col(0).width = int(15 * 260)
            sheet.col(1).width = int(22 * 260)    
            sheet.col(2).width = int(30 * 260)    
            sheet.col(3).width = int(15 * 260) 
            sheet.col(4).width = int(15 * 260)   
            sheet.col(5).width = int(15 * 260)
            sheet.col(6).width = int(18 * 260)
            format0 = xlwt.easyxf('font:height 500,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
            format1 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
            format2 = xlwt.easyxf('font:bold True;align: horiz left')
            format3 = xlwt.easyxf('align: horiz left')
            format4 = xlwt.easyxf('align: horiz right')
            format5 = xlwt.easyxf('font:bold True;align: horiz right')
            format6 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz right')
            format7 = xlwt.easyxf('font:bold True;borders:top thick;align: horiz right')
            format8 = xlwt.easyxf('font:bold True;borders:top thick;pattern: pattern solid, fore_colour gray25;align: horiz left')
            timestamp = str(datetime.today())
            row = 10
            sheet.write_merge(0, 2, 0, 6, 'Purchase Book ' , format0)
            sheet.write(4, 0, "Hospital Name:", format1)
            sheet.write(4, 1, str(rec.company_id.name), format2)
            sheet.write(5, 0, "Address:", format1)
            sheet.write(5, 1, str(rec.company_id.street), format2)
            sheet.write(6, 0, "Purchase Date", format1)
            sheet.write(6, 1, data1['start'], format2)
            sheet.write(6, 2, 'to', format2)
            sheet.write(6, 3, data1['end'], format2)
            sheet.write(9, 0, 'Bill Date', format1)
            sheet.write(9, 1, 'Bill Number', format1)
            sheet.write(9, 2, 'Vendor', format1)
            sheet.write(9, 3, 'Subtotal', format6)
            sheet.write(9, 4, 'Tax Amount', format6)
            sheet.write(9, 5, 'Total', format6)
            sheet.write(9, 6, 'Storekeeper', format1)
            row1 = 10
            total = 0.00
            if record:
                for rec in record:
                    if rec.type == 'in_refund':
                        sub_total = (-1) * float(rec.amount_total)
                    if rec.type == 'in_invoice':
                        sub_total = (1) * float(rec.amount_total)
                    total = sub_total + total
                    sheet.write(row, 0, str(rec.date_invoice), format3)
                    sheet.write(row, 1, str(rec.number), format3)
                    sheet.write(row, 2, str(rec.partner_id.name), format3)
                    sheet.write(row, 3, str(rec.amount_untaxed), format4)
                    sheet.write(row, 4, str(rec.amount_tax), format4)
                    sheet.write(row, 5, str(sub_total), format4)
                    sheet.write(row, 6, str(rec.user_id.login.capitalize()), format3)
                    row = row + 1
                sheet.write(row + 1, 4, "Total", format3)
                sheet.write(row + 1, 5, total, format4)
                    
            else:
                raise Warning("Currently No Invoice/Bills For This Data!!")
            filename = ('/home/reports/Purchase Book' + '.xls')
            workbook.save(filename)
            file = open(filename, "rb")
            file_data = file.read()
            out = base64.encodestring(file_data)
            self.write({'state': 'get', 'file_name': out, 'invoice_data':'Purchase Book.xls'})
            return {
               'type': 'ir.actions.act_window',
               'res_model': 'purchase.book',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': self.id,
               'target': 'new',
            }                      
        else:
            raise Warning("Currently No Invoice/Bills For This Data!!")
