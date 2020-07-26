# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import  timedelta,date,time
import datetime

# class AccIinvPur(models.Model):
#     _inherit = 'account.invoice'
    
#     def reg_pay_view(self):
#         return {
#         'type': 'ir.actions.act_window',
#         'name': '_(Reg) ',
#         'view_mode': 'form', 
#         'target': 'new',
#         'res_model': 'account.invoice',
#         'context': {'inv_obj': self.id} 
#         }                             

class RegPay(models.TransientModel):
    _name = 'reg.pay'
    
    @api.onchange('partner_id')
    def onchange_basket(self):
        # k = self.env['res.partner'].search([('id','=',self.partner_id.id)],limit=1).id
        res = {
        'domain' : {
        'invoice' : [('partner_id', '=', self.partner_id.id),('type', '=', 'in_invoice'),('state','=','open')],
        }
        }
        return res
    # @api.onchange('invoice')
    # def _calculate_invoice(self):
    #         self.amount = self.invoice.amount_total
    #         self.partner_id = self.invoice.partner_id.id
   
    @api.one
    @api.depends('invoice_line_ids.tds_line_amnt')
    def _compute_tot_amount(self):
        self.tds_amnt = sum(line.tds_line_amnt for line in self.invoice_line_ids)

    @api.one
    @api.depends('tds_amnt','amount')
    def _compute_to_pay_amount(self):
        self.tds_amnt_to_pay  = self.amount - self.tds_amnt
    # @api.onchange('invoice')
    # def _calculate_partner(self):
    #         self.partner_id = self.invoice.partner_id.id
            # self.amount = self.invoice.amount_total
    state = fields.Selection([('choose', 'choose'), ('get', 'get'),('done','Done')],
                             default='get')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    amount = fields.Monetary(string='Amount to pay', required=True )
    payment_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, )
    communication = fields.Char(string='Refrence',required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', 'in', ('bank', 'cash'))]")
    currency_id = fields.Many2one('res.currency', string='Currency',  readonly=True)
    invoice = fields.Many2many('account.invoice', string='Invoices', required=True)
    invoice_line_ids = fields.One2many('reg.pay.lines', 'invoice_id', string='Invoice Lines', )
    tds_amnt = fields.Float(string="TDS Amount", compute='_compute_tot_amount')
    tds_amnt_to_pay = fields.Float(string="Amount after TDS", compute='_compute_to_pay_amount')
    tds_account_id = fields.Many2one('account.account',string="TDS Account")
    payment_account_id = fields.Many2one('account.account',string="Payment Account")
    message = fields.Text('Message')
    residual = fields.Monetary(string='Amount Due')
    flag = fields.Boolean('Flag',default=False)

    @api.multi
    def reg_pay_view(self):
       return {
                'type': 'ir.actions.act_window',
                'res_model': 'reg.pay',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'new',
                }
    @api.multi
    def show_lines_purchase(self):
        amt = 0.0
        resi = 0.0
        # self._origin.id
        for line in self.invoice_line_ids:
                line.unlink()
        for records in self.invoice: 
            # self.amount = self.invoice.amount_total
            # self.partner_id = self.invoice.partner_id.id
            inv_obj = self.env['account.invoice'].search([('id','=',records.id)],limit=1)
            amt = amt + inv_obj.amount_total
            resi = resi + inv_obj.residual
            p_id = inv_obj.partner_id.id
            RegPay = self.env['reg.pay.lines']
            for rec in inv_obj.invoice_line_ids:
                if rec.invoice_line_tax_ids:
                    k = "Vat 13%"
                else:
                    k = " "
                
                RegPay.create({
                'inv_id': rec.invoice_id.id,
                'product_id':rec.product_id.id,
                'price_unit':rec.price_unit,
                'tax_lebel':k,
                'quantity':rec.quantity,
                'price_subtotal':rec.price_subtotal,
                'invoice_id': self.id,
                })
            # self.write({'state': 'get'})
            # self.write({'invoice': self.invoice.id})
            self.amount = amt
            self.residual = resi
            self.partner_id = p_id
            self.flag = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reg.pay',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
            }
    
    @api.multi
    def trans_amt_reconcile_full(self,id_data):
        move_lines = self.env['account.move.line'].browse(id_data)
        currency = False
        for aml in move_lines:
            if not currency and aml.currency_id.id:
                currency = aml.currency_id.id
            elif aml.currency_id:
                if aml.currency_id.id == currency:
                    continue
                raise UserError(_('Operation not allowed. You can only reconcile entries that share the same secondary currency or that don\'t have one. Edit your journal items or make another selection before proceeding any further.'))
        #Don't consider entrires that are already reconciled
        move_lines_filtered = move_lines.filtered(lambda aml: not aml.reconciled)
        #Because we are making a full reconcilition in batch, we need to consider use cases as defined in the test test_manual_reconcile_wizard_opw678153
        #So we force the reconciliation in company currency only at first
        move_lines_filtered.with_context(skip_full_reconcile_check='amount_currency_excluded', manual_full_reconcile_currency=currency).reconcile()

        #then in second pass the amounts in secondary currency, only if some lines are still not fully reconciled
        move_lines_filtered = move_lines.filtered(lambda aml: not aml.reconciled)
        if move_lines_filtered:
            move_lines_filtered.with_context(skip_full_reconcile_check='amount_currency_only', manual_full_reconcile_currency=currency).reconcile()
        move_lines.compute_full_after_batch_reconcile()
        # return {'type': 'ir.actions.act_window_close'}
       
    @api.multi
    def payment_done(self):
            if self.amount == self.residual or self.amount <= self.residual:
                account_id = self.env['account.account'].search([('name','like','Account Payable')],limit=1)
                if self.tds_amnt > 0.0:
                    move_lines = [
                            (0, 0, {
                                'name': self.communication, # a label so accountant can understand where this line come from
                                'debit': self.amount, # amount of debit
                                'credit': 0.0, # amount of credit
                                'account_id': account_id.id, # account 
                                'date': self.payment_date,
                                'partner_id': self.partner_id.id, # partner if there is one
                                'currency_id':account_id.currency_id.id or False,
                            }),
                            (0, 0, {
                                'name': self.communication,
                                'debit': 0.0, 
                                'credit': self.amount - self.tds_amnt,
                                'account_id': self.payment_account_id.id,
                                # 'analytic_account_id': context.get('analytic_id', False),
                                'date': self.payment_date,
                                'partner_id': self.partner_id.id,
                                'currency_id': account_id.currency_id.id or False,
                            }),
                            (0, 0, {
                                'name': "TDS",
                                'debit': 0.0, 
                                'credit': self.tds_amnt,
                                'account_id': self.tds_account_id.id,
                                # 'analytic_account_id': context.get('analytic_id', False),
                                'date': self.payment_date,
                                'partner_id': self.partner_id.id,
                                'currency_id':account_id.currency_id.id or False,
                            })
                        ]
                else:
                    move_lines = [
                            (0, 0, {
                                'name': self.communication, # a label so accountant can understand where this line come from
                                'debit': self.amount, # amount of debit
                                'credit': 0.0, # amount of credit
                                'account_id': account_id.id, # account 
                                'date': self.payment_date,
                                'partner_id': self.partner_id.id, # partner if there is one
                                'currency_id':account_id.currency_id.id or False,
                            }),
                            (0, 0, {
                                'name': self.communication,
                                'debit': 0.0, 
                                'credit': self.amount,
                                'account_id': self.payment_account_id.id,
                                # 'analytic_account_id': context.get('analytic_id', False),
                                'date': self.payment_date,
                                'partner_id': self.partner_id.id,
                                'currency_id': account_id.currency_id.id or False,
                            }),
                            
                        ]
            # Create account move
                # sequence_code = 'Cash'
                k = self.env['account.move'].create( {
                            'name': '/',
                            'journal_id': self.journal_id.id, # journal ex: sale journal, cash journal, bank journal....
                            'date':self.payment_date,
                            'ref': self.communication,
                            # 'state': 'posted',
                            'line_ids': move_lines, # this is one2many field to account.move.line
                        })
                k.post() 
                id_data = []
                # invoice_ob = self.env['account.invoice'].search([('id','=',self.invoice.id)],limit=1)
                # invoice_ob.update({'state' : 'paid'}) 
                for records in self.invoice:
                    result = self._cr.execute("""update account_invoice set state = 'paid' where id =%s"""%(records.id))
                    l = self.env['account.move.line'].search([('move_id','=',records.move_id.id),('account_id','=',account_id.id)]) 
                    id_data.append(l.id)
                # for lines in k.line_ids:
                j = self.env['account.move.line'].search([('move_id','=',k.id),('account_id','=',account_id.id)])
                id_data.append(j.id)
                    
                
                self.trans_amt_reconcile_full(id_data)
                self.write({'message': _("Invoice Paid Successfully")})
                self.write({'state': 'choose'})
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'reg.pay',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.id,
                    'target': 'new',
                    }
            else:
                raise Warning(_("The due amount should be equal to amount to pay."))

