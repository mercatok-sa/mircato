# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    imagel = fields.Binary(related='company_id.imagel', readonly=False)
    imagem = fields.Binary(related='company_id.imagem', readonly=False)
    imager = fields.Binary(related='company_id.imager', readonly=False)
    imagef = fields.Binary(related='company_id.imagef', readonly=False)
    imageh = fields.Binary(related='company_id.imageh', readonly=False)




