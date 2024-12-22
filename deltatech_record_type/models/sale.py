# ©  2024 Terrabit Solutions
#              Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):
    _inherit = "sale.order"

    so_type = fields.Many2one("record.type", string="Order Type", tracking=True)

    @api.onchange("so_type")
    def _onchange_so_type(self):
        for default_value in self.so_type.default_values_ids:
            self[default_value.field_name] = safe_eval(default_value.field_value)
