odoo.define('qerp_whatsapp_pos.ClientDetailsEdit', function (require) {
    'use strict';

    const { _t } = require('web.core');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit')

    const { debounce } = owl.utils;
    const { useListener } = require('web.custom_hooks');
    const { isConnectionError } = require('point_of_sale.utils');
    const { useAsyncLockedMethod } = require('point_of_sale.custom_hooks');


const MyClientDetailsEdit = (ClientDetailsEdit) => class extends ClientDetailsEdit {
    saveChanges() {
            let processedChanges = {};
            for (let [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
            if ((!this.props.partner.name && !processedChanges.name) ||
                processedChanges.name === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _t('A Customer Name Is Required'),
                });
            }
            if ((!this.props.partner.mobile && !processedChanges.mobile) ||
                            processedChanges.mobile === '' ){
                            return this.showPopup('ErrorPopup', {
                              title: _t('A Customer Mobile Is Required'),
                            });
                        }
            processedChanges.id = this.props.partner.id || false;
            this.trigger('save-changes', { processedChanges });
        }
    }

    Registries.Component.extend(ClientDetailsEdit,MyClientDetailsEdit);

    return MyClientDetailsEdit;
});