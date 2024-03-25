odoo.define('pos_closing_report.SalesDetailsReport', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { renderToString } = require('@web/core/utils/render');
    const SaleDetailsButton = require('point_of_sale.SaleDetailsButton');

    console.log("YOU ARE HERE ?")
    const SaleDetailsButtonCustom = (SaleDetailsButton) =>
    class extends SaleDetailsButton {
        constructor() {
				super(...arguments);
			}
        async onClick() {
            console.log("HERE")
            // IMPROVEMENT: Perhaps put this logic in a parent component
            // so that for unit testing, we can check if this simple
            // component correctly triggers an event.
            const saleDetails = await this.rpc({
                model: 'report.point_of_sale.report_saledetails',
                method: 'get_pos_sale_details',
                args: [[this.env.pos.pos_session.id]],
            });
            console.log("saleDetails ==",saleDetails)
            const report = renderToString(
                'SaleDetailsReport',
                Object.assign({}, saleDetails, {
                    date: new Date().toLocaleString(),
                    pos: this.env.pos,
                })
            );
            console.log("report ==",report)
            const printResult = await this.env.proxy.printer.print_receipt(report);
            if (!printResult.successful) {
                await this.showPopup('ErrorPopup', {
                    title: printResult.message.title,
                    body: printResult.message.body,
                });
            }
        }
    }


    Registries.Component.extend(SaleDetailsButton, SaleDetailsButtonCustom);


    return SaleDetailsButtonCustom;
});
