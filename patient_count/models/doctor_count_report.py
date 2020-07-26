# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import drop_view_if_exists
from odoo.exceptions import Warning


class AccountCountReport(models.Model):
    _name = 'doctor.count.report'
    _auto = False
    _description = "Doctorwise patient count"

    count = fields.Integer(string="Count", readonly=True)
    date = fields.Date(string="Date", readonly=True)
    doctor_id = fields.Many2one('doctor.setup', string="Doctor")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'doctor_count_report')
        self.env.cr.execute("""
            create or replace view doctor_count_report as (
                select
                    concat(ail.doctor_id, '_', ai.date_invoice) as id,
                    ai.date_invoice as date,
                    ail.doctor_id as doctor_id,
                    count(*) as count
                from account_invoice ai, account_invoice_line ail
                where
                    ail.invoice_id = ai.id
                    and ai.type != 'out_refund'
                group by ail.doctor_id, ai.date_invoice
            )""")

    @api.multi
    def unlink(self):
        raise Warning('You cannot delete any record!')
