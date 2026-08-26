// Domingo 30/08 — "Countdown" — Instagram — FUNDO ESCURO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "dark");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "[DATA]", { x: 0.55, y: 3.0, w: 8.9, h: 1.4, fontSize: 72, bold: true, fontFace: MONO, color: LILAC, align: "center" });
  tx(s, "O HELIKE VOA", { x: 0.55, y: 4.6, w: 8.9, h: 0.9, fontSize: 40, bold: true, color: ORANGE, align: "center" });
  tx(s, "LASC 2026 · foguete Dédalo #11", { x: 0.55, y: 5.7, w: 8.9, h: 0.5, fontSize: 16, fontFace: MONO, color: t.muted, align: "center" });
  logoBar(s);
}
// S2 o que vai acontecer
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O QUE VAI ACONTECER", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  const steps = [
    ["SUBIDA", "o Dédalo leva o Helike a ~1520 m de altitude"],
    ["EJEÇÃO", "o deployer solta o satélite — e as asas abrem sozinhas"],
    ["DESCIDA", "~111 s girando como uma semente, até o solo"],
  ];
  let y = 2.5;
  steps.forEach(([t_, d], i) => {
    card(s, 0.55, y, 8.9, 1.5);
    tx(s, t_, { x: 0.9, y: y + 0.22, w: 2.6, h: 0.5, fontSize: 20, bold: true, fontFace: MONO, color: LILAC });
    tx(s, d, { x: 3.7, y: y + 0.22, w: 5.4, h: 1.0, fontSize: 15, color: t.text });
    y += 1.8;
  });
  logoBar(s);
}
// S3 onde acompanhar
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "ONDE ACOMPANHAR", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  card(s, 0.55, 2.5, 8.9, 1.6);
  tx(s, "STORIES @SerraRocketry", { x: 0.9, y: 2.75, w: 8.1, h: 0.5, fontSize: 20, bold: true, color: LILAC });
  tx(s, "cobertura ao vivo da equipe em solo", { x: 0.9, y: 3.3, w: 8.1, h: 0.45, fontSize: 14, color: t.muted });
  card(s, 0.55, 4.4, 8.9, 1.6);
  tx(s, "TRANSMISSÃO OFICIAL LASC", { x: 0.9, y: 4.65, w: 8.1, h: 0.5, fontSize: 20, bold: true, color: LILAC });
  tx(s, "[link quando sair]", { x: 0.9, y: 5.2, w: 8.1, h: 0.45, fontSize: 14, fontFace: MONO, color: t.muted });
  tx(s, "Telemetria LoRa ao vivo na ground station durante a descida.",
     { x: 0.55, y: 6.5, w: 8.9, h: 0.5, fontSize: 16, color: t.text });
  logoBar(s);
}
// S4 CTA
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "ATIVE AS NOTIFICAÇÕES", { x: 0.55, y: 3.4, w: 9, h: 0.8, fontSize: 36, bold: true, color: t.text });
  tx(s, "[DATA] · ÀS [HORA]", { x: 0.55, y: 4.3, w: 9, h: 0.9, fontSize: 40, bold: true, fontFace: MONO, color: ORANGE, align: "center" });
  tx(s, "Toda a validação que mostramos essa semana vai ser testada de verdade.",
     { x: 0.55, y: 5.7, w: 9, h: 0.8, fontSize: 18, color: t.muted, align: "center" });
  logoBar(s);
}

pres.writeFile({ fileName: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/slides/helike_dom.pptx` }).then(() => console.log("ok"));
