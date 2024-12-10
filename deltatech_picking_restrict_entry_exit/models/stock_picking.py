from odoo import _, api, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(
        self, vals_list
    ):
        # this should restrict users from creating delivery/receipts manually, they should only be created from sale/purchase orders
        for vals in vals_list:
            # there are users that can create picking without sale/purchase order if they have the group
            if not self.env.user.has_group("deltatech_picking_restrict_entry_exit.group_picking_restrict_entry_exit"):
                picking_type = self.env["stock.picking.type"].browse(vals.get("picking_type_id"))
                # returns and backorders are not restricted because they don't come with sale_id or purchase_id, don't know the back orders is not associated
                if not vals.get("return_id", False) and not vals.get("backorder_id", False):
                    if picking_type.code == "outgoing":
                        if not vals.get("sale_id"):
                            raise UserError(_("You cannot create an outgoing picking without a source sale order."))
                    elif picking_type.code == "incoming":
                        if not vals.get("purchase_id"):
                            raise UserError(_("You cannot create an incoming picking without a source purchase order."))

        return super().create(vals_list)

    # self.env.user.has_group("deltatech_picking_restrict_entry_exit.group_picking_restrict_entry_exit")
    def button_validate(self):
        for picking in self:  # this should restrict validation of delivery/receipts with unaccounted lines or with quantities greater than ordered
            if not self.return_id and not self.backorder_id:  # again returns and backorders are not restricted
                if not self.env.user.has_group(
                    "deltatech_picking_restrict_entry_exit.group_picking_restrict_entry_exit"
                ):
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

    def write(self, vals):
        if "move_ids_without_package" in vals:  # client wanted the same check on validation to be done on saving too
            for move_data in vals["move_ids_without_package"]:  # we check if the lines were touched
                if len(move_data) > 2 and "quantity" in move_data[2]:
                    move_id = move_data[1]
                    if (
                        isinstance(move_id, str) and "virtual" in move_id
                    ):  # if the line contains virtual, it means it's a new line and we check it differently
                        if self.picking_type_code in ["incoming", "outgoing"] and not self.env.user.has_group(
                            "deltatech_picking_restrict_entry_exit.group_picking_restrict_entry_exit"
                        ):  # we check if the picking is incoming/outgoing, if yes we restrict creation
                            raise UserError(_("You can't manually add moves to an incoming/outgoing picking"))
                        else:  # if it is not incoming/outgoing, we check if the quantity is greater than the ordered quantity
                            if move_data[2]["quantity"] > move_data[2]["product_uom_qty"]:
                                raise UserError(
                                    _(
                                        "You can't add a line where the quantity done is greater than the quantity needed"
                                    )
                                )
                    else:  # this is for existing lines and we do the same check as in the validation
                        quantity = move_data[2]["quantity"]
                        move = self.env["stock.move"].browse(move_id)
                        if quantity > move.product_uom_qty:
                            raise UserError(
                                _(
                                    "You cannot save the picking because the quantity done is greater than the quantity ordered for the product %s."
                                )
                                % move.product_id.display_name
                            )
        return super().write(vals)
        # for picking in self:# additional check from previous version, not sure if it's needed but shouldn't cause any issues
        #     if not self.return_id and not self.backorder_id:
        #         picking_type = picking.picking_type_id
        #         for move in picking.move_ids:
        #             if picking_type.code == "outgoing":
        #                 if not move.sale_line_id:
        #                     raise UserError(
        #                         _(
        #                             "You cannot save the picking because the product %s is not linked to a sale order line."
        #                         )
        #                         % move.product_id.display_name
        #                     )
        #             elif picking_type.code == "incoming":
        #                 if not move.purchase_line_id:
        #                     raise UserError(
        #                         _(
        #                             "You cannot save the picking because the product %s is not linked to a purchase order line."
        #                         )
        #                         % move.product_id.display_name
        #                     )
