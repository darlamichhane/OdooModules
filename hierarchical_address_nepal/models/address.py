from odoo import models, fields,_

class AddressState(models.Model):
    _name = 'res.nepal.state'
    _description = 'States of Nepal'
    _order = 'name'

    name = fields.Char(string='Name',readonly=1)
    code = fields.Char(string='State Code',required=1,readonly=1)
    country_id = fields.Many2one('res.country',string='Country',required=1,readonly=1)


class AddressDistrict(models.Model):
    _name = 'res.address.district'
    _description = 'District of Nepal'
    _order = 'name'

    name = fields.Char(string='Name',readonly=1)
    state_id = fields.Many2one('res.nepal.state',string='State',required=1,readonly=1)


class AddressLocal(models.Model):
    _name = 'res.address.local'
    _description = 'Local Levels of Nepal'
    _order = 'name'

    name = fields.Char(string='Name')
    district_id = fields.Many2one('res.address.district',string='District',required=1)
