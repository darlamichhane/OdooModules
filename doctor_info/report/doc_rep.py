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


class DoctorSalesReporting(models.TransientModel):
    _name = "doctor.reporting"
    
    invoice_data = fields.Char('Name',)
    file_name = fields.Binary('Doctor Checkups Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')
   
    doctor_id = fields.Many2one('doctor.setup', string='Doctor')
    category_id = fields.Many2one('product.category', string='Department')
    date_from = fields.Date('Start Date', required='True', default=date.today())
    date_to = fields.Date('End date', required='True', default=date.today())

    @api.multi
    def action_doc_report(self):
        # mon_name = datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
        # mon_name = mon_name.strftime("%B")
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
       
        sheet = workbook.add_sheet("Doctor_Checkups_Report", cell_overwrite_ok=True)
        sheet.col(0).width = int(15 * 260)
        sheet.col(1).width = int(20 * 260)    
        sheet.col(2).width = int(25 * 260)    
        sheet.col(3).width = int(28 * 260) 
        sheet.col(4).width = int(20 * 260)   
        sheet.col(5).width = int(24 * 260)
        sheet.col(6).width = int(24 * 260)
        sheet.col(7).width = int(12 * 260)
        sheet.col(8).width = int(12 * 260)
        sheet.col(9).width = int(15 * 260)   
        sheet.col(10).width = int(15 * 260)
        sheet.col(11).width = int(30 * 260)   
        sheet.write_merge(0, 1, 0, 10, 'Doctor Checkups Report', format0)
        sheet.write(2, 0, str("Date" + ":"), format1)
        sheet.write(2, 1, str(self.date_from), format1)
        sheet.write(2, 2, str("Doctor"), format1)
        sheet.write(2, 3, str(self.doctor_id.name), format1)
        
        sheet.write(3, 0, "Invoice Date", format1)
        sheet.write(3, 1, "Invoice Number", format1)
        sheet.write(3, 2, "Patient Name", format1)
        sheet.write(3, 3, "Service", format1)
        sheet.write(3, 4, "Service Department", format1)
        sheet.write(3, 5, "Doctor Department", format1)
        sheet.write(3, 6, "Doctor Name", format1)
        sheet.write(3, 7, "Quantity", format1)
        sheet.write(3, 8, "Discount", format1)
        sheet.write(3, 9, "Amount", format1)
        sheet.write(3, 10, "Salesperson", format1)
        # sheet.write(3, 5, str(m_date_from), format1)
        # sheet.write(3, 6, str(m_date_to), format1)
        if self.doctor_id and not self.category_id:
            curdoc_id = self.doctor_id.id
            self._cr.execute("""select ail.doctor_id,ail.discount_line_amount,ai.id,ai.type as type,ai.discount_type as disc_typ,ai.discount_percentage as disc_p,ai.number as number,ai.date_invoice as dat,ai.user_id as usr,pp.product_tmpl_id,ail.name as pro_name,ds.name as doc_name,ds.profile,rs.name as pat_name,ail.quantity,ail.price_subtotal from account_invoice_line ail 
            left join doctor_setup ds on ail.doctor_id = ds.id left join account_invoice ai on ail.invoice_id = ai.id left join res_partner rs on ai.partner_id =rs.id left join product_product pp left join product_template pt on pt.id = pp.product_tmpl_id
            on ail.product_id = pp.id where ai.date_invoice>=%s and ai.date_invoice<=%s and ai.state in ('open','paid')  and ai.type in ('out_invoice','out_refund') and ail.doctor_id =%s order by ai.date_invoice,ai.number""", (m_date_from, m_date_to, curdoc_id,))
            result = self._cr.dictfetchall()
        elif self.doctor_id and self.category_id:
            curdoc_id = self.doctor_id.id
            curcat_id = self.category_id.id
            self._cr.execute("""select ail.doctor_id,ail.discount_line_amount,ai.id,ai.type as type,ai.discount_type as disc_typ,ai.discount_percentage as disc_p,ai.number as number,ai.date_invoice as dat,ai.user_id as usr,pp.product_tmpl_id,ail.name as pro_name,ds.name as doc_name,ds.profile,rs.name as pat_name,ail.quantity,ail.price_subtotal from account_invoice_line ail 
            left join doctor_setup ds on ail.doctor_id = ds.id left join account_invoice ai on ail.invoice_id = ai.id left join res_partner rs on ai.partner_id =rs.id left join product_product pp left join product_template pt on pt.id = pp.product_tmpl_id
            on ail.product_id = pp.id where ai.date_invoice>=%s and ai.date_invoice<=%s and pt.categ_id = %s and ail.doctor_id =%s and  ai.state in ('open','paid') and ai.type in ('out_invoice','out_refund')  order by ai.date_invoice,ai.number""", (m_date_from, m_date_to, curcat_id, curdoc_id,))
            result = self._cr.dictfetchall()
        elif not self.doctor_id  and self.category_id:
            curcat_id = self.category_id.id
            self._cr.execute("""select ail.doctor_id,ail.discount_line_amount,ai.id,ai.type as type,ai.discount_type as disc_typ,ai.discount_percentage as disc_p,ai.number as number,ai.date_invoice as dat,ds.profile,ai.user_id as usr,pp.product_tmpl_id,ail.name as pro_name,ds.name as doc_name,rs.name as pat_name,ail.quantity,ail.price_subtotal from account_invoice_line ail 
            left join doctor_setup ds on ail.doctor_id = ds.id left join account_invoice ai on ail.invoice_id = ai.id left join res_partner rs on ai.partner_id =rs.id left join product_product pp left join product_template pt on pt.id = pp.product_tmpl_id
            on ail.product_id = pp.id where ai.date_invoice>=%s and ai.date_invoice<=%s and pt.categ_id = %s and ai.state in ('open','paid') and ai.type in ('out_invoice','out_refund') order by ai.date_invoice,ai.number""", (m_date_from, m_date_to, curcat_id,))
            result = self._cr.dictfetchall()
        else:
            self._cr.execute("""select ail.doctor_id,ail.discount_line_amount,ai.id,ai.type as type,ai.discount_type as disc_typ,ai.discount_percentage as disc_p,ai.number as number,ai.date_invoice as dat,ai.user_id as usr,ds.profile,pp.product_tmpl_id,ail.name as pro_name,ds.name as doc_name,rs.name as pat_name,ail.quantity,ail.price_subtotal from account_invoice_line ail 
            left join doctor_setup ds on ail.doctor_id = ds.id left join account_invoice ai on ail.invoice_id = ai.id left join res_partner rs on ai.partner_id =rs.id left join product_product pp left join product_template pt on pt.id = pp.product_tmpl_id
            on ail.product_id = pp.id where ai.date_invoice>=%s and ai.date_invoice<=%s and ai.state in ('open','paid') and ai.type in ('out_invoice','out_refund') order by ai.date_invoice,ai.number""", (m_date_from, m_date_to,))
            result = self._cr.dictfetchall()
        row = 4
        total = 0.00
        disc_amt = 0.00
        for data in result:
            if data['disc_typ'] == 'percentage':
                if data['type'] == 'out_refund':
                    sub_total = (-1) * ((float(data['price_subtotal']) - (float(data['price_subtotal']) * float(data['disc_p'])) / 100))
                if data['type'] == 'out_invoice':
                    sub_total = (1) * ((float(data['price_subtotal']) - (float(data['price_subtotal']) * float(data['disc_p'])) / 100))
                total = sub_total + total
                # total = float(data['price_subtotal'])+total
            else:
                if data['type'] == 'out_refund':
                    sub_total = (-1) * float(data['price_subtotal']) 
                if data['type'] == 'out_invoice':
                    sub_total = (1) * float(data['price_subtotal']) 
                total = sub_total + total
            
            tmp_id = int(data['product_tmpl_id'])
            
            tmp_obj = self.env['product.template'].search([('id', '=', tmp_id)], limit=1)
            cate_obj = self.env['product.category'].search([('id', '=', tmp_obj.categ_id.id)], limit=1)
            inv_obj = self.env['account.invoice'].search([('id', '=', data['id'])], limit=1)
            total_discount = 0.0
            for rec in inv_obj:
                if rec.discount:
                    if rec['type'] == 'out_refund':
                        disc_amt = (-1) * (float(data['price_subtotal']) * float(data['disc_p'])) / 100
                        sheet.write(row, 8, str(disc_amt), format3)
                    total_discount = disc_amt + total_discount
                    if rec['type'] == 'out_invoice':
                        disc_amt = (1) * (float(data['price_subtotal']) * float(data['disc_p'])) / 100
                        sheet.write(row, 8, str(disc_amt), format3)
                    total_discount = disc_amt + total_discount
           
            if (float(data['discount_line_amount'])) > 0:
                    sheet.write(row, 6, str(data['discount_line_amount']), format3)
            sheet.write(row, 0, str(data['dat']), format3)
            sheet.write(row, 1, str(data['number']), format3)
            sheet.write(row, 2, str(data['pat_name']).title(), format3)
            sheet.write(row, 3, str(tmp_obj.name), format3)
            sheet.write(row, 4, str(cate_obj.name), format3)
            sheet.write(row, 5, str(data['profile']), format3)
            sheet.write(row, 6, str(data['doc_name']), format3)
            sheet.write(row, 7, str(data['quantity']), format3)
            sheet.write(row, 9, str(sub_total), format3)
            slpr_id = self.env['res.users'].search([('id', '=', data['usr'])])
            if slpr_id:
                sheet.write(row, 10, str(slpr_id.login).capitalize(), format3)
            row = row + 1
        sheet.write(row + 1, 8, "Total", format4)
        sheet.write(row + 1, 9, total, format4)
        path = ("/home/reports/Doctor_checkups_report.xls")
        workbook.save(path)
        file = open(path, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        self.write({'state': 'get', 'file_name': out, 'invoice_data':'Doctor_checkups_report.xls'})
        return {
               'type': 'ir.actions.act_window',
               'res_model': 'doctor.reporting',
               'view_mode': 'form',
               'view_type': 'form',
               'res_id': self.id,
               'target': 'new',
            }                
                  
