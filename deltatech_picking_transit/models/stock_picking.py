# models/stock_picking.py

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_transit_transfer = fields.Boolean(default=False, compute="_compute_is_transit_transfer")
    sub_location_existent = fields.Boolean(default=False, compute="_compute_sub_location_existent")
    second_transfer_created = fields.Boolean(default=False)
    source_transfer_id = fields.Many2one("stock.picking")

    def open_transfer_wizard(self):
        if self.second_transfer_created:
            raise UserError(_("Second transfer already created."))
        return {
            "name": "Create Transfer",
            "type": "ir.actions.act_window",
            "res_model": "stock.picking.transfer.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_picking_id": self.id},
        }

    def create_second_transfer_wizard(self, final_dest_location_id, picking_type_id):
        for picking in self:
            if picking.picking_type_id.code == "internal":
                new_picking_vals = {
                    "picking_type_id": picking_type_id.id,
                    "location_id": picking.location_dest_id.id,
                    "location_dest_id": final_dest_location_id.id,
                    "move_ids_without_package": [],
                }
                new_picking = self.env["stock.picking"].create(new_picking_vals)
                self.copy_move_lines(picking, new_picking)
                new_picking.action_confirm()
                # new_picking.action_assign()
                # new_picking.do_unreserve()
                self.second_transfer_created = True

                message = _("This transfer was generated from %s.") % picking.name
                new_picking.message_post(body=message)
                new_picking.source_transfer_id = picking.id
                message = _("Transfer %s was generated.") % new_picking.name

                picking.message_post(body=message)

                return new_picking

    def copy_move_lines(self, source_picking, target_picking):
        for move in source_picking.move_ids_without_package:
            move.copy(
                {
                    "picking_id": target_picking.id,
                    "location_id": source_picking.location_dest_id.id,
                    "location_dest_id": target_picking.location_dest_id.id,
                    "state": "draft",
                }
            )

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     if res.picking_type_id.code == "internal" and res.picking_type_id.next_operation_id:
    #         res.action_toggle_is_locked()
    #        # res.immediate_transfer = False
    #     return res

    def _compute_sub_location_existent(self):
        for record in self:
            sub_location_usage = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(key="deltatech_picking_transit.use_sub_locations", default=False)
            )
            if sub_location_usage and self.picking_type_id.code == "internal":
                record.sub_location_existent = True
            else:
                record.sub_location_existent = False

    def reassign_location(self):
        for move_line in self.move_line_ids:
            quants = self.env["stock.quant"].search(
                [
                    ("product_id", "=", move_line.product_id.id),
                    ("location_id", "child_of", self.location_id.id),
                    ("quantity", ">", 0.0),
                ]
            )
            if quants:
                move_line.location_id = quants[0].location_id

    @api.onchange("picking_type_id")
    def _compute_is_transit_transfer(self):
        for record in self:
            if self.second_transfer_created:
                record.is_transit_transfer = False
                return
            if record.picking_type_id.code == "internal" and record.picking_type_id.two_step_transfer_use == "delivery":
                record.is_transit_transfer = True
                record.action_toggle_is_locked()
            # record.immediate_transfer = False
            else:
                record.is_transit_transfer = False

    def button_validate(self):
        for picking in self:
            if picking.source_transfer_id:
                for move in picking.move_ids_without_package:
                    other_moves = picking.source_transfer_id.move_ids_without_package.filtered(
                        lambda x: x.product_id == move.product_id
                    )
                    if not other_moves:
                        raise UserError(_("You cannot validate the picking because the product %s is not from the source picking") % move.product_id.display_name)
        return super().button_validate()
