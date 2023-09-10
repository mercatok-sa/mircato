odoo.define('barameg_geidea_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    var BarcodeParser = require('barcodes.BarcodeParser');
    var BarcodeReader = require('point_of_sale.BarcodeReader');
    var PosDB = require('point_of_sale.DB');
    var devices = require('point_of_sale.devices');
    var concurrency = require('web.concurrency');
    var config = require('web.config');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var utils = require('web.utils');

    var QWeb = core.qweb;
    var _t = core._t;
    var Mutex = concurrency.Mutex;
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    models.load_models([{
        model: 'geidea.terminals',
        condition: function(self){ return true; },
        fields: ['name', 'ConnectionMode', 'ComName', 'BaudRate', 'DataBits', 'Parity', 'IpAddress', 'Port', 'PrintSettings', 'AppId'],
        domain: function(self){ return [['name','!=',true]]; },
        loaded: function(self,result){
            if(result.length){
    //    # do operation as you like, here setting the value in a variable
                self.geidea_terminals = result
                self.geidea_terminals_by_id = {}
                self.geidea_terminals.forEach((terminal, index)=>{
                    self.geidea_terminals_by_id[terminal.id] = terminal
                })
            }
        },
    }],{'after': 'product.product'});

    var _super_paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        initialize: function(attributes, options) {
            _super_paymentline.initialize.apply(this, arguments);
            this.PrimaryAccountNumber = ''
            this.RetrievalReferenceNumber = ''
            this.TransactionAuthCode = ''
        },
        init_from_JSON: function(json){
            _super_paymentline.init_from_JSON.apply(this, arguments);
            this.PrimaryAccountNumber = json.PrimaryAccountNumber
            this.RetrievalReferenceNumber = json.RetrievalReferenceNumber
            this.TransactionAuthCode = json.TransactionAuthCode
        },
        export_as_JSON: function(){
            let object = _super_paymentline.export_as_JSON.apply(this, arguments);
            object.PrimaryAccountNumber = this.PrimaryAccountNumber
            object.RetrievalReferenceNumber = this.RetrievalReferenceNumber
            object.TransactionAuthCode = this.TransactionAuthCode
            return object
        },

    })


    // New orders are now associated with the current table, if any.
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            _super_order.initialize.apply(this,arguments);
            const d = new Date();
            this.ecr_number = d.getTime().toString() + (Math.floor(Math.random()*(999-100+1)+100)).toString()
            return this
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.ecr_number = json.ecr_number
        },
        export_as_JSON: function(){
            let json = _super_order.export_as_JSON.apply(this,arguments);
            json.ecr_number =  this.ecr_number
            return json
        },
    });

})