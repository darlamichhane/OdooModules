# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    service_charge_account = fields.Many2one('account.account', string='ST charge Account')
    service_charge_amount = fields.Monetary(string='ST charge Amount')
