from flask import Blueprint, Response
from services.grafico_service import gerar_grafico_png

grafico_bp = Blueprint('grafico', __name__)

@grafico_bp.route('/grafico/<string:ativo>', methods=['GET'])
def grafico_ativo(ativo):
    imagem_png = gerar_grafico_png(ativo)
    return Response(imagem_png, mimetype='image/png')
