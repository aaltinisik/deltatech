from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    # @api.model
    # def create(self, vals):
    #     if vals.get("picking_id"):
    #         picking = self.env["stock.picking"].browse(vals["picking_id"])
    #         if picking.second_transfer_created and picking.picking_type_id.code != "return":
    #             raise UserError(
    #                 _("You can't add another move to this picking because the second transfer is already created.")
    #             )
    #     res = super().create(vals)
    #     return res
