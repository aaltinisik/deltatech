# ©  2023 Deltatech
# See README.rst file on addons root folder for license details


from odoo import api, fields, models


class BusinessDevelopment(models.Model):
    _name = "business.development"
    _inherit = ["portal.mixin", "business.development"]
