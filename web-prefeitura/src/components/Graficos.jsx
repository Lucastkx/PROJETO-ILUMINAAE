import { useMemo } from "react";
import { STATUS, TIPOS } from "../util";

const DIA = 86400000;
const dt = (iso) => new Date(iso + "Z");
const pad = (n) => String(n).padStart(2, "0");
const chaveDia = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const rotuloDia = (d) => `${pad(d.getDate())}/${pad(d.getMonth() + 1)}`;

const ROTULO_SITUACAO = { recebido: "Aguardando equipe", equipe_a_caminho: "Equipe a caminho", resolvido: "Resolvido" };
const COR_SITUACAO = { recebido: "var(--bad)", equipe_a_caminho: "var(--manut)", resolvido: "var(--ok)" };

function dataResolucao(c) {
  if (c.status !== "resolvido") return null;
  const h = [...c.historico].reverse().find((x) => x.status === "resolvido");
  return dt(h ? h.criado_em : c.atualizado_em);
}

function fmtDuracao(ms) {
  const h = ms / 3600000;
  if (h < 1) return `${Math.max(1, Math.round(h * 60))} min`;
  if (h < 48) return `${h.toFixed(h < 10 ? 1 : 0).replace(".", ",")} h`;
  return `${(h / 24).toFixed(1).replace(".", ",")} dias`;
}

function calcular(chamados, periodo) {
  const agora = Date.now();
  const inicio = periodo ? agora - periodo * DIA : 0;
  const lista = chamados.filter((c) => dt(c.criado_em).getTime() >= inicio);

  const porSituacao = { recebido: 0, equipe_a_caminho: 0, resolvido: 0 };
  lista.forEach((c) => { porSituacao[c.status] += 1; });

  const resolvidos = lista.filter((c) => c.status === "resolvido");
  const duracoes = resolvidos.map((c) => dataResolucao(c) - dt(c.criado_em)).filter((x) => x >= 0);
  const tempoMedio = duracoes.length ? duracoes.reduce((a, b) => a + b, 0) / duracoes.length : null;
  const taxa = lista.length ? Math.round((resolvidos.length / lista.length) * 100) : null;

  const abertos = chamados.filter((c) => c.status !== "resolvido");
  const maisAntigo = abertos.length ? Math.max(...abertos.map((c) => agora - dt(c.criado_em).getTime())) : null;
  const urgentes = abertos.filter((c) => c.urgencia === "alta").length;

  const n = periodo === 7 ? 7 : 30;
  const dias = [];
  for (let i = n - 1; i >= 0; i--) {
    const data = new Date(agora - i * DIA);
    dias.push({ chave: chaveDia(data), data, criados: 0, resolvidos: 0 });
  }
  const idx = Object.fromEntries(dias.map((d, i) => [d.chave, i]));
  chamados.forEach((c) => {
    const k = chaveDia(dt(c.criado_em));
    if (k in idx) dias[idx[k]].criados += 1;
    const r = dataResolucao(c);
    if (r) {
      const kr = chaveDia(r);
      if (kr in idx) dias[idx[kr]].resolvidos += 1;
    }
  });

  const porBairro = {};
  lista.forEach((c) => {
    const b = (porBairro[c.bairro] ||= { bairro: c.bairro, abertos: 0, resolvidos: 0 });
    if (c.status === "resolvido") b.resolvidos += 1; else b.abertos += 1;
  });
  const bairros = Object.values(porBairro)
    .sort((a, b) => b.abertos + b.resolvidos - (a.abertos + a.resolvidos))
    .slice(0, 6);

  const porTipo = {};
  lista.forEach((c) => c.tipo_problema.split(",").filter(Boolean).forEach((t) => { porTipo[t] = (porTipo[t] || 0) + 1; }));
  const tipos = Object.entries(porTipo)
    .map(([t, qtd]) => ({ tipo: t, nome: TIPOS[t] ?? t, qtd }))
    .sort((a, b) => b.qtd - a.qtd);

  return { lista, porSituacao, tempoMedio, taxa, abertos: abertos.length, maisAntigo, urgentes, dias, bairros, tipos };
}

