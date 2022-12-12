// This Function is used to prevent add the new product in the Refund order in POS.
odoo.define('disable_price_discount.TicketScreen_Popup', function(require) {
  'use strict';
    const ProductScreen = require('point_of_sale.ProductScreen');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { isConnectionError, posbus } = require('point_of_sale.utils');
    const { useState, onMounted } = owl.hooks;
    const { parse } = require('web.field_utils');
      const PosProductScreen = (ProductScreen) =>
       class extends ProductScreen {
           async _clickProduct(event){
           if (this.currentOrder.getHasRefundLines()){
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
       };
   Registries.Component.extend(ProductScreen, PosProductScreen);
   return ProductScreen;
});


odoo.define('disable_price_discount.HeaderButton', function(require) {
    'use strict';
    const HeaderButton = require('point_of_sale.HeaderButton')
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    const PosHeaderButton = (HeaderButton) =>
       class extends HeaderButton {
        onClick() {
            window.location = '/web#action=point_of_sale.action_client_pos_menu';
        }
    
    }
    HeaderButton.template = 'HeaderButton';
    Registries.Component.extend(HeaderButton,PosHeaderButton);
    return HeaderButton;
});
