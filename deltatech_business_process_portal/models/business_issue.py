# ©  2023 Deltatech
# See README.rst file on addons root folder for license details


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BusinessIssue(models.Model):
    _name = "business.issue"
    _inherit = ["portal.mixin", "business.issue"]

    def send_mail(self):
        if self.env.user.has_group("base.group_portal"):
            return self.sudo().send_mail()
        return super().send_mail()
