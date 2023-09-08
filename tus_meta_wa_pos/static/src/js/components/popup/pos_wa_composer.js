odoo.define('tus_meta_wa_pos.WaComposerPopup', function(require) {
    'use strict';

    const { useState } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class WaComposerPopup extends AbstractAwaitablePopup {
         constructor() {
            super(...arguments);
            this.state = owl.hooks.useState({
                templates: this.env.pos.templates.filter(t => this.env.pos.config.allowed_provider_ids && this.env.pos.config.allowed_provider_ids[0] == t.provider_id[0]),
                providers: this.env.pos.providers.filter(p => this.env.pos.config.allowed_provider_ids.includes(p.id)),
            })
        }
        onChangeProvider(event){
             this.state.templates = this.env.pos.templates.filter(t => parseInt(event.target.value) == t.provider_id[0])
       }
    }
    WaComposerPopup.template = 'WaComposerPopup';
    WaComposerPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        body: '',
    };

    Registries.Component.add(WaComposerPopup);

    return WaComposerPopup;
});