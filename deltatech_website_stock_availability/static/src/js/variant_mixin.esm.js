/** @odoo-module **/

import VariantMixin from "@website_sale/js/sale_variant_mixin";
import publicWidget from "@web/legacy/js/public/public_widget";
import {renderToFragment} from "@web/core/utils/render";
import "@website_sale/js/website_sale";

VariantMixin._onChangeLeadTimeMessage = function (ev, $parent, combination) {
    let product_id = 0;
    // Needed for list view of variants
    if ($parent.find("input.product_id:checked").length) {
        product_id = $parent.find("input.product_id:checked").val();
    } else {
        product_id = $parent.find(".product_id").val();
    }
    const isMainProduct =
        combination.product_id &&
        ($parent.is(".js_main_product") || $parent.is(".main_product")) &&
        combination.product_id === parseInt(product_id, 10);

    if (!this.isWebsite || !isMainProduct) {
        return;
    }

    const $addQtyInput = $parent.find('input[name="add_qty"]');
    const qty = $addQtyInput.val();
    combination.selected_qty = qty;

    $(".oe_website_sale")
        .find(".lead_time_messages_" + combination.product_template)
        .remove();
    const $message = $(renderToFragment("deltatech_website_stock_availability.lead_time", combination));
    $("div.lead_time_messages").html($message);
};

publicWidget.registry.WebsiteSale.include({
    /**
     * Update the renting text when the combination change.
     * @override
     */
    _onChangeCombination: function () {
        this._super.apply(this, arguments);
        VariantMixin._onChangeLeadTimeMessage.apply(this, arguments);
    },
});

export default VariantMixin;
