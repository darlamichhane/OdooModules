# -*- coding: utf-8 -*-
import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import  timedelta,date,time
import datetime
from odoo.http import request
import re
class MassPaymentReporting(models.TransientModel):
    _name = "mass.payment"
    
    def _get_default_journal(self):
        return self.env['account.journal'].search([('name', 'ilike', 'Cash')])[0].id

    @api.one
    @api.depends('invoices_ids.amount')
    def _compute_mass_amount(self):
        self.amount = sum(line.amount for line in self.invoices_ids)
    state = fields.Selection([('choose', 'choose'), ('get', 'get'),('done','Done')],
                             default='choose')
    journal_id = fields.Many2one('account.journal',string='Payment Journal',domain=[('type', '=', 'cash')],required=True,default=_get_default_journal)
    user_id = fields.Many2one('res.users',string='Salesperson',required=True)
    date_from = fields.Date('Start Date',required='True',default=date.today())
    date_to = fields.Date('End Date',required='True',default=date.today())
    payment_date = fields.Date('Payment Date',required='True',default=date.today())
    amount = fields.Float(string='Total Invoice Amount',readonly=True, compute='_compute_mass_amount')
    invoices_ids = fields.One2many('mass.payment.line', 'p_id', string='Invoices')
    
    @api.multi
    def action_create_salesperson_pay(self):
        tm = datetime.time(23, 59, 59)
        dt1 = datetime.datetime.strptime(self.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(self.date_to, "%Y-%m-%d").date()
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        domain = [('date_invoice','>=',m_date_from),('date_invoice','<=',m_date_to),('state','=','open'),('amount_total','>','0'),('user_id','=',self.user_id.id),('type','in',('out_invoice','out_refund'))]
        inv_objs = self.env['account.invoice'].search(domain)
        if inv_objs:
            for invoice in inv_objs:
                payment_vals = {}
                j = invoice.id
                k = [j]
                if invoice.type == 'out_invoice':
                    payment_vals['journal_id'] = self.journal_id.id
                    payment_vals['partner_type'] = 'customer'
                    payment_vals['communication'] = invoice.number
                    payment_vals['payment_type'] = 'inbound'
                    payment_vals['payment_method_id'] = 1
                    payment_vals['currency_id'] = invoice.currency_id.id
                    payment_vals['amount'] = abs(invoice.amount_total)
                    payment_vals['payment_date'] = self.payment_date
                    payment_vals['partner_id'] = invoice.partner_id.id
                    payment = self.env['account.payment']
                    payment_s = payment.create(payment_vals)
                    payment.browse(payment_s.id).invoice_ids = k
                    payment_s.post()
                elif invoice.type == 'out_refund':
                    payment_vals['journal_id'] = self.journal_id.id
                    payment_vals['partner_type'] = 'customer'
                    payment_vals['communication'] = invoice.number
                    payment_vals['payment_type'] = 'outbound'
                    payment_vals['payment_method_id'] = 1
                    payment_vals['currency_id'] = invoice.currency_id.id
                    payment_vals['amount'] = abs(invoice.amount_total)
                    payment_vals['payment_date'] = self.payment_date
                    payment_vals['partner_id'] = invoice.partner_id.id
                    payment = self.env['account.payment']
                    payment_s = payment.create(payment_vals)
                    payment.browse(payment_s.id).invoice_ids = k
                    payment_s.post()
            self.write({'state': 'done'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mass.payment',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new',
                }
            # raise Warning(_("All Invoices Paid Sucesssfully"))
            # return {'type': 'ir.actions.act_window_close'}
        else:
            raise Warning(_("No invoices found for selected salesperson or period."))
    
    @api.multi
    def action_show_invoices(self):
        tm = datetime.time(23, 59, 59)
        dt1 = datetime.datetime.strptime(self.date_from, "%Y-%m-%d").date()
        dt2 = datetime.datetime.strptime(self.date_to, "%Y-%m-%d").date()
        m_date_from = datetime.datetime.combine(dt1, datetime.datetime.min.time())
        m_date_to = datetime.datetime.combine(dt2, tm)
        for lines in self.invoices_ids:
                lines.unlink()
        domain = [('date_invoice','>=',m_date_from),('date_invoice','<=',m_date_to),('state','=','open'),('amount_total','>','0'),('user_id','=',self.user_id.id),('type','in',('out_invoice','out_refund'))]
        inv_objs = self.env['account.invoice'].search(domain)   
        if inv_objs:
            for invoice in inv_objs:
                if invoice.type == 'out_invoice':
                    MassPayment = self.env['mass.payment.line']
                    MassPayment.create({
                    'name':invoice.number,
                    'user_id':invoice.user_id.id,
                    'amount':invoice.amount_total,
                    'payment_date':invoice.date_invoice,
                    'state':invoice.state,
                    'patient_id': invoice.partner_id.id,
                    'p_id':self.id
                    })
                elif invoice.type == 'out_refund':
                    MassPayment = self.env['mass.payment.line']
                    MassPayment.create({
                    'name':invoice.number,
                    'user_id':invoice.user_id.id,
                    'amount':(-1)*(invoice.amount_total),
                    'payment_date':invoice.date_invoice,
                    'state':invoice.state,
                    'patient_id': invoice.partner_id.id,
                    'p_id':self.id
                    })
            self.write({'state': 'get'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mass.payment',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new',
                }
        else:
            raise Warning(_("No invoices found for selected salesperson or period. Please choose again."))
class MassPaymentLine(models.TransientModel):
    _name = "mass.payment.line"       

    name = fields.Char('Invoice Ref Number',readonly=True)
    user_id = fields.Many2one('res.users',string='Salesperson',readonly=True)
    amount = fields.Float(string='Total Invoice Amount',readonly=True)
    payment_date = fields.Date('Invoice Date',readonly=True)
    state = fields.Char('State',readonly=True)
    p_id = fields.Many2one('mass.payment',string='mass_id')
    patient_id = fields.Many2one('res.partner',string='Patient')

                  
