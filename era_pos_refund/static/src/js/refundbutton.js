odoo.define("era_pos_refund.RefundButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const RefundButton = require("point_of_sale.RefundButton");

    const PosRefundButton = (RefundButton) =>
        class extends RefundButton {
            get hasRefundAccess() {
                return this.env.pos.get_cashier().hasGroupRefund;
            }
        };

    Registries.Component.extend(RefundButton, PosRefundButton);

    return RefundButton;
});
