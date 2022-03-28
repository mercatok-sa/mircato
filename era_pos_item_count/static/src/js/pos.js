odoo.define('era_pos_item_count.pos_item_count', function(require){
 var models = require('point_of_sale.models');
    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(){
            var self = this;
            OrderlineSuper.prototype.initialize.apply(this, arguments);
            this.bind('change', function(line){
            	setTimeout(function(){
            	var orders = self.order;
	            var qty=0;
	            if(orders != null){
	                var order_lines = orders.get_orderlines()
	                for(var i=0;i<order_lines.length;i++){
	                    qty+=order_lines[i].quantity;
	                }
	                orders.items = qty;
	            }
	           $(".count_num_item").html(qty);
	             }, 10);
            });
        },
    });
});
