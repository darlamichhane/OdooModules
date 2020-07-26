from odoo import models, fields, api,  _
from datetime import datetime
from odoo.exceptions import ValidationError
import re


class WorkOrder(models.Model):
    _name = 'job.order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Job Order for Vehicle Servicing'
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
            vals['name'] = self.env['ir.sequence'].next_by_code('job.order') or _('New')
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
    name = fields.Char(string='Order ID', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New Joborder'))
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
    last_odometer=fields.Float(string='Last Odometer Reading',required=0, compute='set_odometer',help='Leave blank if it is your First Servicing')
    odometer=fields.Float(string='Current Odometer Reading',required=1,help='Odometer Reading',track_visibility='always')

# Field for Multi-company
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)

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
    time = fields.Float(string='Delivery Time', track_visibility='always')

    #Instruction Fields
    job_instruction = fields.Text(string="Job Instruction", track_visibility='always')
    technician_report = fields.Text(string="Technician Report", track_visibility='always', default="\n\n")

    additional_job = fields.Text(string="Additional Job",track_visibility='always')
    revised_del_date = fields.Date(string="Revised Del. Date", track_visibility='always')

    ordered_part_lines = fields.One2many('part.order.lines', 'order_id', string=' Ordered Part Lines')

    #Fields for Technician
    technician_id = fields.Many2one('hr.employee', string="Responsible Technician", track_visibility='always')
    job_start_time = fields.Datetime(string="Job Start Time", track_visibility='always')
    job_completion_time = fields.Datetime(string="Job Completion Time", track_visibility='always')
    recommendation = fields.Text(string="Recommendation", track_visibility='always')

    #Fields for Supervisor and Inspector
    job_taking_supervisor_id = fields.Many2one('hr.employee', string="Job Taken By", track_visibility='always')
    final_inspecting_supervisor_id = fields.Many2one('hr.employee', string="Final Inspection Done By", track_visibility='always')

    supervisor_remarks = fields.Text(string="Remarks (if Any)", track_visibility='always')
    inspector_remarks = fields.Text(string="Remarks (if Any)", track_visibility='always')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, default='draft')



class OrderedPartLines(models.Model):
    _name = 'part.order.lines'
    _description = 'Parts Order Lines'

    part_id = fields.Many2one('product.product', string='Parts Name')
    order_id = fields.Many2one('job.order', string='Order ID')






    # order_lines = fields.One2many('job.order.lines', 'order_id', string='Order Lines')


# class WorkOrderLines(models.Model):
#     _name = 'job.order.lines'
#     _description = 'Job Order Lines'
#
#     instruction = fields.Char(string='Job Instruction')
#     product_qty = fields.Integer(string="Quantity", default='1')
#     product_price = fields.Float(string="Total Price", readonly='1')
#     order_id = fields.Many2one('job.order', string='Order ID')
#
#     @api.onchange('product_id')
#     def _load_product_attributes(self):
#         if not self.product_id:
#             return {}
#
#         for rec in self:
#             rec.product_price = rec.product_id.product_tmpl_id.list_price
#             rec._update_price_with_quantity()
#
#     @api.onchange('product_qty')
#     def _update_price_with_quantity(self):
#        self.product_price = self.product_id.product_tmpl_id.list_price * self.product_qty

