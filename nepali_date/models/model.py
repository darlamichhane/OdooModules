# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import date
from . import bikram
from bikram import samwat


class NepDateInv(models.Model):
    _inherit = 'account.invoice'

    @api.depends('date_invoice')
    def mydate3(self):
        """:return the Nepalidate"""
        if self.date_invoice:
            date_str = str(self.date_invoice) 
            format_str = '%Y-%m-%d'  # The format
            datetime_obj = datetime.strptime(date_str, format_str)
            self.nep_inv_date = samwat.from_ad(datetime_obj.date())

    @api.depends('date_due')
    def mydate4(self):
        if self.date_due:
            """:return the Nepalidate"""
            date_str2 = str(self.date_due)
            format_str = '%Y-%m-%d'  # The format
            datetime_obj2 = datetime.strptime(date_str2, format_str)
            self.nep_due_date = samwat.from_ad(datetime_obj2.date())
    
    nep_inv_date = fields.Char(string='Invoice Date BS', compute=mydate3, store=True)
    nep_due_date = fields.Char(string='Due Date BS', compute=mydate4, store=True)


class NepDateJv(models.Model):
    _inherit = 'account.move'

    @api.depends('date')
    def mydate3(self):
        """:return the Nepalidate"""
        if self.date:
            date_str = str(self.date) 
            format_str = '%Y-%m-%d'  # The format
            datetime_obj = datetime.strptime(date_str, format_str)
            self.nep_jv_date = samwat.from_ad(datetime_obj.date())     

    nep_jv_date = fields.Char(string='Date BS', compute=mydate3, store=True)

    
class DateBsStock(models.Model):
    _inherit = 'stock.picking'

    @api.depends('date')
    def picking_date_bs(self):
        """:return the Nepalidate"""
        if self.date:
            date_str = str(self.date) 
            format_str = '%Y-%m-%d %H:%M:%S'  # The format
            datetime_obj = datetime.strptime(date_str, format_str)
            self.date_bs = samwat.from_ad(datetime_obj.date())     

    date_bs = fields.Char(string='Date BS', compute=picking_date_bs, store=True)

