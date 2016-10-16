# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_TIME_FORMAT
import time 
from datetime import datetime

class account_invoice(models.Model):
    _inherit = "account.invoice"

 
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        res = super(account_invoice,self)._onchange_journal_id()
        msg = self.check_data(journal_id=self.journal_id, date_invoice=self.date_invoice)
        if msg != '': 
            res['warning'] = {'title':_('Warning'),'message':msg}          
        return res
    
    @api.multi



    @api.multi    
    def check_data(self, journal_id=None, date_invoice=None):
        
        for obj_inv in self:
            inv_type = obj_inv.type
            number = obj_inv.number
            date_invoice = date_invoice or obj_inv.date_invoice
            journal_id = journal_id or obj_inv.journal_id.id
         
            if (inv_type == 'out_invoice' or inv_type == 'out_refund') and not obj_inv.move_name:
                res = self.search(  [('type','=',inv_type),
                                     ('date_invoice','>',date_invoice), 
                                     ('journal_id', '=', journal_id) ,
                                     ('state','in',['open','paid']) ],
                                  limit = 1,
                                  order = 'date_invoice desc')
                if res:                
                    lang = self.env['res.lang'].search([('code','=',self.env.user.lang)])
                    #date_invoice = fields.Datetime.from_string
                    date_invoice = datetime.strptime(res.date_invoice, DEFAULT_SERVER_DATE_FORMAT).strftime(lang.date_format.encode('utf-8'))
                    return  _('Post the invoice with a greater date than %s') % date_invoice
        return ''
    
       
    @api.multi
    def action_move_create(self):
        msg = self.check_data()
        if msg != '':
            raise Warning(_('Date Inconsistency'), msg )
        super(account_invoice, self).action_move_create()
        return True





              

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



 
