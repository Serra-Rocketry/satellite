// Sexta 28/08 — "O TIME" — Instagram — FUNDO ESCURO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "dark");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "QUEM FEZ", { x: 0.55, y: 2.6, w: 9, h: 1.0, fontSize: 46, bold: true, color: t.text });
  tx(s, "O HELIKE?", { x: 0.55, y: 3.6, w: 9, h: 1.0, fontSize: 46, bold: true, color: ORANGE });
  tx(s, "O time por trás do projeto", { x: 0.55, y: 4.8, w: 9, h: 0.6, fontSize: 22, color: LILAC, bold: true });
  logoBar(s);
}
// S2 áreas (estrutura/SRAB + eletrônica/firmware)
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "QUEM CUIDA DO QUÊ", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  card(s, 0.55, 2.5, 4.5, 4.2);
  tx(s, "ESTRUTURA + SRAB", { x: 0.85, y: 2.75, w: 3.9, h: 0.5, fontSize: 19, bold: true, color: ORANGE });
  tx(s, "[NOME 1]\n[NOME 2]", { x: 0.85, y: 3.5, w: 3.9, h: 1.2, fontSize: 18, bold: true, fontFace: MONO, color: t.text });
  tx(s, "geometria das asas, mecanismo\npassivo, integração mecânica", { x: 0.85, y: 5.0, w: 3.9, h: 1.4, fontSize: 14, color: t.muted });
  card(s, 5.35, 2.5, 4.5, 4.2);
  tx(s, "ELETRÔNICA + FIRMWARE", { x: 5.65, y: 2.75, w: 3.9, h: 0.5, fontSize: 19, bold: true, color: ORANGE });
  tx(s, "[NOME 3]\n[NOME 4]", { x: 5.65, y: 3.5, w: 3.9, h: 1.2, fontSize: 18, bold: true, fontFace: MONO, color: t.text });
  tx(s, "ESP32-C3, sensores, LoRa,\nloop de voo 5 Hz, watchdog", { x: 5.65, y: 5.0, w: 3.9, h: 1.4, fontSize: 14, color: t.muted });
  logoBar(s);
}
// S3 áreas (simulação/doc) + como começou
{
  const s = pres.addSlide();
  marker(s);
  card(s, 0.55, 1.3, 4.5, 3.4);
  tx(s, "SIMULAÇÃO + DOCS", { x: 0.85, y: 1.55, w: 3.9, h: 0.5, fontSize: 19, bold: true, color: ORANGE });
  tx(s, "[NOME 5]\n[NOME 6]", { x: 0.85, y: 2.25, w: 3.9, h: 1.2, fontSize: 18, bold: true, fontFace: MONO, color: t.text });
  tx(s, "RocketPy, Monte Carlo,\nmission report, compliance", { x: 0.85, y: 3.6, w: 3.9, h: 1.0, fontSize: 14, color: t.muted });
  card(s, 5.35, 1.3, 4.5, 3.4);
  tx(s, "COMO COMEÇOU", { x: 5.65, y: 1.55, w: 3.9, h: 0.5, fontSize: 19, bold: true, color: ORANGE });
  tx(s, "Time universitário do IPRJ-UERJ,\nautofinanciado, aprendendo fazendo.\nSeis pessoas dividindo tudo.",
     { x: 5.65, y: 2.25, w: 3.9, h: 1.9, fontSize: 15, color: t.text });
  tx(s, "Seis nomes, seis funções — preencher antes de publicar.",
     { x: 0.55, y: 5.2, w: 8.9, h: 0.5, fontSize: 15, fontFace: MONO, color: ORANGE });
  logoBar(s);
}
// S4 CTA
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "QUER VER ESSE CUBO", { x: 0.55, y: 3.2, w: 9, h: 0.8, fontSize: 36, bold: true, color: t.text });
  tx(s, "CAINDO E GIRANDO?", { x: 0.55, y: 4.05, w: 9, h: 0.8, fontSize: 36, bold: true, color: ORANGE });
  tx(s, "Siga — lançamento dia [DATA].", { x: 0.55, y: 5.3, w: 9, h: 0.6, fontSize: 20, color: LILAC, bold: true });
  logoBar(s);
}

pres.writeFile({ fileName: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/slides/helike_sex.pptx` }).then(() => console.log("ok"));
