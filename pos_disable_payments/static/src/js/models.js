// pos_disable_payments js
odoo.define('pos_disable_payments.models', function(require) {
	"use strict";

	const models = require('point_of_sale.models');
	const session = require('web.session');;

	models.load_models([{
		model:  'res.users',
		fields: ['name','company_id', 'id', 'groups_id', 'lang','is_allow_numpad','is_allow_payments','is_allow_discount',
			'is_allow_qty','is_edit_price','is_allow_remove_orderline','is_allow_customer_selection','is_allow_plus_minus_button'],
		domain: function(self){ return [['company_ids', 'in', self.config.company_id[0]],'|', ['groups_id','=', self.config.group_pos_manager_id[0]],['groups_id','=', self.config.group_pos_user_id[0]]]; },
		loaded: function(self, users) {

            users.forEach(function(user) {
                user.role = 'cashier';
                user.groups_id.some(function(group_id) {
                    if (group_id === self.config.group_pos_manager_id[0]) {
                        user.role = 'manager';
                        return true;
                    }
                });
                if (user.id === self.session.uid) {
                    self.user = user;
                    self.employee.name = user.name;
                    self.employee.role = user.role;
                    self.employee.user_id = [user.id, user.name];
                    self.employee.is_allow_numpad = user.is_allow_numpad;
					self.employee.is_allow_payments = user.is_allow_payments;
					self.employee.is_allow_qty = user.is_allow_qty;
					self.employee.is_allow_discount = user.is_allow_discount;
					self.employee.is_edit_price = user.is_edit_price;
					self.employee.is_allow_remove_orderline = user.is_allow_remove_orderline;
					self.employee.is_allow_customer_selection = user.is_allow_customer_selection;
					self.employee.is_allow_plus_minus_button = user.is_allow_plus_minus_button;
                }
            });
            self.users = users;
            self.employees = [self.employee];
            self.set_cashier(self.employee);
		}
	}]);

	models.load_models([{
		model:  'hr.employee',
		fields: ['name', 'id', 'user_id','is_allow_numpad','is_allow_payments','is_allow_discount',
			'is_allow_qty','is_edit_price','is_allow_remove_orderline','is_allow_customer_selection','is_allow_plus_minus_button'],
		domain: function(self){ return [['company_id', '=', self.config.company_id[0]]]; },
		loaded: function(self, employees) {
			if (self.config.module_pos_hr) {
				if (self.config.employee_ids.length > 0) {
					self.employees = employees.filter(function(employee) {
						return self.config.employee_ids.includes(employee.id) || employee.user_id[0] === self.user.id;
					});
				} else {
					self.employees = employees;
				}
				self.employees.forEach(function(employee) {
					let hasUser = self.users.some(function(user) {
						if (user.id === employee.user_id[0]) {
							employee.role = user.role;
							employee.is_allow_numpad = user.is_allow_numpad;
							employee.is_allow_payments = user.is_allow_payments;
							employee.is_allow_qty = user.is_allow_qty;
							employee.is_allow_discount = user.is_allow_discount;
							employee.is_edit_price = user.is_edit_price;
							employee.is_allow_remove_orderline = user.is_allow_remove_orderline;
							employee.is_allow_customer_selection = user.is_allow_customer_selection;
							employee.is_allow_plus_minus_button = user.is_allow_plus_minus_button;
							return true;
						}
						return false;
					});
					if (!hasUser) {
						employee.role = 'cashier';
					}
				});
			}
		}
	}]);

});
