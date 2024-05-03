# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details


from odoo import fields, models


class WizardDownloadFile(models.TransientModel):
    _name = "wizard.download.file"
    _description = "Download Wizard"

    file_name = fields.Char(string="File Name")
    data_file = fields.Binary(string="File")

    def do_download_file(self):
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content?model={self._name}&download=True&field=data_file&id={self.id}&filename={self.file_name}",
            "target": "new",
        }
