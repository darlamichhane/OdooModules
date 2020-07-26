from odoo import models, fields, api,  _
from datetime import datetime
from odoo.exceptions import ValidationError
import re


class WorkOrder(models.Model):
    _name = 'work.order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Work Order for Vehicle Servicing'
    _order = 'name'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
        if self.odometer:
            self.vehicle_id.odometer=self.odometer

    @api.onchange('customer_id')
    def onchange_customer_id(self):
        for rec in self:
            if rec.customer_id:
                rec.email=rec.customer_id.email
                rec.mobile=rec.customer_id.mobile
                address=rec.customer_id.address_state.name + ", " + rec.customer_id.address_district.name + ", " + rec.customer_id.address_local.name
                if rec.customer_id.ward_no:
                    address = address + "-" + rec.customer_id.ward_no
                if rec.customer_id.street_name:
                    address += ", " + rec.customer_id.street_name
                rec.address=address
            # return {'domain': {'vehicle_id': [('owner_id', '=', rec.customer_id)]}}

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        for rec in self:
            if rec.vehicle_id:
                rec.engine_no=rec.vehicle_id.engine_no
                rec.chasis_no=rec.vehicle_id.chasis_no
                rec.insurance_company=rec.vehicle_id.insurance_company
                rec.insurance_validity=rec.vehicle_id.insurance_validity


    # Overriding the create method to assign sequence for the record
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('work.order') or _('New')
        result = super(WorkOrder, self).create(vals)
        return result

    @api.depends('vehicle_id')
    def set_odometer(self):
        if self.vehicle_id:
            self.last_odometer=self.vehicle_id.odometer

    @api.constrains('contact_person')
    def check_contact_name(self):
        if self.contact_person:
            for rec in self:
                if re.search(r'\d', rec.contact_person):
                    raise ValidationError(_('The Name of Contact Person cannot contain number'))

    @api.onchange('contact_person')
    def caps_contact_name(self):
        if self.contact_person:
            self.contact_person = str(self.contact_person).title()



# Fields for Customer
    name = fields.Char(string='Order ID', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New Workorder'))
    customer_id= fields.Many2one('res.partner',string='Customer',required=1,help='Customer Name',track_visibility='always')
    address= fields.Char(string='Address', track_visibility='always')
    contact_person= fields.Char(string='Contact Person', help='Contact Person',track_visibility='always')
    email= fields.Char(string='Email',readonly=0,track_visibility='always')
    mobile = fields.Char(string='Mobile No.', help='Ten Digit Mobile number',track_visibility='always')

# Fields for Vehicle
    vehicle_id = fields.Many2one('vehicle.create',string='Vehicle',required=1,help='Choose your Vehicle or Register your Vehicle',track_visibility='always')
    engine_no= fields.Char(string='Engine No.',readonly=0, track_visibility='always')
    chasis_no= fields.Char(string='Chasis No.',readonly=0, track_visibility='always')
    insurance_company = fields.Char(string="Insurance Company", readonly=0, track_visibility='always')
    insurance_validity = fields.Date(string="Valid Upto", readonly=0, track_visibility='always')
    last_odometer=fields.Float(string='Last Odometer',required=0, compute='set_odometer',help='Leave blank if it is your First Servicing')
    odometer=fields.Float(string='Current Odometer',required=1,help='Odometer Reading',track_visibility='always')

    #Fields for Servicing
    service_type = fields.Selection([
        ('paid', 'Paid Service'),
        ('free', 'Free Service'),
        ('pdi', 'Pre-delivery Inspection'),
        ('warranty', 'Warranty'),
        ('ssc', 'Special Service Campaign'),
        ('general', 'General Service')
    ], string='Service Type', track_visibility='always')

    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('Card', 'Card')
    ], string='Payment Method', track_visibility='always')

    date_in = fields.Date(string="Date In", track_visibility='always', default=datetime.today())
    date_out = fields.Date(string="Promise Del. Date", track_visibility='always')
    time = fields.Float(string='Time', track_visibility='always')
    order_lines = fields.One2many('work.order.lines', 'order_id', string='Order Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, default='draft')





class WorkOrderLines(models.Model):
    _name = 'work.order.lines'
    _description = 'Work Order Lines'

    product_id = fields.Many2one('product.product', string='Service')
    product_qty = fields.Integer(string="Quantity", default='1')
    product_price = fields.Float(string="Total Price", readonly='1')
    order_id = fields.Many2one('work.order', string='Order ID')

    @api.onchange('product_id')
    def _load_product_attributes(self):
        if not self.product_id:
            return {}

        for rec in self:
            rec.product_price = rec.product_id.product_tmpl_id.list_price
            rec._update_price_with_quantity()

    @api.onchange('product_qty')
    def _update_price_with_quantity(self):
       self.product_price = self.product_id.product_tmpl_id.list_price * self.product_qty

