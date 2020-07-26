# -*- coding: utf-8 -*-
##############################################################################

from odoo import models, fields, api, _


class DriverCreation(models.Model):
    _name = 'driver.info'
    
    @api.onchange('driver_id')
    def set_driver_phone(self):
        for rec in self:
            rec.mob_no = rec.driver_id.mobile_phone
            
    @api.onchange('driver_id')
    def set_driver_city(self):
        for rec in self:
            rec.driver_city = rec.driver_id.city        

    @api.onchange('driver_id')
    def set_driver_country(self):
        for rec in self:
            rec.drivercountry_id = rec.driver_id.country_id
    name = fields.Many2one(string="Vehicle Name", required=True)
    driver_image = fields.Binary(string='Image', store=True, attachment=True)
    driver_id = fields.Many2one('hr.employee', string="Driver Name", required=True)
    liscense_no = fields.Char(string="Driver License No", required=True)
    mob_no = fields.Char(string="Driver Mobile No", required=True)
    driver_address = fields.Char(string="Address")
    driver_city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    drivercountry_id = fields.Many2one('res.country', string='Country')
    active = fields.Boolean(string="Active", default=True)
