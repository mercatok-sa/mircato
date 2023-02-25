odoo.define('pos_items_receipt.items_receipt', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var rpc = require('web.rpc');

	var utils = require('web.utils');
	var session = require('web.session');
	var time = require('web.time');
	var round_pr = utils.round_precision;
	var chrome = require('point_of_sale.chrome');

	var _t = core._t;

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({

		get_total_items: function() {
			var utils = require('web.utils');
			var round_pr = utils.round_precision;
			return round_pr(this.orderlines.reduce((function(sum, orderLine) {
				return sum + orderLine.quantity;
			}), 0), this.pos.currency.rounding);
		},
	});
	screens.OrderWidget.include({
		update_summary: function(){
			this._super();
			var order = this.pos.get_order();
			if (!order.get_orderlines().length) {
				return;
			}
			var total_items    = order ? order.get_total_items() : 0;
			this.el.querySelector('.item_count .val').textContent = total_items.toFixed(0);
		},
	});

});
