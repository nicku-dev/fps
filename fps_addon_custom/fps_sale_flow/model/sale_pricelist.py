
from werkzeug import urls
from odoo import api, fields, models, _
from datetime import datetime

class SaleMdPricelist(models.Model):
    _name = 'sale.md.pricelist'
    _description = 'Sale MD Pricelist'

    name = fields.Char('Name')
    create_date = fields.Date('Create Date', default=datetime.today())
    price_region = fields.Char(string='Region')
    pol = fields.Char(string='POL')
    pod = fields.Char(string='POD')
    load = fields.Char(string='LOAD')
    unit_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        compute='_compute_currency_id', store=True, readonly=False, precompute=True,
        help="The payment's currency.")
    item_ids = fields.One2many(
        comodel_name='sale.md.pricelist.item',
        inverse_name='pricelist_id',
        string="Pricelist Rules",
        copy=True)
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the pricelist without removing it.")
    company_id = fields.Many2one(
        comodel_name='res.company')

class SaleMdPricelistItem(models.Model):
    _name = 'sale.md.pricelist.item'
    _description = 'Sale MD Pricelist Item'

    def _default_pricelist_id(self):
        return self.env['sale.md.pricelist'].search([
            '|', ('company_id', '=', False),
            ('company_id', '=', self.env.company.id)], limit=1)
   
    name = fields.Char('Name')
    pricelist_id = fields.Many2one(
        comodel_name='sale.md.pricelist',
        string="Pricelist",
        index=True, ondelete='cascade',
        required=True,
        default=_default_pricelist_id)

    active = fields.Boolean(related='pricelist_id.active', store=True)
    company_id = fields.Many2one(related='pricelist_id.company_id', store=True)
    currency_id = fields.Many2one(related='pricelist_id.currency_id', store=True)

    date_start = fields.Datetime(
        string="Start Date",
        help="Starting datetime for the pricelist item validation\n"
            "The displayed value depends on the timezone set in your preferences.")
    date_end = fields.Datetime(
        string="End Date",
        help="Ending datetime for the pricelist item validation\n"
            "The displayed value depends on the timezone set in your preferences.")

    min_quantity = fields.Float(
        string="Min. Quantity",
        default=0,
        digits='Product Unit of Measure',
        help="For the rule to apply, bought/sold quantity must be greater "
             "than or equal to the minimum quantity specified in this field.\n"
             "Expressed in the default unit of measure of the product.")

    applied_on = fields.Selection(
        selection=[
            ('3_global', "All Products"),
            ('2_product_category', "Product Category"),
            ('1_product', "Product"),
            ('0_product_variant', "Product Variant"),
        ],
        string="Apply On",
        default='3_global',
        required=True,
        help="Pricelist Item applicable on selected option")

    categ_id = fields.Many2one(
        comodel_name='product.category',
        string="Product Category",
        ondelete='cascade',
        help="Specify a product category if this rule only applies to products belonging to this category or its children categories. Keep empty otherwise.")
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string="Product",
        ondelete='cascade', check_company=True,
        help="Specify a template if this rule only applies to one product template. Keep empty otherwise.")
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product Variant",
        ondelete='cascade', check_company=True,
        help="Specify a product if this rule only applies to one product. Keep empty otherwise.")