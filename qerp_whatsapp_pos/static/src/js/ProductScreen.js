// This Function is used to prevent add the new product in the Refund order in POS.
odoo.define('qerp_whatsapp_pos.ProductScreen', function (require) {
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
                console.log(this.currentOrder);
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
    return PosProductScreen;
});

