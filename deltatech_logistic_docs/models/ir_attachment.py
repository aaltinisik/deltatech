# ©  2008-2022 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def button_download(self):
        if self.name.endswith(".zplpdf"):
            self.sudo().write({"mimetype": "application/raw"})
        return {
            "type": "ir.actions.act_url",
            # "url": f"/web/content?model={self._name}&download=True&field=datas&id={self.id}&filename={self.name}",
            "url": f"/web/content/{self.id}/{self.name}",
            "target": "new",
        }
