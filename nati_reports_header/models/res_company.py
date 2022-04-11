# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
   
class res_company(models.Model):
    _inherit = "res.company"

    imagel = fields.Binary(string='Image Left')
    imagem = fields.Binary(string='Image Medium')
    imager = fields.Binary(string='Image Right')
    imageh = fields.Binary(string='Image Header')
    imagef = fields.Binary(string='Image Footer')
    #default font oviraid
    font = fields.Selection(
        [("Lato", "Lato"), ("Roboto", "Roboto"), ("Open_Sans", "Open Sans"), ("Montserrat", "Montserrat"),
         ("Oswald", "Oswald"), ("Raleway", "Raleway"),("Almarai", "Almarai"),
         ("Droid Arabic Naskh", "Droid Arabic Naskh"),
         ("Droid Arabic Kufi", "Droid Arabic Kufi"), ("Cairo", "Cairo"),], default="Almarai")
