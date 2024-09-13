from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class FreightTimesheet(models.Model):
    _name = 'freight.timesheet'
    _description = 'Freight Timesheet'

    timesheet_id = fields.Many2one('freight.order')
    date = fields.Date(string='Timesheet Date')
    timesheet_datetime = fields.Datetime(string='Time')
    timesheet_activity = fields.Char(string='Kegiatan/Posisi')
    qty_cumulative = fields.Float(string='Qty Cummulative')
    qty_daily_rate = fields.Float(string='Qty Daily Rate')
    load = fields.Many2one(comodel_name='freight.load', string='Load')
    keterangan = fields.Char(string='Keterangan')
    
