// Terça 25/08 — "O que é um PocketQube 1P" — LinkedIn — FUNDO CLARO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "light");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O QUE É UM", { x: 0.55, y: 2.2, w: 9, h: 0.9, fontSize: 40, bold: true, color: t.text });
  tx(s, "POCKETQUBE 1P?", { x: 0.55, y: 3.1, w: 9, h: 0.9, fontSize: 40, bold: true, color: ORANGE });
  card(s, 0.55, 4.6, 8.9, 4.6, { fill: t.card, edge: DEEP });
  s.addImage({ path: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/figures/1P_ALBA_ORBITAL_frame_p1.png`, x: 2.8, y: 4.85, w: 4.4, h: 4.1, sizing: { type: "contain", w: 4.4, h: 4.1 } });
  tx(s, "50 × 50 × 50 mm · ~200 g", { x: 0.55, y: 9.5, w: 8.9, h: 0.5, fontSize: 22, bold: true, fontFace: MONO, color: LILAC, align: "center" });
  tx(s, "O menor formato padronizado de satélite que existe.", { x: 0.55, y: 10.2, w: 8.9, h: 0.5, fontSize: 17, color: t.muted, align: "center" });
  logoBar(s);
}
// S2 comparação de formatos
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "POR QUE 1P E NÃO CUBESAT?", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  const rows = [
    ["CanSat", "sem envelope padronizado, sem herança de deployer", t.card],
    ["1U CubeSat", "10 cm, ~1 kg — consome o payload do Dédalo inteiro", t.card],
    ["1P PocketQube", "5 cm, ~200 g — cabe na classe de 800 g com folga", t.card2],
  ];
  let y = 2.6;
  rows.forEach(([nome, desc, fill], i) => {
    card(s, 0.55, y, 8.9, 1.5, { fill, edge: i === 2 ? DEEP : null });
    tx(s, nome, { x: 0.9, y: y + 0.25, w: 2.6, h: 0.5, fontSize: 21, bold: true, color: i === 2 ? ORANGE : t.muted });
    tx(s, desc, { x: 3.6, y: y + 0.25, w: 5.5, h: 1.0, fontSize: 15, color: t.text });
    y += 1.75;
  });
  tx(s, "Frame de voo doado pela Alba Orbital no LASC 2025 — estrutura de alumínio\ncom backplate de FRP. A estrutura veio pronta; o esforço foi todo no SRAB.",
     { x: 0.55, y: 8.2, w: 8.9, h: 1.0, fontSize: 15, color: t.muted });
  logoBar(s);
}
// S3 specs
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O HELIKE #213", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 34, bold: true, color: t.text });
  const specs = [
    ["RECUPERAÇÃO", "SRAB · 2 asas · passiva"],
    ["VELOCIDADE FINAL", "13.33 m/s (limite 20, SF 1.5)"],
    ["CÉREBRO", "ESP32-C3 · telemetria 5 Hz"],
    ["RÁDIO", "LoRa 915 MHz + GPS"],
    ["ARMAZENAMENTO", "SD card + LittleFS"],
    ["ENERGIA", "1300 mAh · ~8 h (req. 4 h)"],
  ];
  let y = 2.5;
  specs.forEach(([k, v]) => {
    tx(s, k, { x: 0.55, y, w: 3.3, h: 0.45, fontSize: 15, bold: true, fontFace: MONO, color: LILAC });
    tx(s, v, { x: 4.0, y, w: 5.4, h: 0.45, fontSize: 17, color: t.text });
    y += 0.85;
  });
  tx(s, "Nada importante depende de uma coisa só.", { x: 0.55, y: 7.9, w: 8.9, h: 0.5, fontSize: 19, bold: true, color: ORANGE });
  logoBar(s);
}
// S4 CTA
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "AMANHÃ: A FÍSICA", { x: 0.55, y: 3.2, w: 9, h: 0.8, fontSize: 36, bold: true, color: t.text });
  tx(s, "DA AUTORROTAÇÃO", { x: 0.55, y: 4.05, w: 9, h: 0.8, fontSize: 36, bold: true, color: ORANGE });
  tx(s, "↓", { x: 4.55, y: 5.3, w: 0.9, h: 0.9, fontSize: 44, bold: true, color: LILAC, align: "center" });
  tx(s, "github.com/ViniciusCMB/satellite", { x: 2.5, y: 6.6, w: 5, h: 0.4, fontSize: 16, bold: true, fontFace: MONO, color: LILAC, align: "center" });
  logoBar(s);
}

pres.writeFile({ fileName: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/slides/helike_ter.pptx` }).then(() => console.log("ok"));
