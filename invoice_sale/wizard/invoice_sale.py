# -*- coding: utf-8 -*-
import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
class InvoiceReport(models.TransientModel):
    _name = "invoice.report"
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    salesperson_id = fields.Many2one('res.users', string="Salesperson")
    invoice_data = fields.Char('Name',)
    file_name = fields.Binary('Invoice Excel Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    _sql_constraints = [
            ('check','CHECK((start_date <= end_date))',"End date must be greater then start date")
    ]
    @api.multi
    def action_invoice_report(self):
        if self.salesperson_id:
             domain = [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date),
                                                    ('state', 'in', ('open','paid')),('user_id','=',self.salesperson_id.id)]
        else:
            domain = [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date),
                                                    ('state', 'in', ('open','paid'))]
        invoice = self.env['account.invoice'].search(domain)
        record = []
        if invoice:
            for rec in invoice:
                # if self.partner_select == "customer" and rec.partner_id.customer == True and rec.partner_id.supplier == False:
                #     record.append(rec)
                # elif self.partner_select == "vendor" and rec.partner_id.supplier == True and rec.partner_id.customer == False:
                #     record.append(rec)
                # elif self.partner_select == "both" and rec.partner_id.customer == True and rec.partner_id.supplier == True:
                record.append(rec)
            file = StringIO()
            self.record= record.sort(key=lambda p: (p.date_invoice, p.number))
            data1 = {}
            data1['start'] = str(self.start_date)
            data1['end'] = str(self.end_date)
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('sale001')
            sheet.col(0).width = int(30*260)
            sheet.col(1).width = int(30*260)
            sheet.col(2).width = int(18*260)
            sheet.col(3).width = int(18*260)
            sheet.col(4).width = int(33*260)
            sheet.col(5).width = int(23*260)
            sheet.col(6).width = int(18*260)
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
            row=16
            sheet.write_merge(0, 2, 0, 7, 'VAT SALES REGISTER ' , format0)
            sheet.write(5, 0, "Seller Name:", format1)
            sheet.write(5, 1, str(rec.company_id.name), format2)
            sheet.write(6, 0, "Seller PAN:", format1)
            sheet.write(6, 1, str(rec.company_id.vat), format2)
            sheet.write(7, 0, "Seller Address:", format1)
            sheet.write(7, 1, str(rec.company_id.street), format2)
            sheet.write(8, 0, "Duration of sales", format1)
            sheet.write(8, 1, data1['start'], format2)
            sheet.write(8, 2, 'to', format2)
            sheet.write(8, 3, data1['end'], format2)
            sheet.write(10, 1, 'Report generated at:', format2)
            sheet.write(10, 2, timestamp, format2)
            sheet.write(15, 0, 'Date BS', format1)
            sheet.write(15, 1, 'Invoice No', format1)
            sheet.write(15, 2, 'Customer', format1)
            sheet.write(15, 3, 'Customer PAN No', format1)
            sheet.write(15, 4, 'Subtotal.', format1)
            # sheet.write(15, 5, 'ST Charge', format1)
            sheet.write(15, 5, 'Amount Tax', format1)
            sheet.write(15, 6, 'Total', format6)
            sheet.write(15, 7, 'Salesperson', format6)
            row1 = 16
            total = 0.00
            if record:
                for rec in record:
                    if rec.type == 'out_refund':
                        sub_total = (-1)*float(rec.amount_total)
                    if rec.type == 'out_invoice':
                        sub_total = (1)*float(rec.amount_total)
                    total = sub_total+total
                    sheet.write(row, 0, str(rec.nep_inv_date), format3)
                    sheet.write(row, 1, str(rec.number), format3)
                    sheet.write(row, 2, str(rec.partner_id.name), format3)
                    sheet.write(row, 3, str(rec.partner_id.tax_no), format3)
                    sheet.write(row, 4, str(rec.amount_untaxed), format4)
                    # sheet.write(row, 5, str(rec.service_charge_amount), format4)
                    sheet.write(row, 5, str(rec.amount_tax), format4)
                    sheet.write(row, 6, str(sub_total), format4)
                    sheet.write(row, 7, str(rec.user_id.name), format4)
                    # sheet.write(row, 7, str(rec.amount_tax), format3)
                    # sheet.write(row, 8, str(rec.amount_total), format3)
                    # sheet.write(row, 9, str(rec.amount_tax), format3)
                    row=row+1
                sheet.write(row+1, 5,"Total", format3)
                sheet.write(row+1, 6, total, format4)
            else:
                raise Warning("Currently No Invoice/Bills For This Data!!")
            filename = ('/home/reports/Invoice Report'+ '.xls')
            workbook.save(filename)
            file = open(filename, "rb")
            file_data = file.read()
            out = base64.encodestring(file_data)
            self.write({'state': 'get', 'file_name': out, 'invoice_data':'Invoice Report.xls'})
            return {
               'type': 'ir.actions.act_window',
               'res_model': 'invoice.report',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': self.id,
               'target': 'new',
            }
        else:
            raise Warning("Currently No Invoice/Bills For This Data!!")