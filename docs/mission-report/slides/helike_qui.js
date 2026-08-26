// Quinta 27/08 — "Da semente ao código" — Instagram — FUNDO CLARO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "light");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "DE UMA SAMARA", { x: 0.55, y: 2.4, w: 9, h: 0.9, fontSize: 42, bold: true, color: t.text });
  tx(s, "A UM SATÉLITE", { x: 0.55, y: 3.3, w: 9, h: 0.9, fontSize: 42, bold: true, color: t.text });
  tx(s, "NATUREZA → EQUAÇÃO → CÓDIGO", { x: 0.55, y: 4.6, w: 9, h: 0.6, fontSize: 22, bold: true, fontFace: MONO, color: LILAC });
  card(s, 1.5, 5.8, 7.0, 4.0, { fill: t.card, edge: DEEP });
  s.addImage({ path: `${A}/membro_segurando_a_versao_asa2_sem_fundo.png`, x: 2.4, y: 5.95, w: 5.2, h: 3.7, sizing: { type: "contain", w: 5.2, h: 3.7 } });
  logoBar(s);
}
// S2 a iteração
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "TRÊS GERAÇÕES DE ASAS", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 34, bold: true, color: t.text });
  const asas = [
    ["ASA1", "7.68 m/s", "primeira queda estável"],
    ["ASA2", "8.04 m/s", "eletrônica embarcada validada"],
    ["ASA3", "12.90 m/s", "geometria final, 2 asas"],
  ];
  asas.forEach(([nome, v, d], i) => {
    const x = 0.55 + i * 3.05;
    card(s, x, 2.5, 2.8, 3.6, { fill: t.card, edge: i === 2 ? DEEP : null });
    tx(s, nome, { x: x + 0.2, y: 2.75, w: 2.4, h: 0.5, fontSize: 22, bold: true, color: i === 2 ? ORANGE : t.muted });
    tx(s, v, { x: x + 0.2, y: 3.4, w: 2.4, h: 0.6, fontSize: 24, bold: true, fontFace: MONO, color: LILAC });
    tx(s, d, { x: x + 0.2, y: 4.2, w: 2.4, h: 1.6, fontSize: 14, color: t.text });
    if (i < 2) tx(s, "→", { x: x + 2.78, y: 3.9, w: 0.3, h: 0.5, fontSize: 24, bold: true, color: ORANGE, align: "center" });
  });
  tx(s, "Cada queda de drone gerava dados. Cada dado gerava a próxima asa.",
     { x: 0.55, y: 6.6, w: 8.9, h: 0.6, fontSize: 18, bold: true, color: t.text });
  tx(s, "valores de impacto nos drop tests (~20-30 m)", { x: 0.55, y: 7.3, w: 8.9, h: 0.4, fontSize: 13, fontFace: MONO, color: t.muted });
  logoBar(s);
}
// S3 o código
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "E ISSO TUDO VIROU CÓDIGO", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 34, bold: true, color: t.text });
  card(s, 0.55, 2.4, 8.9, 4.6, { fill: t.card, edge: DEEP });
  tx(s, "// loop de voo — roda 5x por segundo\nwhile (true) {\n  ler_sensores();        // IMU, pressão, GPS\n  validar_dados();       // descarta leitura ruim\n  transmitir_lora();     // manda pra base\n  gravar_sd();           // guarda tudo\n}",
    { x: 0.95, y: 2.7, w: 8.1, h: 4.0, fontSize: 16, fontFace: MONO, color: t.text, lineSpacing: 26 });
  tx(s, "1 loop, 5 medições por segundo · se travar, o chip reinicia sozinho",
     { x: 0.55, y: 7.3, w: 8.9, h: 0.5, fontSize: 17, bold: true, color: ORANGE });
  tx(s, "esse código voa dentro de 5 × 5 × 5 cm", { x: 0.55, y: 8.1, w: 8.9, h: 0.45, fontSize: 16, color: t.muted });
  logoBar(s);
}
// S4 CTA
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O RESULTADO?", { x: 0.55, y: 3.0, w: 9, h: 0.8, fontSize: 38, bold: true, color: t.text });
  tx(s, "~470 RPM GIRANDO", { x: 0.55, y: 3.9, w: 9, h: 0.8, fontSize: 38, bold: true, color: ORANGE });
  tx(s, "ATÉ POUSAR.", { x: 0.55, y: 4.8, w: 9, h: 0.8, fontSize: 38, bold: true, color: ORANGE });
  tx(s, "Amanhã: o time por trás disso.", { x: 0.55, y: 6.1, w: 9, h: 0.6, fontSize: 20, color: LILAC, bold: true });
  logoBar(s);
}

pres.writeFile({ fileName: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/slides/helike_qui.pptx` }).then(() => console.log("ok"));
