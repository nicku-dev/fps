# -*- coding: utf-8 -*-

from odoo import api, fields, models



class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    approval_ids = fields.One2many('approval.line', 'move_id')
    document_fully_approved = fields.Boolean(compute='_compute_document_fully_approved')
    check_approve_ability = fields.Boolean(compute='_compute_check_approve_ability')
    is_approved = fields.Boolean(compute='_compute_is_approved')
    page_visibility = fields.Boolean(compute='_compute_page_visibility')
