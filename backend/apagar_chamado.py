"""Apaga chamados do banco, junto com o historico e as fotos deles, sem deixar sobras.

Use dentro da pasta backend (com o ambiente .venv ativo):

  python apagar_chamado.py              lista os chamados e os totais
  python apagar_chamado.py 5            apaga o chamado de id 5 (pergunta antes)
  python apagar_chamado.py 5 6 10       apaga varios de uma vez
  python apagar_chamado.py 5 -y         apaga sem perguntar
  python apagar_chamado.py --limpar     remove sobras (historico/fotos sem chamado)

Nunca mexe em usuarios nem em postes.
"""
import sqlite3
import sys
from pathlib import Path

try:  # evita letras quebradas no terminal do Windows
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PASTA = Path(__file__).resolve().parent
BANCO = PASTA / "ilumina.db"      # sempre o banco da pasta backend, de onde quer que voce rode
UPLOADS = PASTA / "uploads"
SITUACAO = {"recebido": "Recebido", "equipe_a_caminho": "A caminho", "resolvido": "Resolvido"}


def totais(db):
    total = db.execute("SELECT COUNT(*) FROM chamados").fetchone()[0]
    print(f"\nTotal de chamados: {total}")
    por_status = dict(db.execute("SELECT status, COUNT(*) FROM chamados GROUP BY status").fetchall())
    print("Por situacao:", ", ".join(f"{SITUACAO.get(k, k)} {v}" for k, v in por_status.items()) or "-")
    bairros = db.execute("SELECT bairro, COUNT(*) FROM chamados GROUP BY bairro ORDER BY 2 DESC, 1").fetchall()
    print("Por bairro:  ", ", ".join(f"{b} {n}" for b, n in bairros) or "-")
    hist = db.execute("SELECT COUNT(*) FROM historico_status").fetchone()[0]
    fotos = db.execute("SELECT COUNT(*) FROM fotos_chamado").fetchone()[0]
    print(f"Linhas de historico: {hist} | fotos registradas: {fotos}")


def listar(db):
    linhas = db.execute(
        "SELECT id, protocolo, bairro, status, urgencia, tipo_problema, substr(criado_em, 1, 10) "
        "FROM chamados ORDER BY id"
    ).fetchall()
    print(f"{'ID':>3}  {'PROTOCOLO':<10}  {'BAIRRO':<14}  {'SITUACAO':<10}  {'URG':<6}  {'CRIADO EM':<10}  TIPOS")
    for i, prot, bairro, status, urg, tipos, criado in linhas:
        print(f"{i:>3}  {prot:<10}  {bairro:<14}  {SITUACAO.get(status, status):<10}  {urg:<6}  {criado:<10}  {tipos}")
    totais(db)


def apagar(db, ids, sem_perguntar):
    apagados = 0
    for cid in ids:
        c = db.execute("SELECT id, protocolo, bairro, status FROM chamados WHERE id = ?", (cid,)).fetchone()
        if not c:
            print(f"- Chamado {cid}: nao existe, pulei.")
            continue
        if not sem_perguntar:
            resp = input(f"Apagar o chamado {c[0]} ({c[1]}, {c[2]}, {SITUACAO.get(c[3], c[3])})? [s/N] ")
            if resp.strip().lower() not in ("s", "sim"):
                print(f"- Chamado {cid}: mantido.")
                continue
        # fotos: apaga os arquivos da pasta uploads (so pelo nome, por seguranca)
        for (caminho,) in db.execute("SELECT caminho FROM fotos_chamado WHERE chamado_id = ?", (cid,)).fetchall():
            arquivo = UPLOADS / Path(caminho).name
            if arquivo.is_file():
                arquivo.unlink()
        n_hist = db.execute("DELETE FROM historico_status WHERE chamado_id = ?", (cid,)).rowcount
        n_fotos = db.execute("DELETE FROM fotos_chamado WHERE chamado_id = ?", (cid,)).rowcount
        db.execute("DELETE FROM chamados WHERE id = ?", (cid,))
        db.commit()
        apagados += 1
        print(f"- Chamado {cid} ({c[1]}) apagado, com {n_hist} linha(s) de historico e {n_fotos} foto(s).")
    if apagados:
        totais(db)


def limpar(db):
    h = db.execute("DELETE FROM historico_status WHERE chamado_id NOT IN (SELECT id FROM chamados)").rowcount
    f = db.execute("DELETE FROM fotos_chamado WHERE chamado_id NOT IN (SELECT id FROM chamados)").rowcount
    db.commit()
    print(f"Sobras removidas: {h} linha(s) de historico e {f} foto(s) sem chamado.")
    totais(db)


def main():
    args = sys.argv[1:]
    sem_perguntar = "-y" in args
    ids = [int(a) for a in args if a.isdigit()]
    desconhecidos = [a for a in args if not a.isdigit() and a not in ("-y", "--limpar")]
    if desconhecidos:
        print("Nao entendi:", " ".join(desconhecidos))
        print(__doc__)
        return
    if not BANCO.exists():
        print(f"Nao achei o banco em {BANCO}.\nRode primeiro:  python seed.py")
        return
    db = sqlite3.connect(BANCO, timeout=10)
    try:
        if "--limpar" in args:
            limpar(db)
        elif ids:
            apagar(db, ids, sem_perguntar)
        else:
            listar(db)
    except sqlite3.OperationalError as erro:
        print(f"Nao consegui mexer no banco ({erro}).")
        print("Feche o DB Browser (ou qualquer programa com o ilumina.db aberto) e tente de novo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
