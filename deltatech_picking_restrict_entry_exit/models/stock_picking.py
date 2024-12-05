from odoo import _, api, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not self.env.user.has_group("deltatech_picking_restrict_entry_exit.group_picking_restrict_entry_exit"):
                picking_type = self.env["stock.picking.type"].browse(vals.get("picking_type_id"))
                if picking_type.code == "outgoing":
                    if not vals.get("sale_id"):
                        raise UserError(_("You cannot create an outgoing picking without a source sale order."))
                elif picking_type.code == "incoming":
                    if not vals.get("purchase_id"):
                        raise UserError(_("You cannot create an incoming picking without a source purchase order."))

        return super().create(vals_list)

    # self.env.user.has_group("deltatech_picking_restrict_entry_exit.group_picking_restrict_entry_exit")
    def button_validate(self):
        for picking in self:
            picking_type = picking.picking_type_id
            for move in picking.move_ids:
                if picking_type.code == "outgoing":
                    if not move.sale_line_id:
                        raise UserError(
                            _(
                                "You cannot validate the picking because the product %s is not linked to a sale order line."
                            )
                            % move.product_id.display_name
                        )
                elif picking_type.code == "incoming":
                    if not move.purchase_line_id:
                        raise UserError(
                            _(
                                "You cannot validate the picking because the product %s is not linked to a purchase order line."
                            )
                            % move.product_id.display_name
                        )
                if move.quantity > move.product_uom_qty:
                    raise UserError(
                        _(
                            "You cannot validate the picking because the quantity done is greater than the quantity ordered for the product %s."
                        )
                        % move.product_id.display_name
                    )

        return super().button_validate()
