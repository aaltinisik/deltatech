odoo.define("deltatech_pos_decimal_numpad_dot.NumberBuffer", function (require) {
    "use strict";

    const NumberBuffer = require("point_of_sale.NumberBuffer");

    NumberBuffer._onKeyboardInput = function (event) {
        var keyAccessor = (e) => e.key;
        if (event.code === "NumpadDecimal") {
            event.decimalPoint = this.decimalPoint;
            keyAccessor = (e) => e.decimalPoint;
        }
        return this._bufferEvents(this._onInput(keyAccessor))(event);
    };
});
