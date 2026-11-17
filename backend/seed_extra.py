"""Acrescenta dados de demonstracao (postes e chamados dos ultimos ~25 dias) ao banco atual.

Rode UMA vez, depois do seed.py:   python seed_extra.py
Nao apago nada e nao mexe nas contas. Pode ser rodado de novo sem duplicar.
Os chamados sao ficticios e as posicoes dos postes sao aproximadas.
"""
import random
from datetime import datetime, timedelta

from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)
db = SessionLocal()

dono = db.scalar(select(models.Usuario).where(models.Usuario.perfil == "cidadao", models.Usuario.ativo.is_(True)))
if not dono:
    raise SystemExit("Nenhum cidadao encontrado. Rode primeiro: python seed.py")

if db.scalar(select(models.Chamado).where(models.Chamado.protocolo == "2026-1001")):
    raise SystemExit("Os dados extras ja foram adicionados antes. Nada a fazer.")

novos_postes = [
    ("ILU-0512", "Av. Cruz Cabugá", "Santo Amaro", -8.0500, -34.8770),
    ("ILU-0633", "Av. Agamenon Magalhães", "Derby", -8.0558, -34.8995),
    ("ILU-0747", "Av. Rui Barbosa", "Graças", -8.0418, -34.8982),
    ("ILU-0815", "Rua do Bom Jesus", "Recife Antigo", -8.0627, -34.8715),
    ("ILU-0166", "Rua do Hospício", "Boa Vista", -8.0580, -34.8845),
]
for codigo, rua, bairro, lat, lng in novos_postes:
    if not db.scalar(select(models.Poste).where(models.Poste.codigo == codigo)):
        db.add(models.Poste(codigo=codigo, rua=rua, bairro=bairro, latitude=lat, longitude=lng))
db.flush()
postes = db.scalars(select(models.Poste)).all()

rnd = random.Random(7)  # resultado sempre igual
agora = datetime.utcnow()
combos = [
    "lampada_apagada", "lampada_apagada", "lampada_apagada", "lampada_apagada",
    "lampada_quebrada", "lampada_quebrada", "luz_acesa_de_dia", "luz_acesa_de_dia",
    "lampada_apagada,lampada_quebrada", "outro",
]
obs = [None, None, None, "Apagado há alguns dias.", "Rua ficou muito escura à noite.", "Perto de uma escola.", "Piscando desde ontem."]

for i in range(28):
    poste = rnd.choice(postes)
    criado = agora - timedelta(days=rnd.choice([0, 1, 1, 2, 3, 3, 4, 5, 6, 7, 8, 10, 12, 14, 17, 20, 24]), hours=rnd.randint(0, 20), minutes=rnd.randint(0, 59))
    sorteio = rnd.random()
    status = "resolvido" if sorteio < 0.58 else ("equipe_a_caminho" if sorteio < 0.82 else "recebido")
    tipo = rnd.choice(combos)
    c = models.Chamado(
        protocolo=f"2026-{1001 + i}", usuario_id=dono.id, poste_id=poste.id,
        rua=poste.rua, bairro=poste.bairro, codigo_poste=poste.codigo,
        latitude=poste.latitude, longitude=poste.longitude,
        tipo_problema=tipo, tem_lampada="quebrada" not in tipo, sem_energia=rnd.random() < 0.15,
        descricao=rnd.choice(obs), status=status, criado_em=criado, atualizado_em=criado,
        urgencia="alta" if (status != "resolvido" and rnd.random() < 0.2) else "normal",
    )
    c.historico.append(models.HistoricoStatus(status="recebido", criado_em=criado))
    if status in ("equipe_a_caminho", "resolvido"):
        caminho = min(criado + timedelta(hours=rnd.randint(2, 30)), agora)
        c.historico.append(models.HistoricoStatus(status="equipe_a_caminho", criado_em=caminho))
        c.atualizado_em = caminho
    if status == "resolvido":
        fim = min(caminho + timedelta(hours=rnd.randint(3, 72)), agora)
        c.historico.append(models.HistoricoStatus(status="resolvido", criado_em=fim))
        c.atualizado_em = fim
    db.add(c)

db.commit()
print("Pronto: 5 postes e 28 chamados de demonstracao adicionados!")
