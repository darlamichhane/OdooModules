# -*- coding: utf-8 -*-

import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from odoo.tools import amount_to_text_en

from odoo.exceptions import UserError, RedirectWarning, ValidationError

import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    requisition_id = fields.Many2one('requisition.form', string='Add Requisition Order',
        help='Encoding help. When selected, the associated requisition form lines are added to the stock picking.')

    @api.onchange('state', 'move_lines')
    def _onchange_allowed_requisition_ids(self):
        '''The purpose of the method is to define a domain for the available requisition forms.'''
        result = {}
        domain = [('transfer_status', '=', 'to transfer')]
        result['domain'] = {'requisition_id': domain}
        return result

    @api.onchange('requisition_id')
    def onchange_requisition(self):
        if not self.requisition_id:
            return {}
        for rec in self:
            lines=[]
            for line in self.requisition_id.form_line:
                vals = {
                    'product_id': line.product_id,
                    'product_uom_qty': line.product_uom_qty,
                    'state': 'draft',
                    'product_uom': line.product_id.product_tmpl_id.uom_id,
                    'location_dest_id': self.location_dest_id,
                    'location_id': self.location_id,
                    'requisition_id': line.id,
                    'picking_type_id': self.picking_type_id.id,
                    'name': line.product_id.product_tmpl_id.name,
                    'create_date': datetime.now(),
                    'date_expected': datetime.now(),

                }
#                 _logger.error('%s', vals)
                lines.append((vals))
            rec.move_lines = lines
            self.requisition_id = False
            return {}
#             _logger.error('%s', lines)

    @api.multi
    def do_transfer(self):
        """ If no pack operation, we do simple action_done of the picking.
        Otherwise, do the pack operations. """
        # TDE CLEAN ME: reclean me, please
        self._create_lots_for_picking()

        no_pack_op_pickings = self.filtered(lambda picking: not picking.pack_operation_ids)
        no_pack_op_pickings.action_done()
        other_pickings = self - no_pack_op_pickings
        for picking in other_pickings:
            need_rereserve, all_op_processed = picking.picking_recompute_remaining_quantities()
            todo_moves = self.env['stock.move']
            toassign_moves = self.env['stock.move']

            # create extra moves in the picking (unexpected product moves coming from pack operations)
            if not all_op_processed:
                todo_moves |= picking._create_extra_moves()

            if need_rereserve or not all_op_processed:
                moves_reassign = any(x.origin_returned_move_id or x.move_orig_ids for x in picking.move_lines if x.state not in ['done', 'cancel'])
                if moves_reassign and picking.location_id.usage not in ("supplier", "production", "inventory"):
                    # unnecessary to assign other quants than those involved with pack operations as they will be unreserved anyways.
                    picking.with_context(reserve_only_ops=True, no_state_change=True).rereserve_quants(move_ids=picking.move_lines.ids)
                picking.do_recompute_remaining_quantities()

            # split move lines if needed
            for move in picking.move_lines:
                rounding = move.product_id.uom_id.rounding
                remaining_qty = move.remaining_qty
                if move.state in ('done', 'cancel'):
                    # ignore stock moves cancelled or already done
                    continue
                elif move.state == 'draft':
                    toassign_moves |= move
                if float_compare(remaining_qty, 0,  precision_rounding=rounding) == 0:
                    if move.state in ('draft', 'assigned', 'confirmed'):
                        todo_moves |= move
                elif float_compare(remaining_qty, 0, precision_rounding=rounding) > 0 and float_compare(remaining_qty, move.product_qty, precision_rounding=rounding) < 0:
                    # TDE FIXME: shoudl probably return a move - check for no track key, by the way
                    new_move_id = move.split(remaining_qty)
                    new_move = self.env['stock.move'].with_context(mail_notrack=True).browse(new_move_id)
                    todo_moves |= move
                    # Assign move as it was assigned before
                    toassign_moves |= new_move

            # TDE FIXME: do_only_split does not seem used anymore
            if todo_moves and not self.env.context.get('do_only_split'):
                todo_moves.action_done()
            elif self.env.context.get('do_only_split'):
                picking = picking.with_context(split=todo_moves.ids)

            picking._create_backorder()

            for lines in self:
                req_obj = self.env['requisition.form'].search([('id', '=', lines.requisition_id.id)])
                if self.requisition_id:
                    req_obj.transfer_status = 'transferred'
                _logger.error('%s', req_obj)
                _logger.error('%s', lines)
        return True

    @api.onchange('requisition_id')
    def _onchange_origin(self):
        for rec in self:
            rec.origin = rec.requisition_id.name


class StockMoveInherited(models.Model):
    _inherit = 'stock.move'

    on_hand_stock = fields.Float(string="On Hand Stock", compute="_compute_on_hand_total")
    remaining_stock = fields.Float(string="Remaining Stock", compute="_compute_on_hand_total")

    @api.depends('product_id', 'product_uom_qty')
    def _compute_on_hand_total(self):
        for record in self:
            if record.product_id and record.state != 'done':
                actual_qty = record.product_id.with_context(
                    {'location': record.location_id.id}).qty_available
                outgoing_qty = record.product_id.with_context(
                    {'location': record.location_id.id}).outgoing_qty
                record.on_hand_stock = actual_qty - outgoing_qty
                record.remaining_stock = record.on_hand_stock - record.product_uom_qty
