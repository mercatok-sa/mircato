odoo.define('era_pos_item_count.models', function (require) {
"use strict";

    var models = require('point_of_sale.models');

    models.load_fields("res.users", ['display_all_info_close_session']);

});