class RegPayLines(models.TransientModel):
    _name = 'reg.pay.lines'

    @api.one
    @api.depends('tds_percent')
    def _compute_tdsamount(self):
        self.tds_line_amnt = ((self.tds_percent)/100) * self.price_subtotal
    
    # @api.one
    # @api.depends('price_unit')
    # def _compute_subtotal(self):
    #     self.price_subtotal = self.price_unit * self.quantity
    
    product_id = fields.Many2one('product.product', string='Product',ondelete='restrict', index=True)
    inv_id = fields.Many2one('account.invoice', string='Bill no', index=True)
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Monetary(string='Amount (without Taxes)',store=True, readonly=True, help="Total amount without taxes")
    # invoice_line_tax_ids = fields.Many2one('account.tax',string='Taxes', )
    tax_lebel = fields.Char(string='Tax Applied')
    tds_percent = fields.Float(string="TDS Percent")
    price_tds = fields.Monetary(string='Amount (without Taxes)',store=True, readonly=True, help="Total amount without taxes")
    tds_line_amnt = fields.Float(string='Unit Price',compute='_compute_tdsamount')
    currency_id = fields.Many2one('res.currency', string='Currency',  readonly=True)
    invoice_id = fields.Many2one('reg.pay', string='Invoice Reference',ondelete='cascade', index=True)
