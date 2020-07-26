# -*- coding: utf-8 -*-
import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
class TokenCreditSaleReport(models.TransientModel):
    _name = "creditsale.report"
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    token_data = fields.Char('Name',)
    file_name = fields.Binary('Token Sale Excel Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
    _sql_constraints = [
            ('check','CHECK((start_date <= end_date))',"End date must be greater then start date")
    ]

    @api.multi
    def action_token_sales_report(self):
        if self.partner_id:
            domain = [('claim_date', '>=', self.start_date), ('claim_date', '<=', self.end_date), ('partner_id', '=', self.partner_id.id)]
        else:
            domain = [('claim_date', '>=', self.start_date), ('claim_date', '<=', self.end_date)]

        token_sale = self.env['token.claim'].search(domain)
        record = []
        if token_sale:
            for rec in token_sale:
                record.append(rec)
            self.record = record.sort(key=lambda p: (p.claim_date))
            data1 = {}
            data1['start'] = str(self.start_date)
            data1['end'] = str(self.end_date)
            workbook = xlwt.Workbook()
            sheet=workbook.add_sheet('Credit Token Sales')

            #Column Width
            sheet.col(0).width = int(30 * 260)
            sheet.col(1).width = int(30 * 260)
            sheet.col(2).width = int(18 * 260)
            sheet.col(3).width = int(18 * 260)
            sheet.col(4).width = int(33 * 260)
            sheet.col(5).width = int(23 * 260)
            sheet.col(6).width = int(18 * 260)
            sheet.col(7).width = int(30 * 260)

            #Defining Formats
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
            total=0.00

            #Writing in Sheets
            sheet.write_merge(0, 2, 0, 7, 'Token Credit Sales ', format0)
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

            sheet.write(15, 0, 'Token Number', format1)
            sheet.write(15, 1, 'Product', format1)
            sheet.write(15, 2, 'Quantity', format1)
            sheet.write(15, 3, 'Unit of Measure', format1)
            sheet.write(15, 4, 'Unit Price', format1)
            sheet.write(15, 5, 'Amount (Without Tax)', format1)
            sheet.write(15, 6, 'Total', format6)
            sheet.write(15, 7, 'Customer', format6)

            if record:
                for rec in record:
                    sheet.write(row, 0, str(rec.token_claim_ids.number.number), format3)
                    sheet.write(row, 1, str(rec.token_claim_ids.product_id.name), format3)
                    sheet.write(row, 2, str(rec.token_claim_ids.product_qty), format3)
                    sheet.write(row, 3, str(rec.token_claim_ids.uom_id.name), format3)
                    sheet.write(row, 4, str(rec.token_claim_ids.price_unit), format3)
                    sheet.write(row, 5, str(rec.token_claim_ids.price_total), format3)
                    sheet.write(row, 6, str(rec.token_claim_ids.price_total), format3)
                    sheet.write(row, 7, str(rec.partner_id.name), format3)
                    row+=1
                    total+=rec.token_claim_ids.price_total
                sheet.write(row + 1, 5, "Total", format3)
                sheet.write(row + 1, 6, total, format4)
            else:
                raise Warning("Currently No Credit Tokens For This Data!!")


            #Saving File
            filename = ('/home/reports/Token Sale Report' + '.xls')
            workbook.save(filename)
            file = open(filename, "rb")
            file_data = file.read()
            out = base64.encodestring(file_data)
            self.write({'state': 'get', 'file_name': out, 'token_data': 'Token Credit Sales Report.xls'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'creditsale.report',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new',
            }
        else:
            raise Warning("Currently No Credit Tokens For This Data!!")

