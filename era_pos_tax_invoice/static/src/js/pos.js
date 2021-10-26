odoo.define('era_tax_invoice.OrderReceipt', function(require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

//    models.load_fields('pos.config',['allow_qr_code']);

    var module = require('point_of_sale.models');
    var models = module.PosModel.prototype.models;
    for(var i=0; i<models.length; i++){
        var model=models[i];
        if(model.model === 'res.company'){
             model.fields.push('street');
             model.fields.push('city');
             model.fields.push('state_id');
             model.fields.push('country_id');

             // other field you want to pull from the res.company table.

        }
    }
//    console.log(models)


    const PosQRCodeOrderReceipt = OrderReceipt =>
        class extends OrderReceipt {
            get receiptEnv () {
//                if (this.env.pos.allow_qr_code) {
                    let receipt_render_env = super.receiptEnv;
                    let order = this.env.pos.get_order();
                    receipt_render_env.receipt.company.street = this.env.pos.company.street;
                    var qr_code_data = "Company:"+this.env.pos.company.name;
                    if(this.env.pos.company.vat){
                         qr_code_data += "  | VAT NO.:"+ this.env.pos.company.vat;
                    }
                    if(order['formatted_validation_date']){
                        qr_code_data += "  | Order Date:"+ order['formatted_validation_date'];
                    }
                    if(order.get_total_with_tax()){
                        qr_code_data += "  | Total Amount:"+ Math.round(order.get_total_with_tax()*100)/100;
                    }
                    if(order.get_total_tax()){
                        qr_code_data += "  | Total Tax:"+ Math.round(order.get_total_tax()*100)/100;
                    }
                    var company_address =  this.env.pos.company.street;
                    if (this.env.pos.company.city){company_address += "-"+this.env.pos.company.city}
                    var company_state = this.env.pos.company.state_id[1];
                    if (this.env.pos.company.country_id){company_state += "-"+this.env.pos.company.country_id[1]}
//                    console.log(qr_code_data)
                    receipt_render_env.receipt.qr_code = '('+qr_code_data+')';
                    receipt_render_env.receipt.company_address = company_address;
                    receipt_render_env.receipt.company_state = company_state;
                    return receipt_render_env;
//                }
            }
        };

    Registries.Component.extend(OrderReceipt, PosQRCodeOrderReceipt);

    return OrderReceipt;
});
