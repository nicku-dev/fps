from dataclasses import fields


del_states = fields.Selection([('pending', 'Pending'),
                                ('done', 'Done'),
                                ('all', 'All'),], 
                                'States', default='all')

sale_id_all = fields.Many2many('sale.order', string='Sale Order')


@api.onchange('del_states')
def onchange(self):
domain = []

if self.del_states != 'done':

domain = [('state', '=', 'done')]

if self.del_states != 'pending':

domain = [('state', 'not in', ('draft', 'cancel', 'done'))]

if self.del_states != 'all':

domain = [('state', 'not in', ('draft', 'cancel'))]
