from flask import Flask, request, redirect, send_from_directory, jsonify, make_response
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USUARIOS_ARQ = os.path.join(BASE_DIR, "usuarios.json")
CONTATOS_ARQ = os.path.join(BASE_DIR, "contatos.json")
COMPRAS_ARQ = os.path.join(BASE_DIR, "compras.json")


# ---------------------- FUNÇÃO SEGURA DE CARREGAMENTO ----------------------
def carregar_arquivo(caminho, padrao):
    if not os.path.exists(caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(padrao, f, indent=4, ensure_ascii=False)

    with open(caminho, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return padrao


# ---------------------- FUNÇÃO UNIVERSAL DE LEITURA (FORM + JSON) ----------------------
def dados_requisicao():
    """Aceita JSON OU formulário HTML automaticamente."""
    if request.is_json:
        return request.get_json()
    else:
        return request.form.to_dict()


# ---------------------- ROTAS DE PÁGINAS ----------------------
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:arquivo>")
def arquivos(arquivo):
    return send_from_directory(BASE_DIR, arquivo)


# ---------------------- CADASTRO ----------------------
@app.route("/cadastro", methods=["POST"])
def cadastro():
    dados = dados_requisicao()
    usuarios = carregar_arquivo(USUARIOS_ARQ, [])

    # Verifica se email já existe
    for usuario in usuarios:
        if usuario["email"] == dados.get("email"):
            return jsonify({"erro": "Email já cadastrado!"})

    usuarios.append(dados)

    with open(USUARIOS_ARQ, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

    return jsonify({"sucesso": True})


# ---------------------- LOGIN (AGORA COM COOKIE!) ----------------------
@app.route("/login", methods=["POST"])
def login():
    dados = dados_requisicao()
    usuarios = carregar_arquivo(USUARIOS_ARQ, [])

    for usuario in usuarios:
        if usuario["email"] == dados.get("email") and usuario["senha"] == dados.get("senha"):

            nome = usuario.get("nome", "Usuário")

            # Criar resposta com cookie
            resposta = make_response(jsonify({"sucesso": True}))
            resposta.set_cookie("user", nome, path="/")

            return resposta

    return jsonify({"erro": "Email ou senha incorretos!"})


# ---------------------- SALVAR CONTATO ----------------------
@app.route("/contato", methods=["POST"])
def contato():
    dados = dados_requisicao()
    contatos = carregar_arquivo(CONTATOS_ARQ, [])

    contatos.append(dados)

    with open(CONTATOS_ARQ, "w", encoding="utf-8") as f:
        json.dump(contatos, f, indent=4, ensure_ascii=False)

    return jsonify({"sucesso": True})


# ---------------------- REGISTRAR COMPRA ----------------------
@app.route("/finalizar_compra", methods=["POST"])
def finalizar_compra():
    dados = dados_requisicao()
    compras = carregar_arquivo(COMPRAS_ARQ, [])

    compras.append({
        "produto": dados.get("produto"),
        "preco": dados.get("preco"),
        "comprador": {
            "nome": dados.get("nome"),
            "cpf": dados.get("cpf"),
            "telefone": dados.get("telefone"),
            "estado": dados.get("estado"),
            "cidade": dados.get("cidade"),
            "endereco": dados.get("endereco")
        }
    })

    with open(COMPRAS_ARQ, "w", encoding="utf-8") as f:
        json.dump(compras, f, indent=4, ensure_ascii=False)

    return jsonify({"redirect": "index.html"})


# ---------------------- INICIAR SERVIDOR ----------------------
if __name__ == "__main__":
    app.run(debug=True)