odoo.define('tus_meta_wa_pos.ReceiptScreen', function(require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const { Printer } = require('point_of_sale.Printer');
    const ajax = require('web.ajax');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;




    models.load_models({
        model: 'wa.template',
        fields: ['id','name' ,'model_id','provider_id'],
        domain: function(self){ return [['model_id.model','=','pos.order']]; },
        loaded: function(self,templates){
            self.templates = templates;
        },
    });

    models.load_models({
        model: 'provider',
        fields: ['id','name'],
        domain: function(self){ return []; },
        loaded: function(self,providers){
            self.providers = providers;
        },
    });

    const PosResReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            /**
             * @override
             */

               mounted() {
                    // Here, we send a task to the event loop that handles
                    // the printing of the receipt when the component is mounted.
                    // We are doing this because we want the receipt screen to be
                    // displayed regardless of what happen to the handleAutoPrint
                    // call.
                    setTimeout(async () => await this.handleAutoPrint(), 0);
                    var self = this
                    this.env.session.user_has_group('tus_meta_wa_pos.whatsapp_group_pos_user').then(async function(has_group){
                        if(has_group){
                             $(self.el).find('.send_by_whatsapp').show();
                             const order = self.currentOrder;
                             const client = order.get_client();
                             if(self.env.pos.config.send_pos_receipt_on_validate && self.env.pos.config.template_id && client.mobile){
                                const printer = new Printer(null, self.env.pos);
                                const receiptString = self.orderReceipt.comp.el.outerHTML;
                                const ticketImage = await printer.htmlToImg(receiptString);
                                const orderName = order.get_name();
                                ajax.jsonRpc("/send/receipt", 'call', {
                                            'provider':self.env.pos.config.provider_id[0],
                                            'template':self.env.pos.config.template_id[0],
                                            'image':ticketImage,
                                            'phone' : client.mobile,
                                            'id': client.id,
                                            'receipt_name':orderName,
                                        }).then(function (data) {
                                            if(data['error']){
                                                return self.showPopup('ErrorPopup', {
                                                    title: self.env._t(data['error']),
                                                });
                                            }
                                        });
                             }
                        } else {
                            $(self.el).find('.send_by_whatsapp').hide()
                        }
                    });
               }

               async sendByWhatsapp(){
                    var def = new $.Deferred();
                    var self = this;
                    const order = self.currentOrder;
                    const client = order.get_client();

                    if(client == null){
                        return this.showPopup('ErrorPopup', {
                          title: _('Please Select Customer'),
                        });
                    }
                    const phone = client.mobile
                    this.showPopup('WaComposerPopup', {
                        transaction: def,
                    });
                    $(document).ready(function () {
                        if(phone){
                            $('#phone').val(phone);
                            $('.wa_template').change(function(){
                                const template_id = $( ".wa_template option:selected" ).val();
                                const orderName = order.get_name();
                                ajax.jsonRpc("/get/template/content", 'call', {
                                                    'template_id':template_id,
                                                    'order_name':orderName,
                                                }).then(function (data) {
                                                    if(data){
                                                        $('#message').val(data)
                                                    }
                                                    else{
                                                        $('#message').val('')
                                                    }
                                                });
                            })

                            $('.sendMessage').click(async function(){
                                if($( ".wa_template option:selected" ).val() != '' && $('#message').val() != '' && $(".provider option:selected" ).val() != ''){
                                    const printer = new Printer(null, self.env.pos);
                                    const receiptString = self.orderReceipt.comp.el.outerHTML;
                                    const ticketImage = await printer.htmlToImg(receiptString);
                                    const order = self.currentOrder;
                                    const orderName = order.get_name();
                                    ajax.jsonRpc("/send/receipt", 'call', {
                                                'message':$('#message').val(),
                                                'template':$( ".wa_template option:selected" ).val(),
                                                'provider':$( ".provider option:selected" ).val(),
                                                'image':ticketImage,
                                                'phone' : phone,
                                                'id': client.id,
                                                'receipt_name':orderName,
                                            }).then(function (data) {
                                                if(data['error']){
                                                    return self.showPopup('ErrorPopup', {
                                                        title: self.env._t(data['error']),
                                                    });
                                                }
                                                $('.wa_cancel').click();
                                            });
                                }
                                else{
                                    self.showPopup('ErrorPopup', {
                                        title: self.env._t('Provider, Message and Template are Required!'),
                                    });
                                }
                            })
                        }
                        else{
                            self.showPopup('ErrorPopup', {
                                title: self.env._t('Mobile Number Required'),
                            });
                            return false;
                        }
                    });
                }
        };

    Registries.Component.extend(ReceiptScreen, PosResReceiptScreen);

    return ReceiptScreen;
});
