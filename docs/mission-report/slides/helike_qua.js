// Quarta 26/08 — "A biologia: samara + LEV" — Instagram — FUNDO ESCURO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "dark");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  card(s, 5.15, 1.9, 4.55, 3.4, { fill: t.card, edge: DEEP });
  s.addImage({ path: `${A}/vista_superior_samara_seed.png`, x: 5.3, y: 2.25, w: 4.25, h: 2.56 });
  tx(s, "A NATUREZA", { x: 0.55, y: 2.5, w: 4.5, h: 0.85, fontSize: 40, bold: true, color: t.text });
  tx(s, "RESOLVEU ISSO", { x: 0.55, y: 3.35, w: 4.5, h: 0.85, fontSize: 40, bold: true, color: t.text });
  tx(s, "HÁ MILHÕES DE ANOS.", { x: 0.55, y: 4.2, w: 4.6, h: 0.85, fontSize: 40, bold: true, color: ORANGE });
  tx(s, "A gente só copiou.", { x: 0.55, y: 5.6, w: 4.5, h: 0.6, fontSize: 22, color: LILAC, bold: true });
  logoBar(s);
}
// S2 o conceito
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "A SAMARA", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 34, bold: true, color: t.text });
  tx(s, "(SEMENTE DE BORDO)", { x: 0.55, y: 2.05, w: 9, h: 0.6, fontSize: 24, bold: true, color: LILAC });
  card(s, 0.55, 3.0, 4.5, 3.4);
  tx(s, "PESO DE UM LADO", { x: 0.85, y: 3.25, w: 3.9, h: 0.45, fontSize: 19, bold: true, color: ORANGE });
  tx(s, "O centro de massa fica numa ponta da semente.", { x: 0.85, y: 3.8, w: 3.9, h: 0.9, fontSize: 15, color: t.text });
  card(s, 5.35, 3.0, 4.5, 3.4);
  tx(s, "SUSTENTAÇÃO NO OUTRO", { x: 5.65, y: 3.25, w: 3.9, h: 0.45, fontSize: 19, bold: true, color: ORANGE });
  tx(s, "A asa gera sustentação na ponta oposta — o desequilíbrio faz a semente girar em queda.", { x: 5.65, y: 3.8, w: 3.9, h: 1.4, fontSize: 15, color: t.text });
  tx(s, "Girando, a asa gera sustentação extra: é isso que segura a queda.\nO vórtice de borda de ataque (LEV) dobra esse efeito.",
     { x: 0.55, y: 6.9, w: 8.9, h: 1.1, fontSize: 17, bold: true, color: t.text });
  logoBar(s);
}
// S3 do conceito ao satélite
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O HELIKE COPIA ISSO", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 34, bold: true, color: t.text });
  card(s, 0.55, 2.4, 8.9, 4.9);
  s.addImage({ path: `${A}/versao_asa2_ao_lado_de_varias_sementes.png`, x: 1.15, y: 2.7, w: 7.7, h: 4.3, sizing: { type: "contain", w: 7.7, h: 4.3 } });
  tx(s, "asa do Helike ao lado das sementes que a inspiraram", { x: 0.55, y: 7.5, w: 8.9, h: 0.4, fontSize: 14, fontFace: MONO, color: t.muted, align: "center" });
  tx(s, "Sem motor. Sem comando. Só aerodinâmica.", { x: 0.55, y: 8.3, w: 8.9, h: 0.5, fontSize: 19, bold: true, color: ORANGE });
  logoBar(s);
}
// S4 CTA
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "AMANHÃ: DA SEMENTE", { x: 0.55, y: 3.2, w: 9, h: 0.8, fontSize: 36, bold: true, color: t.text });
  tx(s, "AO CÓDIGO", { x: 0.55, y: 4.05, w: 9, h: 0.8, fontSize: 36, bold: true, color: ORANGE });
  tx(s, "↓", { x: 4.55, y: 5.3, w: 0.9, h: 0.9, fontSize: 44, bold: true, color: LILAC, align: "center" });
  tx(s, "github.com/ViniciusCMB/satellite", { x: 2.5, y: 6.6, w: 5, h: 0.4, fontSize: 16, bold: true, fontFace: MONO, color: LILAC, align: "center" });
  logoBar(s);
}

pres.writeFile({ fileName: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/slides/helike_qua.pptx` }).then(() => console.log("ok"));
