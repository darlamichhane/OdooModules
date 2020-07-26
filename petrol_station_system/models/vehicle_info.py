# -*- coding: utf-8 -*-
##############################################################################

from odoo import models, fields, api, _

class VehicleInformation(models.Model):
    _name = 'vehicle.info'
    _rec_name = 'vehicle_no'

    # @api.onchange('owner_id')
    # def set_owner_phone(self):
    #     for rec in self:
    #         rec.owner_phone = rec.owner_id.mobile
    #         rec.owner_address = rec.owner_id.street_name
    #         rec.owner_pan = rec.owner_id.pan_number

    name = fields.Char(string="Vehicle Name")
    vehicle_model = fields.Char(string="Vehicle Model", required=True)
    vehicle_no = fields.Char(string="Vehicle Number", required=True)
    owner_id = fields.Many2one('res.partner', string="Vehicle Owner Name",)
    owner_address = fields.Char(string="Address:")
    owner_pan = fields.Char(string="PAN/VAT No:",)
    owner_phone = fields.Char(string="Phone No:")
    image = fields.Binary(string='Image', store=True,)
    active = fields.Boolean(string="Active", default=True)

    @api.multi
    def vehicle_model_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s %s' % (rec.vehicle_model, rec.vehicle_no)))
        return res

    @api.onchange('vehicle_no')
    def _compute_upper_name(self):
        for rec in self:
            rec.vehicle_no = rec.vehicle_no.upper() if rec.vehicle_no else False