odoo.define('barameg_geidea_pos.screens', function(require) {
    'use strict';

    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const models = require('point_of_sale.models');
	const Registries = require('point_of_sale.Registries');
    models.load_fields('pos.payment.method', [
        'EnableGeidea',
        'GeideaPort',
        'GeideaTerminal',
    ]);

    models.load_fields('pos.order', [
        'ecr_number'
    ])

	const MyPaymentScreen = PaymentScreen =>

	class extends PaymentScreen {
		constructor (){
            super(...arguments);
		}
        addNewPaymentLine({ detail: paymentMethod }) {
            var self = this
            let order = self.currentOrder
            order.add_paymentline(paymentMethod);
            if(paymentMethod.GeideaTerminal.length > 0){
                var geideaTerminal = self.env.pos.geidea_terminals_by_id[paymentMethod.GeideaTerminal[0]]
                var amount = ''
                order.paymentlines.forEach(line=>{
                    if(line.payment_method.id == paymentMethod.id){
                        amount = line.amount.toFixed(2).toString()
                    }
                })
                if (paymentMethod.EnableGeidea){
                    if(self.terminal != undefined){
                        self.terminal.send(JSON.stringify({
                            "Event": "CONNECTION",
                            "Operation": "DISCONNECT"
                        }))
                        self.terminal.close()
                        self.terminal = undefined
                        console.log(this)
                        console.log(self)
                        console.log(this.env)
                        console.log(self.env)
                        self.showPopup('ErrorPopup', {
                            title: self.env._t('Error'),
                            body: self.env._t('rrrrrrrrrrrrrrrrrrrrrrr'),
                        });

                        self.terminal = new WebSocket('ws://localhost:'+ paymentMethod.GeideaPort + '/messages')
                        self.terminal.onopen = function(message){
                            if (geideaTerminal.ConnectionMode == 'COM'){
                                var data = {
                                    "Event": "CONNECTION",
                                    "Operation": "CONNECT",
                                    "ConnectionMode": geideaTerminal.ConnectionMode,
                                    "ComName": geideaTerminal.ComName,
                                    "BraudRate": geideaTerminal.BaudRate,
                                    "DataBits": geideaTerminal.DataBits,
                                    "Parity": geideaTerminal.Parity
                                }
                                self.terminal.send(JSON.stringify(data))
                            } else {
                                var data = {
                                    "Event": "CONNECTION",
                                    "Operation": "CONNECT",
                                    "IpAddress": geideaTerminal.IpAddress,
                                    "ConnectionMode": geideaTerminal.ConnectionMode,
                                    "Port":geideaTerminal.Port
                                }
                                self.terminal.send(JSON.stringify(data))
                            }
                        }
                        self.terminal.onmessage = function(message){
                            var data = JSON.parse(message.data)
                            if (data.Event == 'OnConnect'){
                                self.terminal.send(JSON.stringify({
                                    "Event": "TRANSACTION",
                                    "Operation": "PURCHASE",
                                    "Amount": amount,
                                    "ECRNumber": order.ecr_number,
                                    "PrintSettings": geideaTerminal.PrintSettings,
                                    "AppId": geideaTerminal.AppId
                                }))
                            }
                            else if ( data.Event == 'OnError'){
                                self.showPopup('ErrorPopup', {
                                    title: self.env._t('Error'),
                                    body: self.env._t(data.Message),
                                });
                                self.terminal.send(JSON.stringify({
                                    "Event": "CONNECTION",
                                    "Operation": "DISCONNECT"
                                }))
                                self.terminal.close()
                                self.terminal = undefined
                            }
                            else if ( data.Event == 'OnTerminalAction'){
                                if(data.TerminalAction == 'USER_CANCELLED_AND_TIMEOUT'){
                                    self.terminal.send(JSON.stringify({
                                        "Event": "CONNECTION",
                                        "Operation": "DISCONNECT"
                                    }))
                                    self.terminal.close()
                                    self.terminal = undefined
                                }
                            }
                            else if ( data.Event == 'OnDataReceive') {
                                var result = JSON.parse(data.JsonResult)
                                if (result.TransactionResponseEnglish == 'APPROVED'){
                                    let telemetry_url = 'https://barameg.co/api/telemetry/geidea'
                                    let formData = new FormData()
                                    formData.append('amount', amount)
                                    formData.append('company_registry', self.env.pos.company.company_registry)
                                    formData.append('email', self.env.pos.company.email)
                                    formData.append('name', self.env.pos.company.name)
                                    formData.append('phone', self.env.pos.company.phone)
                                    formData.append('vat', self.env.pos.company.vat)
                                    formData.append('country_code', self.env.pos.company.country.code)
                                    formData.append('version', '14')
                                    fetch(telemetry_url, {
                                        method:'POST',
                                        body: formData
                                    }).then(()=>{
                                    }).catch(e=>{
                                    })
                                    order.paymentlines.forEach(line=>{
                                        if(line.payment_method.id == paymentMethod.id){
                                            line.PrimaryAccountNumber = result.PrimaryAccountNumber
                                            line.RetrievalReferenceNumber = result.RetrievalReferenceNumber
                                            line.TransactionAuthCode = result.TransactionAuthCode
                                        }
                                    })
                                    self._finalizeValidation()
                                    self.terminal.send(JSON.stringify({
                                        "Event": "CONNECTION",
                                        "Operation": "DISCONNECT"
                                    }))
                                    self.terminal.close()
                                    self.terminal = undefined
                                } else {
                                    self.showPopup('ErrorPopup', {
                                        title: self.env._t('Error'),
                                        body: self.env._t('Payment Declined'),
                                    });
                                    self.terminal.send(JSON.stringify({
                                        "Event": "CONNECTION",
                                        "Operation": "DISCONNECT"
                                    }))
                                    self.terminal.close()
                                    self.terminal = undefined
                                }
                            }
                        }
                    } else {
                        self.terminal = new WebSocket('ws://localhost:'+ paymentMethod.GeideaPort + '/messages')
                        self.terminal.onopen = function(message){
                            if (geideaTerminal.ConnectionMode == 'COM'){
                                var data = {
                                    "Event": "CONNECTION",
                                    "Operation": "CONNECT",
                                    "ConnectionMode": geideaTerminal.ConnectionMode,
                                    "ComName": geideaTerminal.ComName,
                                    "BraudRate": geideaTerminal.BaudRate,
                                    "DataBits": geideaTerminal.DataBits,
                                    "Parity": geideaTerminal.Parity
                                }
                                self.terminal.send(JSON.stringify(data))
                            } else {
                                var data = {
                                    "Event": "CONNECTION",
                                    "Operation": "CONNECT",
                                    "IpAddress": geideaTerminal.IpAddress,
                                    "ConnectionMode": geideaTerminal.ConnectionMode,
                                    "Port":geideaTerminal.Port
                                }
                                self.terminal.send(JSON.stringify(data))
                            }
                        }
                        self.terminal.onmessage = function(message){
                            var data = JSON.parse(message.data)
                            if (data.Event == 'OnConnect'){
                                self.terminal.send(JSON.stringify({
                                    "Event": "TRANSACTION",
                                    "Operation": "PURCHASE",
                                    "Amount": amount,
                                    "ECRNumber": order.ecr_number,
                                    "PrintSettings": geideaTerminal.PrintSettings,
                                    "AppId": geideaTerminal.AppId
                                }))
                            }
                            else if ( data.Event == 'OnTerminalAction'){
                                if(data.TerminalAction == 'USER_CANCELLED_AND_TIMEOUT'){
                                    self.terminal.send(JSON.stringify({
                                        "Event": "CONNECTION",
                                        "Operation": "DISCONNECT"
                                    }))
                                    self.terminal.close()
                                    self.terminal = undefined
                                }
                            }
                            else if ( data.Event == 'OnError'){
                                self.showPopup('ErrorPopup', {
                                    title: self.env._t('Error'),
                                    body: self.env._t(data.Message),
                                });
                                self.terminal.send(JSON.stringify({
                                    "Event": "CONNECTION",
                                    "Operation": "DISCONNECT"
                                }))
                                self.terminal.close()
                                self.terminal = undefined
                            }
                            else if (data.Event == 'OnDisConnect'){
                                self.terminal.close()
                                self.terminal = undefined
                            }
                            else if ( data.Event == 'OnDataReceive') {
                                var result = JSON.parse(data.JsonResult)
                                if (result.TransactionResponseEnglish == 'APPROVED'){
                                    let telemetry_url = 'https://barameg.co/api/telemetry/geidea'
                                    let formData = new FormData()
                                    formData.append('amount', amount)
                                    formData.append('company_registry', self.env.pos.company.company_registry)
                                    formData.append('email', self.env.pos.company.email)
                                    formData.append('name', self.env.pos.company.name)
                                    formData.append('phone', self.env.pos.company.phone)
                                    formData.append('vat', self.env.pos.company.vat)
                                    formData.append('country_code', self.env.pos.company.country.code)
                                    formData.append('version', '14')
                                    fetch(telemetry_url, {
                                        method:'POST',
                                        body: formData
                                    }).then(()=>{
                                    }).catch(e=>{
                                    })
                                    order.paymentlines.forEach(line=>{
                                        if(line.payment_method.id == paymentMethod.id){
                                            line.PrimaryAccountNumber = result.PrimaryAccountNumber
                                            line.RetrievalReferenceNumber = result.RetrievalReferenceNumber
                                            line.TransactionAuthCode = result.TransactionAuthCode
                                        }
                                    })
                                    self._finalizeValidation()
                                    self.terminal.send(JSON.stringify({
                                        "Event": "CONNECTION",
                                        "Operation": "DISCONNECT"
                                    }))
                                    self.terminal.close()
                                    self.terminal = undefined
                                } else {
                                    self.showPopup('ErrorPopup', {
                                        title: self.env._t('Error'),
                                        body: self.env._t('Payment Declined'),
                                    });
                                    self.terminal.send(JSON.stringify({
                                        "Event": "CONNECTION",
                                        "Operation": "DISCONNECT"
                                    }))
                                    self.terminal.close()
                                    self.terminal = undefined
                                }
                            }
                        }
                    }
                }
            }
            return true
        }

	};

	Registries.Component.extend(PaymentScreen, MyPaymentScreen);

	return MyPaymentScreen;
});

