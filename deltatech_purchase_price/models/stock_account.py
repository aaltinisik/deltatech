# ©  2015-2018 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

from odoo import api, models
from odoo.tools import safe_eval


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def _get_price_unit(self):
        """ Returns the unit price to store on the quant """
        if self.purchase_line_id:
            get_param = self.env["ir.config_parameter"].sudo().get_param

            update_product_price = safe_eval(get_param("purchase.update_product_price", default="True"))

            # este neidicat de a se forta actualizarea pretului standard
            update_standard_price = safe_eval(get_param("purchase.update_standard_price", default="False"))

            price_unit = self.purchase_line_id.with_context(date=self.date)._get_stock_move_price_unit()
            self.product_id.write({"last_purchase_price": price_unit})
            self.write({"price_unit": price_unit})  # mai trebuie sa pun o conditie de status ?
            # update price form last receipt
            # from_currency = self.purchase_line_id.order_id.currency_id or self.env.user.company_id.currency_id
            from_currency = self.env.user.company_id.currency_id

            for seller in self.product_id.seller_ids:
                if seller.name == self.purchase_line_id.order_id.partner_id:
                    if seller.min_qty == 0.0 and seller.date_start is False and seller.date_end is False:
                        # conversia ar trebui deja sa fie facuta de _get_stock_move_price_unit()
                        to_currency = seller.currency_id or self.env.user.company_id.currency_id
                        seller_price_unit = from_currency.compute(price_unit, to_currency)
                        # seller_price_unit = price_unit
                        if update_product_price:
                            seller.write({"price": seller_price_unit})

            # pretul standard se actualizeaza prin rutinele standard. Aici este o fortare pe ultimul pret
            if update_standard_price:
                self.product_id.write({"standard_price": price_unit})

            return price_unit

        return super(StockMove, self)._get_price_unit()

    @api.multi
    def product_price_update_before_done(self, forced_qty=None):

        super(StockMove, self.with_context(force_fifo_to_average=True)).product_price_update_before_done(forced_qty)
