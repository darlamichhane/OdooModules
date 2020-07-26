from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'


    @api.onchange('address_state')
    def onchange_address_state(self):
        for rec in self:
            return {'domain': {'address_district': [('state_id', '=', rec.address_state.id)]}}

    @api.onchange('address_district')
    def onchange_address_district(self):
        for rec in self:
            return {'domain': {'address_local': [('district_id', '=', rec.address_district.id)]}}


    @api.constrains('ward_no')
    def _check_ward_no(self):
        if self.ward_no:
            if not (self.ward_no.isdigit()):
                raise ValidationError('The Ward Number must be number not alphabet')


    address_state= fields.Many2one('res.nepal.state', string='State', required=1,help='Choose your state', track_visibility='always')

    address_district= fields.Many2one('res.address.district', string='District',required=1,help='Choose your District', track_visibility='always')

    address_local= fields.Many2one('res.address.local', string='City', required=1,help='Choose your Locality',track_visibility='always')

    ward_no= fields.Char(string='Ward', help='Your Ward No.', track_visibility='always')

    street_name= fields.Char(string='Street', help='Your Street Name', track_visibility='always')