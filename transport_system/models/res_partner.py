# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Add PAN Number'

    pan_number = fields.Char(string='PAN Number',)

    @api.constrains('pan_number')
    def check_pan_number(self):
        if self.pan_number:
            for rec in self:
                if len(rec.pan_number) != 9:
                    raise ValidationError(_('PAN Number must be 9 digit number'))
                if not re.match('^[0-9]*$', rec.pan_number):
                    raise ValidationError(_('PAN Number must be 9 digit number'))

    def action_check_pan(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://ird.gov.np/PanSearch',
            'target': 'new',
        }

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s  [%s]' % (rec.name, rec.pan_number)))
        return res

    @api.onchange('name')
    def _compute_upper_name(self):
        for rec in self:
            rec.name = rec.name.upper() if rec.name else False
