# -*- coding: utf-8 -*-
##############################################################################

from odoo import models, fields, api, _


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    
    license_no = fields.Char(string="License No")
    is_driver = fields.Boolean(string='Is Driver')
