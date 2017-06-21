# -*- coding: utf-8 -*-

import os.path as path
from flask import send_from_directory


def configure_routes(app):
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            path.join(app.root_path, 'static', 'images'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )

    #
    # Application views
    #

    from application.home.views import HomeMethodView
    home_view = HomeMethodView.as_view('views.home')
    app.add_url_rule('/', view_func=home_view, methods=['GET', 'POST'])

    #
    # API
    #

    from application.api.search import SearchApiView
    search_api_view = SearchApiView.as_view('views.api.search')
    app.add_url_rule('/api/search/', view_func=search_api_view, methods=['GET'])
