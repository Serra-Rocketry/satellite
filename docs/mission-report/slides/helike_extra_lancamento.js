// EXTRA 2 — Dia de LANÇAMENTO (03–05/09) — IG + LinkedIn — FUNDO CLARO
// Duas versões de caption prontas (sucesso/falha parcial); slides neutros que servem pra ambas.
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "light");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa (neutra — serve pra sucesso ou falha parcial)
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O VOO", { x: 0.55, y: 2.8, w: 9, h: 1.1, fontSize: 54, bold: true, color: t.text });
  tx(s, "ACONTECEU.", { x: 0.55, y: 3.9, w: 9, h: 1.1, fontSize: 54, bold: true, color: ORANGE });
  tx(s, "Helike #213 · LASC 2026 · [DATA]", { x: 0.55, y: 5.2, w: 9, h: 0.5, fontSize: 16, fontFace: MONO, color: t.muted, align: "center" });
  logoBar(s);
}
// S2 status honesto
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "STATUS DA MISSÃO", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  const checks = [
    ["EJEÇÃO", "o Helike foi ejetado do Dédalo no apogeu?", "[preencher]"],
    ["SRAB", "as asas abriram e a descida foi autorrotativa?", "[preencher]"],
    ["TELEMETRIA", "recebemos os pacotes LoRa na ground station?", "[preencher]"],
    ["RECUPERAÇÃO", "o satélite foi localizado e recuperado?", "[preencher]"],
  ];
  let y = 2.4;
  checks.forEach(([k, q, r]) => {
    card(s, 0.55, y, 8.9, 1.35);
    tx(s, k, { x: 0.9, y: y + 0.18, w: 2.6, h: 0.45, fontSize: 17, bold: true, fontFace: MONO, color: LILAC });
    tx(s, q, { x: 3.7, y: y + 0.18, w: 4.2, h: 0.95, fontSize: 14, color: t.text });
    tx(s, r, { x: 7.95, y: y + 0.18, w: 1.35, h: 0.45, fontSize: 13, fontFace: MONO, color: t.muted });
    y += 1.6;
  });
  tx(s, "Análise completa dos dados no post-mortem técnico.", { x: 0.55, y: 8.9, w: 8.9, h: 0.5, fontSize: 15, color: t.muted });
  logoBar(s);
}
// S3 previsto × realizado
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "PREVISTO × REALIZADO", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  const rows = [
    ["APOGEU", "1520 m (simulado)", "[real]"],
    ["DESCIDA", "111 s (simulado)", "[real]"],
    ["IMPACTO", "13.33 m/s (simulado)", "[real]"],
  ];
  let y = 2.4;
  rows.forEach(([k, prev, real]) => {
    card(s, 0.55, y, 8.9, 1.3);
    tx(s, k, { x: 0.9, y: y + 0.18, w: 2.2, h: 0.45, fontSize: 16, bold: true, fontFace: MONO, color: t.muted });
    tx(s, prev, { x: 3.3, y: y + 0.18, w: 3.2, h: 0.45, fontSize: 15, color: t.text });
    tx(s, real, { x: 6.7, y: y + 0.18, w: 2.5, h: 0.45, fontSize: 15, bold: true, fontFace: MONO, color: ORANGE });
    y += 1.55;
  });
  tx(s, "Onde o modelo acertou — e onde errou — no post-mortem.",
     { x: 0.55, y: 7.2, w: 8.9, h: 0.5, fontSize: 16, bold: true, color: t.text });
  logoBar(s);
}
// S4 CTA
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "POST-MORTEM TÉCNICO", { x: 0.55, y: 3.4, w: 9, h: 0.8, fontSize: 36, bold: true, color: t.text });
  tx(s, "NA PRÓXIMA SEMANA", { x: 0.55, y: 4.3, w: 9, h: 0.8, fontSize: 36, bold: true, color: ORANGE });
  tx(s, "Sucessos, falhas e todos os dados. Sem filtro.", { x: 0.55, y: 5.5, w: 9, h: 0.6, fontSize: 18, color: t.muted, align: "center" });
  logoBar(s);
}

pres.writeFile({ fileName: "/tmp/helike_extra_lancamento.pptx" }).then(() => console.log("ok"));
