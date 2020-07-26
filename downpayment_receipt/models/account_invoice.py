# -*- coding: utf-8 -*-
from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    receipt_product_id = fields.Many2one('product.product',string='Receipt Product')
    receipt_journal_id = fields.Many2one('account.journal', string='Receipt Journal')
    
    @api.multi
    def set_receipt_product_id(self):
        ir_values_obj = self.env['ir.values']
        ir_values_obj.sudo().set_default('account.config.settings', 'receipt_product_id', self.receipt_product_id.id)
        ir_values_obj.sudo().set_default('account.config.settings', "receipt_journal_id", self.receipt_journal_id.id)

class AccountInvoiceReceiptInherited(models.Model):
    _inherit = 'account.invoice'


    is_downpayment_receipt = fields.Boolean(string="Is Receipt",default=False)
    has_refund = fields.Boolean(string="Needs to refund",default=False)
    to_refund_amount = fields.Monetary(string='Total Refundable',  readonly=True,  track_visibility='always')
    tot_deposited = fields.Monetary(string='Total Deposited',  readonly=True,  track_visibility='always')
    total_spend = fields.Monetary(string='Total Expenditure',  readonly=True,  track_visibility='always')
    # refund_invoice = fields.Many2one('account.invoice',string='Refund Invoice')

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        self.user_id = self.env.user
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        #custom code
        if to_open_invoices.type == 'out_refund' and to_open_invoices.is_downpayment_receipt is False:
            total_deposit = 0.00
            product_id = self.env['ir.values'].get_default('sale.config.settings', 'deposit_product_id_setting')
            for lines in to_open_invoices.invoice_line_ids:
                if lines.product_id.id == product_id:
                    total_deposit += (lines.quantity * lines.price_unit)
                    
                    # for line in lines.invoice_line_tax_ids:
                        # line.unlink()
                    # lines.unlink()
                # elif lines.quantity < 0:
                    
                    # k = []
                    # for line in lines.invoice_line_tax_ids:
                        # k.append(line.id)
                    # self.env['account.invoice.line'].create(
                    #     {'product_id': lines.product_id.id,
                    #     'name': lines.name,
                    #     'quantity': (lines.quantity * -1),
                    #     'price_unit': lines.price_unit,
                    #     'account_id': lines.account_id.id,
                    #     # 'invoice_line_tax_ids': k,
                    #     'discount': lines.discount,
                    #     'invoice_id':lines.invoice_id.id})
                    # lines.unlink()
                    # lines.quantity = lines.quantity * -1
                    # print("Line is OK")
                # else:
                    # print("Line is OK")
            # to_open_invoices.type = 'out_invoice'
            to_open_invoices.has_refund = True
            to_open_invoices.tot_deposited = total_deposit
            to_open_invoices.to_refund_amount = to_open_invoices.amount_total
            to_open_invoices.total_spend = total_deposit - to_open_invoices.amount_total
            
            # to_refund_inv = self.env['account.invoice'].search([('is_downpayment_receipt','=',True),('origin','=',to_open_invoices.origin)],limit=1)
            # refund_inv = to_refund_inv.refund(to_refund_inv.date_invoice, to_refund_inv.date_invoice, to_refund_inv.name, to_refund_inv.journal_id.id)
            # for data in refund_inv:
                # data.is_downpayment_receipt = True
                # for depline in data.invoice_line_ids:
                    # depline.price_unit = to_open_invoices.to_refund_amount
            # refund_inv.action_invoice_open()
            # to_open_invoices.refund_invoice = refund_inv.id

        ######   
        if to_open_invoices.type == 'out_refund' or to_open_invoices.type == 'out_invoice':
            rec_product_id = self.env['ir.values'].get_default('account.config.settings', 'receipt_product_id')
            rec_journal_id = self.env['ir.values'].get_default('account.config.settings', 'receipt_journal_id')
            for lines in to_open_invoices.invoice_line_ids:
                if lines.product_id.id == rec_product_id:
                    to_open_invoices.is_downpayment_receipt = True
                    to_open_invoices.journal_id = rec_journal_id

        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()
# class SaleOrderReceiptInherited(models.Model):
#     _inherit = 'sale.order'
    
#     @api.depends('order_line.product_id')
#     def _product_deposit(self):
#         product_id = self.env['ir.values'].get_default('sale.config.settings', 'deposit_product_id_setting')
#         for order in self:
#             for line in order.order_line:
#                 if line.product_id == product_id:
#                     self.has_downpayment_product = True

#     has_downpayment_product = fields.Boolean(string="Has Downpayment",store=True, readonly=True, compute='_product_deposit',default=False)

#     @api.multi
#     def action_invoice_create(self, grouped=False, final=False):
#         """
#         Create the invoice associated to the SO.
#         :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
#                         (partner_invoice_id, currency)
#         :param final: if True, refunds will be generated if necessary
#         :returns: list of created invoices
#         """
#         inv_obj = self.env['account.invoice']
#         precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#         invoices = {}
#         references = {}
#         invoices_origin = {}
#         invoices_name = {}

#         for order in self:
#             group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
#             for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
#                 if float_is_zero(line.qty_to_invoice, precision_digits=precision):
#                     continue
#                 if group_key not in invoices:
#                     inv_data = order._prepare_invoice()
#                     invoice = inv_obj.create(inv_data)
#                     references[invoice] = order
#                     invoices[group_key] = invoice
#                     invoices_origin[group_key] = [invoice.origin]
#                     invoices_name[group_key] = [invoice.name]
#                 elif group_key in invoices:
#                     if order.name not in invoices_origin[group_key]:
#                         invoices_origin[group_key].append(order.name)
#                     if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
#                         invoices_name[group_key].append(order.client_order_ref)

#                 if line.qty_to_invoice > 0:
#                     line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
#                 #custom code
#                 elif line.qty_to_invoice < 0 and final:
#                     if order.has_downpayment_product:
#                         print("Invoice has down payments skipping the line addition")
#                     else:
#                         line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

#             if references.get(invoices.get(group_key)):
#                 if order not in references[invoices[group_key]]:
#                     references[invoice] = references[invoice] | order

#         for group_key in invoices:
#             invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
#                                        'origin': ', '.join(invoices_origin[group_key])})

#         if not invoices:
#             raise UserError(_('There is no invoicable line.'))

#         for invoice in invoices.values():
#             invoice.compute_taxes()
#             if not invoice.invoice_line_ids:
#                 raise UserError(_('There is no invoicable line.'))
#             # If invoice is negative, do a refund invoice instead
#             if invoice.amount_total < 0:
#                 invoice.type = 'out_refund'
#                 for line in invoice.invoice_line_ids:
#                     line.quantity = -line.quantity
#             # Use additional field helper function (for account extensions)
#             for line in invoice.invoice_line_ids:
#                 line._set_additional_fields(invoice)
#             # Necessary to force computation of taxes. In account_invoice, they are triggered
#             # by onchanges, which are not triggered when doing a create.
#             invoice.compute_taxes()
#             invoice.message_post_with_view('mail.message_origin_link',
#                 values={'self': invoice, 'origin': references[invoice]},
#                 subtype_id=self.env.ref('mail.mt_note').id)
#         return [inv.id for inv in invoices.values()]


class SaleAdvancePaymentInvInherited(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id or self.product_id.categ_id.property_account_income_categ_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        del context
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'is_downpayment_receipt': True,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'account_analytic_id': order.project_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'comment': order.note,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice