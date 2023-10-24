// This Function is used to prevent add the new product in the Refund order in POS.
odoo.define('disable_price_discount.TicketScreen_Popup', function (require) {
    'use strict';
    const ProductScreen = require('point_of_sale.ProductScreen');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const {
        useListener
    } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const {
        onChangeOrder,
        useBarcodeReader
    } = require('point_of_sale.custom_hooks');
    const {
        isConnectionError,
        posbus
    } = require('point_of_sale.utils');
    const {
        useState,
        onMounted
    } = owl.hooks;
    const {
        parse
    } = require('web.field_utils');
    const PosProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _clickProduct(event) {
                if (this.currentOrder.getHasRefundLines()) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Invalid action'),
                        body: this.env._t('You are not allowed to add this quantity in Refund Order'),
                    });
                    return false;
                }
                if (!this.currentOrder) {
                    this.env.pos.add_new_order();
                }
                const product = event.detail;
                const options = await this._getAddProductOptions(product);
                // Do not add product if options is undefined.
                if (!options) return;
                // Add the product after having the extra information.
                this.currentOrder.add_product(product, options);
                NumberBuffer.reset();
            }
            async _onClickPay(event) {
                if (this.currentOrder.getHasRefundLines() && this.env.pos.get_order().orderlines.any(line => line.get_quantity() > 0)) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Invalid action'),
                        body: this.env._t('You are not allowed to add normal quantity in Refund Order'),
                    });
                    return false;
                }
                if (this.env.pos.get_order().orderlines.any(line => line.get_product().tracking !== 'none' && !line.has_valid_product_lot() && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots))) {
                    const {
                        confirmed
                    } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Some Serial/Lot Numbers are missing'),
                        body: this.env._t('You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?'),
                        confirmText: this.env._t('Yes'),
                        cancelText: this.env._t('No')
                    });
                    if (confirmed) {
                        this.showScreen('PaymentScreen');
                    }
                } else {
                    this.showScreen('PaymentScreen');
                }
            }
        };
    Registries.Component.extend(ProductScreen, PosProductScreen);
    return ProductScreen;
});


odoo.define('disable_price_discount.HeaderButton', function (require) {
    'use strict';

    const HeaderButton = require('point_of_sale.HeaderButton')
    const {
        useState,
        useRef
    } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const PosComponent = require('point_of_sale.PosComponent');
    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const CashOpeningPopup = require('point_of_sale.CashOpeningPopup');
    const Registries = require('point_of_sale.Registries');


    const PosHeaderButton = (HeaderButton) =>
        class extends HeaderButton {


            constructor() {
                super(...arguments);
                this.manualInputCashCount = false;
                this.cashControl = this.env.pos.config.cash_control;
                this.moneyDetailsRef = useRef('moneyDetails');
                this.closeSessionClicked = false;
                this.moneyDetails = null;
                this.state = useState({});
            }



            // hasDifference() {

            //     console.log("hasDifference SSSSSSSSSSSSSSSSSSSSSSSS****************************")
            //     return Object.entries(this.state.payments).find(pm => pm[1].difference != 0);
            // }

            // canCloseSession() {
            //     return !this.cashControl || !this.hasDifference() || this.state.acceptClosing;
            // }
            async willStart() {
                try {
                    const closingData = await this.rpc({
                        model: 'pos.session',
                        method: 'get_closing_control_data',
                        args: [
                            [this.env.pos.pos_session.id]
                        ]
                    });
                    this.ordersDetails = closingData.orders_details;
                    this.paymentsAmount = closingData.payments_amount;
                    this.payLaterAmount = closingData.pay_later_amount;
                    this.openingNotes = closingData.opening_notes;
                    this.defaultCashDetails = closingData.default_cash_details;
                    this.otherPaymentMethods = closingData.other_payment_methods;
                    this.isManager = closingData.is_manager;
                    this.amountAuthorizedDiff = closingData.amount_authorized_diff;

                    // component state and refs definition
                    const state = {
                        notes: '',
                        acceptClosing: false,
                        payments: {}
                    };
                    if (this.cashControl) {
                        console.log("=-=-=-=-acceptClosing>>>>>>>>>>>>>>>>>", state)
                        state.payments[this.defaultCashDetails.id] = {
                            counted: 0,
                            difference: 0,
                            number: 0
                        };
                    }
                    console.log("base==========================")
                    if (this.otherPaymentMethods.length > 0) {
                        this.otherPaymentMethods.forEach(pm => {
                            if (pm.type === 'bank') {
                                state.payments[pm.id] = {
                                    counted: this.env.pos.round_decimals_currency(pm.amount),
                                    difference: 0,
                                    number: pm.number
                                }
                            }
                        })
                    }
                    Object.assign(this.state, state);
                } catch (error) {
                    this.error = error;
                }
            }
            async onClick() {


                const closingData = await this.rpc({
                    model: 'pos.session',
                    method: 'get_closing_control_data',
                    args: [
                        [this.env.pos.pos_session.id]
                    ]
                });


                console.log("canCloseSessionAAAAAAAAAAAAAAAAAAA-----------------------", this.moneyDetailsRef)
                // console.log("~~~~~my module js ",this.state.payments[this.defaultCashDetails.id].counted)
                if (!this.closeSessionClicked) {
                    this.closeSessionClicked = true;
                    this.defaultCashDetails = closingData.default_cash_details;
                    this.otherPaymentMethods = closingData.other_payment_methods;
                    let response;

                    if (this.cashControl) {

                        response = await this.rpc({

                            model: 'pos.session',
                            method: 'post_closing_cash_details',
                            args: [this.env.pos.pos_session.id],
                            kwargs: {
                                counted_cash: this.defaultCashDetails.amount,
                            }
                        })
                        if (!response.successful) {
                            return this.handleClosingError(response);
                        }
                    }
                    console.log("&&&&&&&&&&&&&this.modsfsfss-----neyDetailsRef&", closingData.default_cash_details)
                    await this.rpc({
                        model: 'pos.session',
                        method: 'update_closing_control_state_session',
                        args: [this.env.pos.pos_session.id, this.state.notes]
                    })
                    try {
                        console.log("=-=-=-============================", this.state)
                        const bankPaymentMethodDiffPairs = this.otherPaymentMethods.filter((pm) => pm.type == 'bank').map((pm) => [pm.id, this.state.payments[pm.id].difference]);

                        response = await this.rpc({
                            model: 'pos.session',
                            method: 'close_session_from_ui',
                            args: [this.env.pos.pos_session.id, bankPaymentMethodDiffPairs],
                        });
                        if (!response.successful) {
                            return this.handleClosingError(response);
                        }
                        window.location = '/web#action=point_of_sale.action_client_pos_menu';
                    } catch (error) {
                        const iError = identifyError(error);
                        if (iError instanceof ConnectionLostError || iError instanceof ConnectionAbortedError) {
                            await this.showPopup('ErrorPopup', {
                                title: this.env._t('Network Error'),
                                body: this.env._t('Cannot close the session when offline.'),
                            });
                        } else {
                            await this.showPopup('ErrorPopup', {
                                title: this.env._t('Closing session error'),
                                body: this.env._t(
                                    'An error has occurred when trying to close the session.\n' +
                                    'You will be redirected to the back-end to manually close the session.')
                            })
                            window.location = '/web#action=point_of_sale.action_client_pos_menu';
                        }
                    }
                    this.closeSessionClicked = false;
                }
            }
            async handleClosingError(response) {
                await this.showPopup('ErrorPopup', {
                    title: 'Error',
                    body: response.message
                });
                if (response.redirect) {
                    window.location = '/web#action=point_of_sale.action_client_pos_menu';
                }
            }


        }
    HeaderButton.template = 'HeaderButton';
    Registries.Component.extend(HeaderButton, PosHeaderButton, ClosePosPopup, CashOpeningPopup);
    return HeaderButton;
});