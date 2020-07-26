# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import json
import uuid
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gender = fields.Char(string="Gender")
    birthdate = fields.Date(string="Birth Date", readonly=True)
    age = fields.Integer(compute='_compute_age', string='Age',
                         readonly=True, store=True)   

    @api.multi
    @api.depends('birthdate')
    def _compute_age(self):
        '''Method to calculate Customer age'''
        current_dt = datetime.today()
        for rec in self:
            if rec.birthdate:
                start = datetime.strptime(rec.birthdate,
                                          DEFAULT_SERVER_DATE_FORMAT)
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc
       
