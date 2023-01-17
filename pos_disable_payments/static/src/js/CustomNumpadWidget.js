odoo.define('pos_disable_payments.CustomNumpadWidget', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

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
    class CustomNumpadWidget extends PosComponent {
        mounted() {
            // IMPROVEMENT: This listener shouldn't be here because in core point_of_sale
            // there is no way of changing the cashier. Only when pos_hr is installed
            // that this listener makes sense.
            this.env.pos.on('change:cashier', () => {
                if (!this.hasPriceControlRights && this.props.activeMode === 'price') {
                    this.trigger('set-numpad-mode', { mode: 'quantity' });
                }
            });
        }
        willUnmount() {
            this.env.pos.on('change:cashier', null, this);
        }
        get hasPriceControlRights() {
            const cashier = this.env.pos.get('cashier') || this.env.pos.get_cashier();
            return !this.env.pos.config.restrict_price_control || cashier.role == 'manager';
        }
        get hasManualDiscount() {
            return this.env.pos.config.manual_discount;
        }
        changeMode(mode) {
            if (!this.hasPriceControlRights && mode === 'price') {
                return;
            }
            if (!this.hasManualDiscount && mode === 'discount') {
                return;
            }
            this.trigger('set-numpad-mode', { mode });
        }
        sendInput(key) {
			let cashier = this.env.pos.get_cashier();
			if(this.props.activeMode == 'quantity'){
				 if('is_allow_qty' in cashier){
					 if (cashier.is_allow_qty) {
						 this.trigger('numpad-click-input', { key });
					 }
					 else{
						 alert("Sorry,You have no access to change quantity");
					 }
				 }
				 else{
					this.trigger('numpad-click-input', { key });
				 }  
			}else if(this.props.activeMode == 'price'){
				 if('is_edit_price' in cashier){
					 if (cashier.is_edit_price) {
						 this.trigger('numpad-click-input', { key });
					 }
					 else{
						 alert("Sorry,You have no access to change Price");
					 }
				 }
				 else{
					this.trigger('numpad-click-input', { key });
				 } 
			}else if(this.props.activeMode == 'discount'){
				 if('is_allow_discount' in cashier){
					 if (cashier.is_allow_discount) {
						 this.trigger('numpad-click-input', { key });
					 }
					 else{
						 alert("Sorry,You have no access to change discount");
					 }
				 }
				 else{
					this.trigger('numpad-click-input', { key });
				 } 
			}
		}
        get decimalSeparator() {
            return this.env._t.database.parameters.decimal_point;
        }
    }
    CustomNumpadWidget.template = 'CustomNumpadWidget';

    Registries.Component.add(CustomNumpadWidget);

    return CustomNumpadWidget;
});
