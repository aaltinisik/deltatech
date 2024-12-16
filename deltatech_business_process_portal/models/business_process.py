# ©  2023 Deltatech
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BusinessProcess(models.Model):
    _name = "business.process"
    _inherit = ["portal.mixin", "business.process"]
