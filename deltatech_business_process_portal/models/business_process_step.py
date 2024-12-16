# ©  2023 Deltatech
# See README.rst file on addons root folder for license details

from odoo import api, fields, models


class BusinessProcessStep(models.Model):
    _name = "business.process.step"
    _inherit = ["portal.mixin", "business.process.step"]
