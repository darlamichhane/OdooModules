from odoo import api, fields, models, _
import base64
import json
import logging

_logger = logging.getLogger(__name__)


class pos_config(models.Model):
    _inherit = "pos.config"

    order_note = fields.Boolean('Remarks', default=1)
    print_notes = fields.Boolean('Print Notes on Receipt', default=1)