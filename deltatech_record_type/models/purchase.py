# ©  2024 Terrabit Solutions
#              Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):
    _inherit = "purchase.order"

    po_type = fields.Many2one("record.type", string="Order Type", tracking=True)

    @api.onchange("po_type")
    def _onchange_po_type(self):
        for default_value in self.po_type.default_values_ids:
            self[default_value.field_name] = safe_eval(default_value.field_value)
