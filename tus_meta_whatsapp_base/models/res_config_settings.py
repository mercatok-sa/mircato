from odoo import api, fields, models,_


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_tus_meta_wa_sale = fields.Boolean("Tus Whatsapp Sales")
    module_tus_meta_wa_purchase = fields.Boolean("Tus Whatsapp Purchase")
    module_tus_meta_wa_invoice = fields.Boolean("Tus Whatsapp Invoice")
    module_tus_meta_wa_stock_picking = fields.Boolean("Tus Whatsapp Stock Picking")
    module_tus_meta_wa_sale_in_discuss = fields.Boolean("Tus Whatsapp Sale In Discuss")
    module_tus_meta_wa_helpdesk_in_discuss = fields.Boolean("Tus Whatsapp Helpdesk In Discuss")
    module_tus_meta_wa_helpdesk = fields.Boolean("Tus Whatsapp Helpdesk")
    module_tus_meta_wa_follow_up_report = fields.Boolean("Tus Whatsapp Follow Up Report")
    module_tus_meta_wa_discuss = fields.Boolean("Tus Whatsapp Discuss")
    module_tus_meta_wa_crm_in_discuss = fields.Boolean("Tus Whatsapp CRM In Discuss")
    module_tus_meta_wa_crm = fields.Boolean("Tus Whatsapp CRM")
    module_tus_meta_wa_invoice_in_discuss = fields.Boolean("Tus Whatsapp Invoice In Discuss")
    module_tus_meta_wa_marketing = fields.Boolean("Tus Whatsapp Marketing")
    module_tus_meta_wa_purchase_in_discuss = fields.Boolean("Tus Whatsapp Purchase In Discuss")
    module_tus_meta_wa_pos = fields.Boolean("Tus Whatsapp POS")

    @api.onchange('module_tus_meta_wa_purchase_in_discuss')
    def on_module_tus_meta_wa_purchase_in_discuss(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_purchase_in_discuss'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_purchase_in_discuss:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Purchase In Discuss In Discuss module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_marketing')
    def on_module_tus_meta_wa_marketing(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_marketing'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_marketing:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Marketing In Discuss module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_invoice_in_discuss')
    def on_module_tus_meta_wa_invoice_in_discuss(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_invoice_in_discuss'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_invoice_in_discuss:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Invoice In Discuss module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_crm')
    def on_module_tus_meta_wa_crm(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_crm'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_crm:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp CRM module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_discuss')
    def on_module_tus_meta_wa_discuss(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_discuss'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_discuss:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Discuss module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_crm_in_discuss')
    def on_module_tus_meta_wa_crm_in_discuss(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_crm_in_discuss'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_crm_in_discuss:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp CRM In Discuss module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_helpdesk_in_discuss')
    def on_module_tus_meta_wa_helpdesk_in_discuss(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_helpdesk_in_discuss'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_helpdesk_in_discuss:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Helpdesk In Discuss module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_helpdesk')
    def on_module_tus_meta_wa_helpdesk(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_helpdesk'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_helpdesk:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Helpdesk module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_sale_in_discuss')
    def on_module_tus_meta_wa_sale_in_discuss(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_sale_in_discuss'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_sale_in_discuss:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Sale In Discuss module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_follow_up_report')
    def on_module_tus_meta_wa_follow_up_report(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_follow_up_report'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_follow_up_report:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Follow Up Report module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_sale')
    def on_module_tus_meta_wa_sale(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_sale'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_sale:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Sale module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_purchase')
    def on_module_tus_meta_wa_purchase(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_purchase'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_purchase:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Purchase module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_invoice')
    def on_module_tus_meta_wa_invoice(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_invoice'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_invoice:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Invoice module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_pos')
    def on_module_tus_meta_wa_pos_in_discuss(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_pos'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_pos:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp POS module not exist!'),
                }
            }

    @api.onchange('module_tus_meta_wa_stock_picking')
    def on_module_tus_meta_wa_stock_picking(self):
        ModuleSudo = self.env['ir.module.module'].sudo()
        modules = ModuleSudo.search(
            [('name', '=', 'module_tus_meta_wa_stock_picking'.replace("module_", ''))])
        if not modules and self.module_tus_meta_wa_stock_picking:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Tus Whatsapp Stock Picking module not exist!'),
                }
            }

