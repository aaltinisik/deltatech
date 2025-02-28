# ©  2024 Deltatech
# See README.rst file on addons root folder for license details


from odoo import models
from odoo.tools.float_utils import float_round


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _pre_put_in_pack_hook(self, move_line_ids):
        res = super()._pre_put_in_pack_hook(move_line_ids)
        for ml in move_line_ids:
            if not ml.move_id.product_packaging_id:
                continue
            product_packaging = ml.move_id.product_packaging_id

            packaging_uom = product_packaging.product_uom_id

            packaging_qty = float_round(ml.qty_done / product_packaging.qty, precision_rounding=packaging_uom.rounding)
            qty_done = ml.qty_done
            if packaging_qty > 1:
                package = self.env["stock.quant.package"].create(
                    {
                        "package_type_id": product_packaging.package_type_id.id,
                    }
                )
                ml.write(
                    {
                        "qty_done": product_packaging.qty,
                        "reserved_uom_qty": product_packaging.qty,
                        "result_package_id": package.id,
                    }
                )
                new_move_line = self.env["stock.move.line"]
                for _i in range(int(packaging_qty) - 1):
                    package = self.env["stock.quant.package"].create(
                        {
                            "package_type_id": product_packaging.package_type_id.id,
                        }
                    )
                    new_move_line = ml.copy(default={"reserved_uom_qty": 0, "qty_done": 0.0})
                    new_move_line.write(
                        {
                            "qty_done": product_packaging.qty,
                            "reserved_uom_qty": product_packaging.qty,
                            "result_package_id": package.id,
                        }
                    )
                diff = qty_done - (packaging_qty * product_packaging.qty)
                if new_move_line and diff:
                    new_move_line.write(
                        {
                            "qty_done": diff,
                            "reserved_uom_qty": diff,
                        }
                    )

        return res
