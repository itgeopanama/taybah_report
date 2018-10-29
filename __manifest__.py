# -*- coding: utf-8 -*-
{
    'name': "Accounting Reports",

    'summary': """
        This App Provides Reports about Journal Card , Customer Transaction , vendor Transaction , 
        Customer Balance ,Vendor Balance """,

    'description': """
         This App Provides Reports about Journal Card , Customer Transaction , vendor Transaction , 
        Customer Balance ,Vendor Balance
    """,

    'author': "TayBah Soft (Egypt)",
    'website': "http://www.taybahsoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}