from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy import func, or_
import pandas as pd
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, redirect, url_for
import plotly.graph_objs as go


DEBUG = True
USERNAME = 'root'
PASSWORD = 'root'
SERVER = 'localhost'
DB = 'db_sard'

SQLALCHEMY_DATABASE_URI = f'mysql://{USERNAME}:{PASSWORD}@{SERVER}/{DB}'

# USERNAME = 'admin'
# PASSWORD = 'raos481050'
# SERVER = 'rds-sard.czgatsoo6uc5.sa-east-1.rds.amazonaws.com:3306'
# DB = 'rds_sard'
# SQLALCHEMY_DATABASE_URI = f'mysql://{USERNAME}:{PASSWORD}@{SERVER}/{DB}'



SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = "5516500a750bfc88c0832fab"
BABEL_DEFAULT_LOCALE = 'pt'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.secret_key = SECRET_KEY
app.static_url_path = 'static'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subtarefa = db.Column(db.Integer, nullable=True)
    especie = db.Column(db.Integer, nullable=True)
    situacao = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(300), nullable=True)

class Instrucao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subtarefa = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(300), nullable=True)

class Solicitacoes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    protocolo = db.Column(db.Integer, nullable=True)
    solicitante = db.Column(db.String(7), unique=False, nullable=False)
    tipo = db.Column(db.String(100), unique=False, nullable=False)
    matricula = db.Column(db.String(100), unique=False, nullable=True)
    unidade = db.Column(db.String(300), nullable=True)
    especie = db.Column(db.String(2), nullable=True)
    status = db.Column(db.String(300), nullable=True)
    dt_solicitacao = db.Column(db.DateTime, nullable=True)
    dt_conclusao = db.Column(db.DateTime, nullable=True)
class StatusAPI(db.Model):
    __tablename__ = 'status_api'  # Define o nome da tabela
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(45), nullable=True)


@app.route('/')
def index():
    return redirect(url_for('registrar'))


# @app.route('/solicitacoes')
# def solicitacoes():
#     page = request.args.get('page', 1, type=int)
#     per_page = 10  # Definir o número de itens por página
#     todas_solicitacoes = Solicitacoes.query.paginate(page=page, per_page=per_page, error_out=False)
#     return render_template('base.html', solicitacoes=todas_solicitacoes)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        protocolo = request.form.get('protocolo', '')
        solicitante = request.form['solicitante']
        tipo = request.form['tipo']
        matricula = request.form['matricula']
        unidade = request.form['unidade']
        especie = request.form['especie']
        dt_solicitacao = datetime.now()

        protocolo = int(protocolo) if protocolo.isdigit() else None

        nova_solicitacao = Solicitacoes(protocolo=protocolo,solicitante=solicitante, tipo=tipo, matricula=matricula, unidade=unidade,especie=especie,dt_solicitacao=dt_solicitacao)
        db.session.add(nova_solicitacao)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Trate o erro conforme necessário
            print(e)
        return redirect(url_for('registrar'))

    # todas_solicitacoes = Solicitacoes.query.order_by(Solicitacoes.id.desc()).all()
    todas_solicitacoes = Solicitacoes.query.order_by(Solicitacoes.id.desc()).limit(100).all()
    status_mais_recente = StatusAPI.query.order_by(StatusAPI.id.desc()).first()
    return render_template('registrar.html', solicitacoes=todas_solicitacoes,status_api=status_mais_recente)

@app.route('/dados-grafico-estoque')
def dados_grafico_estoque():
    tarefas_distribuidas = Estoque.query.filter(Estoque.status != None).count()
    tarefas_nao_distribuidas = Estoque.query.filter(Estoque.status == None).count()

    labels = ['Tarefas Distribuídas', 'Tarefas Não Distribuídas']
    values = [tarefas_distribuidas, tarefas_nao_distribuidas]

    data = {
        'labels': labels,
        'values': values,
    }
    return jsonify(data)


@app.route('/dados-grafico-estoque-instrucao')
def dados_grafico_estoque_instrucao():
    tarefas_distribuidas = Instrucao.query.filter(Instrucao.status != None).count()
    tarefas_nao_distribuidas = Instrucao.query.filter(Instrucao.status == None).count()

    labels = ['Tarefas de Instrução Distribuídas', 'Tarefas Não Distribuídas']
    values = [tarefas_distribuidas, tarefas_nao_distribuidas]

    data = {
        'labels': labels,
        'values': values,
    }
    return jsonify(data)


@app.route('/dados-grafico')
def dados_grafico():
    especies = Estoque.query.with_entities(Estoque.especie).distinct()
    especies = [especie[0] for especie in especies if especie[0] is not None]

    dados = []

    for especie in especies:
        distribuidas = Estoque.query.filter(Estoque.especie == especie, Estoque.status != None).count()
        nao_distribuidas = Estoque.query.filter(Estoque.especie == especie, Estoque.status == None).count()

        dados.append({
            'especie': especie,
            'distribuidas': distribuidas,
            'nao_distribuidas': nao_distribuidas,
            'total': distribuidas + nao_distribuidas
        })

    # Ordenando os dados pelo total, do maior para o menor
    dados_ordenados = sorted(dados, key=lambda x: x['total'], reverse=True)

    especies_ordenadas = [dado['especie'] for dado in dados_ordenados]
    distribuidas_ordenadas = [dado['distribuidas'] for dado in dados_ordenados]
    nao_distribuidas_ordenadas = [dado['nao_distribuidas'] for dado in dados_ordenados]

    grafico_data = {
        'especies': especies_ordenadas,
        'distribuidas': distribuidas_ordenadas,
        'nao_distribuidas': nao_distribuidas_ordenadas,
    }

    return jsonify(grafico_data)






if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
