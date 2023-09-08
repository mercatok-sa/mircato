odoo.define('qerp_whatsapp_pos.ClientDetailsEdit', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit')
    /**
     * @prop {'quantiy' | 'price' | 'discount'} activeMode
     * @event set-numpad-mode - triggered when mode button is clicked
     * @event numpad-click-input - triggered when numpad button is clicked
     *
     * IMPROVEMENT: Whenever new-orderline-selected is triggered,
     * numpad mode should be set to 'quantity'. Now that the mode state
     * is lifted to the parent component, this improvement can be done in
     * the parent component.
     */
    class MyClientDetailsEdit extends ClientDetailsEdit {


        mounted() {
            // IMPROVEMENT: This listener shouldn't be here because in core point_of_sale
            // there is no way of changing the cashier. Only when pos_hr is installed
            // that this listener makes sense.
//            this.env.pos.on('change:cashier', () => {
//                if (!this.hasPriceControlRights && this.props.activeMode === 'price') {
//                    this.trigger('set-numpad-mode', { mode: 'quantity' });
//                }
//            });
console.log('asadasd');
        }
        async saveChanges(event) {
        console.log('saveChanges')
        }
                    try {
                    console.log(event.detail.processedChanges);
                        let partnerId = await this.rpc({
                            model: 'res.partner',
                            method: 'create_from_ui',
                            args: [event.detail.processedChanges],
                        });
                        await this.env.pos.load_new_partners();
                        this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
                        this.state.detailIsShown = false;
                        this.render();
                    } catch (error) {
                        if (isConnectionError(error)) {
                            await this.showPopup('OfflineErrorPopup', {
                                title: this.env._t('Offline'),
                                body: this.env._t('Unable to save changes.'),
                            });
                        } else {
                            throw error;
                        }
                    }
                }

    Registries.Component.add(MyClientDetailsEdit);

    return MyClientDetailsEdit;
});
