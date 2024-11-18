from odoo import _, api, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list_here = [vals_list]
        for vals in vals_list_here:
            picking_type = self.env["stock.picking.type"].browse(vals.get("picking_type_id"))
            group = self.env.ref("deltatech_picking_restrict_entry_exit.group_picking_restrict_entry_exit")
            if picking_type.code in ["incoming", "outgoing"]:
                if not vals.get("origin") and group not in self.env.user.groups_id:
                    raise UserError(
                        _("You can't create a receipt/delivery picking without a purchase/sale source document.")
                    )
        return super().create(vals_list)

    def button_validate(self):
        for picking in self:
            if picking.picking_type_id.code in ["incoming", "outgoing"]:
                for move in picking.move_ids:
                    if move.quantity > move.product_uom_qty:
                        raise UserError(
                            _(
                                "You cannot validate the picking because the quantity done is greater than the quantity ordered for the product %s."
                            )
                            % move.product_id.display_name
                        )
        return super().button_validate()
