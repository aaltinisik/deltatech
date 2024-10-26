from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    expenses_deduction_id = fields.Many2one("deltatech.expenses.deduction", string="Expenses Deduction", required=False)

    def _seek_for_lines(self):
        liquidity_lines, counterpart_lines, writeoff_lines = super()._seek_for_lines()
        for line in self.move_id.line_ids:
            if not self.journal_id.account_cash_advances_id:
                raise UserError(_("The journal %s does not have an account for cash advances.") % self.journal_id.name)

            if line.account_id == self.journal_id.account_cash_advances_id:
                liquidity_lines += line
        return liquidity_lines, counterpart_lines, writeoff_lines
