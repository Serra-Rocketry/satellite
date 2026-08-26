// EXTRA 1 — 02/09 (abertura da LASC) — Instagram — FUNDO ESCURO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "dark");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "ESTAMOS EM IACANGA", { x: 0.55, y: 2.6, w: 9, h: 0.9, fontSize: 38, bold: true, color: t.text });
  tx(s, "LASC 2026 COMEÇA HOJE", { x: 0.55, y: 3.5, w: 9, h: 0.9, fontSize: 38, bold: true, color: ORANGE });
  tx(s, "[foto da chegada/montagem do stand]", { x: 0.55, y: 5.2, w: 8.9, h: 0.5, fontSize: 15, fontFace: MONO, color: t.muted, align: "center" });
  logoBar(s);
}
// S2 o que levamos
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O QUE A GENTE LEVOU", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  card(s, 0.55, 2.5, 8.9, 1.6);
  tx(s, "HELIKE #213", { x: 0.9, y: 2.75, w: 8.1, h: 0.5, fontSize: 20, bold: true, color: LILAC });
  tx(s, "o PocketQube com o SRAB, pronto pra integrar no deployer", { x: 0.9, y: 3.3, w: 8.1, h: 0.45, fontSize: 14, color: t.muted });
  card(s, 0.55, 4.4, 8.9, 1.6);
  tx(s, "GROUND STATION", { x: 0.9, y: 4.65, w: 8.1, h: 0.5, fontSize: 20, bold: true, color: LILAC });
  tx(s, "estação LoRa pra receber a telemetria ao vivo da descida", { x: 0.9, y: 5.2, w: 8.1, h: 0.45, fontSize: 14, color: t.muted });
  tx(s, "[foto da integração no Dédalo quando acontecer]", { x: 0.55, y: 6.5, w: 8.9, h: 0.5, fontSize: 15, fontFace: MONO, color: t.muted, align: "center" });
  logoBar(s);
}
// S3 agenda da equipe
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "AGENDA 02–05/09", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  const agenda = [
    ["02/09", "abertura, credenciamento, montagem do stand"],
    ["03–05/09", "janela de lançamento — Helike no Dédalo #11"],
    ["[DIA]", "apresentação técnica na bancada [preencher]"],
  ];
  let y = 2.5;
  agenda.forEach(([d, ev]) => {
    card(s, 0.55, y, 8.9, 1.3);
    tx(s, d, { x: 0.9, y: y + 0.2, w: 2.2, h: 0.5, fontSize: 18, bold: true, fontFace: MONO, color: LILAC });
    tx(s, ev, { x: 3.3, y: y + 0.2, w: 5.8, h: 0.9, fontSize: 15, color: t.text });
    y += 1.55;
  });
  tx(s, "Acompanhe tudo nos stories.", { x: 0.55, y: 7.5, w: 8.9, h: 0.5, fontSize: 18, bold: true, color: ORANGE });
  logoBar(s);
}
// S4 CTA
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "LANÇAMENTO PREVISTO", { x: 0.55, y: 3.4, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  tx(s, "PARA [DIA 03–05/09]", { x: 0.55, y: 4.2, w: 9, h: 0.8, fontSize: 36, bold: true, fontFace: MONO, color: ORANGE, align: "center" });
  tx(s, "Ative as notificações.", { x: 0.55, y: 5.4, w: 9, h: 0.6, fontSize: 20, color: LILAC, bold: true, align: "center" });
  logoBar(s);
}

pres.writeFile({ fileName: "/tmp/helike_extra_abertura.pptx" }).then(() => console.log("ok"));
