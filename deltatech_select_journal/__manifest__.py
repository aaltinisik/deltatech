# ©  2008-2021 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Deltatech Select Journal",
    "version": "16.0.1.0.8",
    "author": "Terrabit, Dorin Hongu",
    "license": "OPL-1",
    "website": "https://www.terrabit.ro",
    "summary": "Selectie jurnal",
    "category": "Sales",
    "depends": ["sale_stock", "sales_team", "account", "product"],
    "data": [
        "wizard/sale_make_invoice_advance_views.xml",
        "views/account_move.xml",
        "views/sale_team_view.xml",
        "views/account_journal.xml",
    ],
    "images": ["images/main_screenshot.png"],
    "development_status": "Mature",
    "maintainers": ["dhongu"],
}