function Rosca({ valores, total, onSituacao }) {
  const R = 54;
  const C = 2 * Math.PI * R;
  let acum = 0;
  const resumo = Object.keys(ROTULO_SITUACAO).map((k) => `${ROTULO_SITUACAO[k]}: ${valores[k]}`).join(", ");
  return (
    <div className="rosca">
      <svg viewBox="0 0 140 140" role="img" aria-label={`Chamados por situação. ${resumo}`}>
        <circle cx="70" cy="70" r={R} fill="none" stroke="#e8edf3" strokeWidth="18" />
        {total > 0 && Object.keys(COR_SITUACAO).map((k) => {
          const v = valores[k];
          if (!v) return null;
          const len = (v / total) * C;
          const el = (
            <circle key={k} cx="70" cy="70" r={R} fill="none" strokeWidth="18"
              style={{ stroke: COR_SITUACAO[k] }}
              strokeDasharray={`${len} ${C - len}`} strokeDashoffset={-acum}
              transform="rotate(-90 70 70)">
              <title>{`${ROTULO_SITUACAO[k]}: ${v}`}</title>
            </circle>
          );
          acum += len;
          return el;
        })}
        <text x="70" y="70" textAnchor="middle" className="rosca-n">{total}</text>
        <text x="70" y="88" textAnchor="middle" className="rosca-l">chamados</text>
      </svg>
      <ul className="rosca-leg">
        {Object.keys(ROTULO_SITUACAO).map((k) => (
          <li key={k}>
            <button onClick={() => onSituacao(k)} title="Ver no mapa">
              <i className="bolinha" style={{ background: COR_SITUACAO[k] }} />
              <span className="espaco">{ROTULO_SITUACAO[k]}</span>
              <b>{valores[k]}</b>
              <small>{total ? `${Math.round((valores[k] / total) * 100)}%` : "–"}</small>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PorDia({ dias }) {
  const W = 620, H = 240, L = 32, B = 30, T = 14, Rm = 10;
  const pw = W - L - Rm;
  const ph = H - T - B;
  const max = Math.max(1, ...dias.flatMap((d) => [d.criados, d.resolvidos]));
  const topo = max <= 4 ? max : Math.ceil(max / 2) * 2;
  const y = (v) => T + ph - (v / topo) * ph;
  const bw = pw / dias.length;
  const passo = dias.length > 14 ? 5 : 1;
  const ticks = [...new Set([0, Math.round(topo / 2), topo])];
  const linha = dias.map((d, i) => `${L + bw * i + bw / 2},${y(d.resolvidos)}`).join(" ");
  const totCriados = dias.reduce((a, d) => a + d.criados, 0);
  const totRes = dias.reduce((a, d) => a + d.resolvidos, 0);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" className="g-svg"
      aria-label={`Chamados abertos e resolvidos por dia nos últimos ${dias.length} dias. Total aberto: ${totCriados}. Total resolvido: ${totRes}.`}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - Rm} y1={y(t)} y2={y(t)} className="g-grade" />
          <text x={L - 6} y={y(t) + 4} textAnchor="end" className="g-eixo">{t}</text>
        </g>
      ))}
      {dias.map((d, i) => (
        <g key={d.chave}>
          <rect x={L + bw * i + bw * 0.2} y={y(d.criados)} width={bw * 0.6} height={Math.max(0, ph - (y(d.criados) - T))}
            rx="3" className="b-criados">
            <title>{`${rotuloDia(d.data)}: ${d.criados} abertos, ${d.resolvidos} resolvidos`}</title>
          </rect>
          {(dias.length - 1 - i) % passo === 0 && (
            <text x={L + bw * i + bw / 2} y={H - 10} textAnchor="middle" className="g-eixo">{rotuloDia(d.data)}</text>
          )}
        </g>
      ))}
      <polyline points={linha} className="l-res" />
      {dias.map((d, i) => (
        <circle key={d.chave} cx={L + bw * i + bw / 2} cy={y(d.resolvidos)} r="3.5" className="p-res">
          <title>{`${rotuloDia(d.data)}: ${d.resolvidos} resolvidos`}</title>
        </circle>
      ))}
    </svg>
  );
}

