
odoo.define('pos_disable_payments.BiProductScreen', function(require) {
	'use strict';

	const ProductScreen = require('point_of_sale.ProductScreen');
	const Registries = require('point_of_sale.Registries');

	const BiProductScreen = ProductScreen => class extends ProductScreen {
		
		_setValue(val) {
			let allow_rmv_ol = this.env.pos.get_cashier().is_allow_remove_orderline;
			let is_allow_qty = this.env.pos.get_cashier().is_allow_qty;
			if(allow_rmv_ol == false || is_allow_qty == false){
				if(val == '' || val == 'remove'){
					alert("Sorry,You are not allowed to perform this operation");
					return
				}
			}
			
			if (this.currentOrder.get_selected_orderline()) {
				if (this.state.numpadMode === 'quantity') {
					this.currentOrder.get_selected_orderline().set_quantity(val);
				} else if (this.state.numpadMode === 'discount') {
					this.currentOrder.get_selected_orderline().set_discount(val);
				} else if (this.state.numpadMode === 'price') {
					var selected_orderline = this.currentOrder.get_selected_orderline();
					selected_orderline.price_manually_set = true;
					selected_orderline.set_unit_price(val);
				}
				if (this.env.pos.config.iface_customer_facing_display) {
					this.env.pos.send_current_order_to_customer_facing_display();
				}
			}
		}
		
	};

	Registries.Component.extend(ProductScreen, BiProductScreen);
	return ProductScreen;
 });