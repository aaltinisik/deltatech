# ©  2015-2021 Terrabit Solutions
#              Dan Stoica <danila(@)terrabit(.)ro
# See README.rst file on addons root folder for license details


{
    "name": "Terrabit - Record Type",
    "summary": "Manage multiple record types",
    "version": "17.0.1.0.6",
    "author": "Terrabit, Voicu Stefan",
    "website": "https://www.terrabit.ro",
    "category": "Generic Modules/Other",
    "depends": [
        "sale",
        # "deltatech_select_journal",
        "purchase",
    ],
    "license": "OPL-1",
    "data": [
        "views/record_type_view.xml",
        "views/purchase_view.xml",
        "views/sale_view.xml",
        "security/ir.model.access.csv",
    ],
    "development_status": "Beta",
    "images": ["static/description/main_screenshot.png"],
    "maintainers": ["VoicuStefan2001"],
}
