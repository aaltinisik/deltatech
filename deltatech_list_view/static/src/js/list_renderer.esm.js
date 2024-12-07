/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {ListRenderer} from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, {
    onCellClicked() {
        if (this.getSelectedText() === "") {
            super.onCellClicked(...arguments);
        }
    },

    getSelectedText() {
        if (window.getSelection) {
            return window.getSelection().toString();
        } else if (document.selection) {
            return document.selection.createRange().text;
        }
        return "";
    },
});
