# -*- coding: utf-8 -*-
import logging

try:
    from num2words import num2words
except ImportError:
    logging.getLogger(__name__).warning("The num2words python library is not installed.")
    num2words = None
from odoo import models,fields, api


            
class AccountPayment(models.Model):
    _inherit = 'account.payment'
   # terbilang = fields.Char('Terbilang2')  
    terbilang = fields.Char('Terbilang',compute='_terbilang',  store=False)  
    ket = fields.Char('Keterangan')  
    
    
    @api.depends('amount') 
    def _terbilang(self):
        if self.amount:
            temp = num2words(round(self.amount),lang='id', to='currency')         
            self.terbilang =  temp.title()
#    def _terbilang(self):
#        for record in self:
#            temp = num2words(record['amount'],lang='id')
#            record['terbilang'] = temp.replace('koma', 'rupiah')+' sen'

#        if self.amount:
#            temp = num2words(self.amount,lang='id')
#            self.terbilang = temp.replace('koma', 'rupiah')+' sen'
 #   @api.depends('terbilang')            
 #   def _terbilang2(self):
 #       if self.terbilang:
 #           self.terbilang2 = self.terbilang.replace('koma', 'rupiah')+' sen'
            