export default function Graficos({ chamados, periodo, carregou, onBairro, onSituacao }) {
  const d = useMemo(() => calcular(chamados, periodo), [chamados, periodo]);
  if (!carregou) return <p className="sub" style={{ padding: 24 }}>Carregando…</p>;

  const maxBairro = d.bairros.length ? d.bairros[0].abertos + d.bairros[0].resolvidos : 1;
  const maxTipo = d.tipos.length ? d.tipos[0].qtd : 1;
  const nomePeriodo = periodo === 0 ? "em todo o período" : `nos últimos ${periodo} dias`;

  return (
    <div className="graficos">
      <section className="kpis" aria-label="Indicadores">
        <div className="kpi"><span>Chamados no período</span><b>{d.lista.length}</b></div>
        <div className="kpi"><span>Taxa de resolução</span><b>{d.taxa === null ? "–" : `${d.taxa}%`}</b></div>
        <div className="kpi"><span>Tempo médio de resolução</span><b>{d.tempoMedio === null ? "–" : fmtDuracao(d.tempoMedio)}</b></div>
        <div className="kpi"><span>Em aberto agora</span><b>{d.abertos}</b><small>{d.urgentes} {d.urgentes === 1 ? "urgente" : "urgentes"}</small></div>
        <div className="kpi"><span>Aberto há mais tempo</span><b>{d.maisAntigo === null ? "–" : fmtDuracao(d.maisAntigo)}</b></div>
      </section>

      <div className="g-grid">
        <section className="g-card">
          <h3>Chamados por situação</h3>
          <p className="pequeno">Chamados abertos {nomePeriodo}</p>
          <Rosca valores={d.porSituacao} total={d.lista.length} onSituacao={onSituacao} />
        </section>

        <section className="g-card g-larga">
          <h3>Abertos e resolvidos por dia</h3>
          <p className="pequeno">
            <i className="bolinha" style={{ background: "var(--amber)" }} /> Chamados abertos no dia
            <span className="g-esp" />
            <i className="bolinha" style={{ background: "var(--ok)", borderRadius: "50%" }} /> Chamados resolvidos no dia
          </p>
          <PorDia dias={d.dias} />
        </section>

        <section className="g-card">
          <h3>Por bairro</h3>
          <p className="pequeno">
            <i className="bolinha" style={{ background: "var(--ink)" }} /> Em aberto
            <span className="g-esp" />
            <i className="bolinha" style={{ background: "var(--ok)" }} /> Resolvidos
            <span className="g-esp" />Clique para ver no mapa
          </p>
          {d.bairros.length === 0 ? <p className="sub">Sem chamados {nomePeriodo}.</p> : (
            <ul className="barras">
              {d.bairros.map((b) => (
                <li key={b.bairro}>
                  <button className="barra-linha" onClick={() => onBairro(b.bairro)} title={`Ver ${b.bairro} no mapa`}>
                    <span className="barra-nome">{b.bairro}</span>
                    <span className="barra-trilho">
                      <i className="aberto" style={{ width: `${(b.abertos / maxBairro) * 100}%` }} />
                      <i className="resolvido" style={{ width: `${(b.resolvidos / maxBairro) * 100}%` }} />
                    </span>
                    <span className="barra-num">{b.abertos + b.resolvidos}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="g-card">
          <h3>Tipos de problema</h3>
          <p className="pequeno">Um chamado com mais de um problema conta em cada um deles</p>
          {d.tipos.length === 0 ? <p className="sub">Sem chamados {nomePeriodo}.</p> : (
            <ul className="barras">
              {d.tipos.map((t) => (
                <li key={t.tipo}>
                  <div className="barra-linha estatica">
                    <span className="barra-nome">{t.nome}</span>
                    <span className="barra-trilho"><i className="tipo" style={{ width: `${(t.qtd / maxTipo) * 100}%` }} /></span>
                    <span className="barra-num">{t.qtd}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
