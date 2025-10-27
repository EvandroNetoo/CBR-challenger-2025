from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from flask import Flask
from networkx.readwrite import json_graph

if TYPE_CHECKING:
    from src.estrategias.estrategia_base import EstrategiaBase

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class ServicoWeb:
    _iniciado = False
    estrategia: EstrategiaBase

    @classmethod
    def iniciar(cls):
        if not cls._iniciado:
            flask_thread = threading.Thread(target=cls._subir_app)
            flask_thread.daemon = True
            flask_thread.start()

            cls._iniciado = True

    @staticmethod
    def _subir_app():
        app.run(host='0.0.0.0', port=8080, threaded=True, debug=True, use_reloader=False)


@app.route('/mapa')
def get_mapa():
    data = {
        'pos_atual': ServicoWeb.estrategia.pos_atual,
        'direcao': ServicoWeb.estrategia.direcao,
        'grafo': json_graph.node_link_data(ServicoWeb.estrategia.mapa.grafo, edges='edges'),
    }
    return data
