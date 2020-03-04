# Copyright 2015 ADHOC SA  (http://www.adhoc.com.ar)
# Copyright 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Product(models.Model):
    _inherit = 'product.product'

    @api.onchange('length', 'height', 'width', 'dimensional_uom_id')
    def onchange_calculate_volume(self):
        self.volume = self.env['product.template']._calc_volume(
            self.length, self.height, self.width, self.dimensional_uom_id)

    @api.model
    def _get_dimension_uom_domain(self):
        return [
            ('category_id', '=', self.env.ref('product.uom_categ_length').id)
        ]

    @api.one
    @api.constrains('width', 'height', 'length')
    def _check_negative_values(self):
        if self.height < 0:
            raise ValidationError(_('Height can not be negative'))
        if self.width < 0:
            raise ValidationError(_('Width can not be negative'))
        if self.length < 0:
            raise ValidationError(_('Length can not be negative'))
        return True

    length = fields.Float('Longitud del producto',  compute='_compute_template_variant_length', inverse='_set_length', store=True)
    height = fields.Float('Altitud del producto',  compute='_compute_template_variant_height', inverse='_set_height', store=True)
    width = fields.Float('Anchura del producto',  compute='_compute_template_variant_width', inverse='_set_width', store=True)
    dimensional_uom_id = fields.Many2one(
        'product.uom',
        'Dimensional UoM',
        domain=lambda self: self._get_dimension_uom_domain(),
        help='UoM for length, height, width')

    @api.depends('length', 'product_tmpl_id.length')
    def _compute_template_variant_length(self):
        length_field = self.filtered(lambda template: len(template.product_tmpl_id) == 1)
        for length_v in length_field:
            length_v.length = length_v.product_tmpl_id.length
        for template in (self - length_field):
            template.length = False

    @api.one
    def _set_length(self):
        if len(self.product_tmpl_id) == 1:
            self.product_tmpl_id.length = self.length

    @api.depends('height', 'product_tmpl_id.height')
    def _compute_template_variant_height(self):
        height_field = self.filtered(lambda template: len(template.product_tmpl_id) == 1)
        for height_v in height_field:
            height_v.height = height_v.product_tmpl_id.height
        for template in (self - height_field):
            template.height = False

    @api.one
    def _set_height(self):
        if len(self.product_tmpl_id) == 1:
            self.product_tmpl_id.height = self.height

    @api.depends('width', 'product_tmpl_id.width')
    def _compute_template_variant_width(self):
        width_field = self.filtered(lambda template: len(template.product_tmpl_id) == 1)
        for width_v in width_field:
            width_v.width = width_v.product_tmpl_id.width
        for template in (self - width_field):
            template.width = False

    @api.one
    def _set_width(self):
        if len(self.product_tmpl_id) == 1:
            self.product_tmpl_id.width = self.width

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _calc_volume(self, length, height, width, uom_id):
        volume = 0
        if length and height and width and uom_id:
            length_m = self.convert_to_meters(length, uom_id)
            height_m = self.convert_to_meters(height, uom_id)
            width_m = self.convert_to_meters(width, uom_id)
            volume = length_m * height_m * width_m

        return volume

    @api.onchange('length', 'height', 'width', 'dimensional_uom_id')
    def onchange_calculate_volume(self):
        self.volume = self._calc_volume(
            self.length, self.height, self.width, self.dimensional_uom_id)

    length = fields.Float()
    height = fields.Float()
    width = fields.Float()
    dimensional_uom_id = fields.Many2one(
        'product.uom',
        'Dimensional UoM', related='product_variant_ids.dimensional_uom_id',
        help='UoM for length, height, width')

    def convert_to_meters(self, measure, dimensional_uom):
        uom_meters = self.env.ref('product.product_uom_meter')

        return dimensional_uom._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False,
        )
