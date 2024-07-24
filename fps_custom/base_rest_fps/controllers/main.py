# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.base_rest.controllers import main


class BaseRestFpsPrivateApiController(main.RestController):
    _root_path = "/fps_api/private/"
    _collection_name = "fps.private.services"
    _default_auth = "user"



