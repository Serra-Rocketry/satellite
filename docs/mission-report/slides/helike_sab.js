// Sábado 29/08 — "Simulamos o voo inteiro" — LinkedIn — FUNDO CLARO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "light");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "SIMULAMOS O VOO", { x: 0.55, y: 2.4, w: 9, h: 0.9, fontSize: 40, bold: true, color: t.text });
  tx(s, "INTEIRO ANTES DELE EXISTIR", { x: 0.55, y: 3.3, w: 9.2, h: 0.9, fontSize: 40, bold: true, color: t.text });
  tx(s, "E QUANDO O SIMULADOR NÃO TINHA O QUE\nA GENTE PRECISAVA, ESCREVEMOS.",
     { x: 0.55, y: 4.7, w: 9, h: 1.0, fontSize: 20, bold: true, fontFace: MONO, color: LILAC });
  logoBar(s);
}
// S2 o obstáculo
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "O OBSTÁCULO", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  card(s, 0.55, 2.4, 8.9, 3.4);
  tx(s, "Simuladores de foguete (usamos o RocketPy, open source) sabem\nduas coisas muito bem:", { x: 0.95, y: 2.7, w: 8.1, h: 1.0, fontSize: 17, color: t.text });
  tx(s, "✓ subida propelida\n✓ descida sob paraquedas", { x: 0.95, y: 3.8, w: 8.1, h: 1.0, fontSize: 18, bold: true, color: LILAC });
  tx(s, "O Helike não desce sob paraquedas. Ele desce GIRANDO, como uma semente.\nNão tinha botão pra isso.",
     { x: 0.55, y: 6.2, w: 8.9, h: 1.1, fontSize: 19, bold: true, color: ORANGE });
  logoBar(s);
}
// S3 a solução
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "A SOLUÇÃO: ACOPLAR OS DOIS MUNDOS", { x: 0.55, y: 1.3, w: 9, h: 0.6, fontSize: 30, bold: true, color: t.text });
  const steps = [
    ["SUBIDA", "o Dédalo sobe no simulador padrão, até o apogeu", t.card],
    ["APOGEU 1520 m", "o estado exato (posição + velocidade) é herdado", t.card2],
    ["DESCIDA", "equação própria do SRAB integra a queda até o solo", t.card],
  ];
  let y = 2.5;
  steps.forEach(([t_, d, fill], i) => {
    card(s, 0.55, y, 8.9, 1.55, { fill, edge: i === 1 ? DEEP : null });
    tx(s, t_, { x: 0.9, y: y + 0.2, w: 3.0, h: 0.5, fontSize: 20, bold: true, fontFace: MONO, color: i === 1 ? ORANGE : t.muted });
    tx(s, d, { x: 4.1, y: y + 0.2, w: 5.0, h: 1.1, fontSize: 15, color: t.text });
    if (i < 2) tx(s, "↓", { x: 4.75, y: y + 1.45, w: 0.5, h: 0.4, fontSize: 22, bold: true, color: LILAC, align: "center" });
    y += 1.95;
  });
  tx(s, "mesma atmosfera, mesmo vento, um único ponto de hand-off",
     { x: 0.55, y: 8.5, w: 8.9, h: 0.45, fontSize: 15, fontFace: MONO, color: t.muted, align: "center" });
  logoBar(s);
}
// S4 números
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "OS NÚMEROS", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  const nums = [
    ["1520 m", "apogeu do Dédalo com payload"],
    ["111 s", "de descida autorrotando"],
    ["13.33 m/s", "impacto — o alvo de projeto exato (20/1.5)"],
    ["100/100", "cenários do teste de estresse dentro do limite"],
  ];
  let y = 2.5;
  nums.forEach(([n, d]) => {
    tx(s, n, { x: 0.55, y, w: 2.9, h: 0.6, fontSize: 26, bold: true, fontFace: MONO, color: ORANGE });
    tx(s, d, { x: 3.7, y: y + 0.08, w: 5.6, h: 0.55, fontSize: 16, color: t.text });
    y += 1.05;
  });
  tx(s, "Tudo open source. No dia [DATA], a simulação encontra o voo real.",
     { x: 0.55, y: 7.0, w: 8.9, h: 0.6, fontSize: 18, bold: true, color: t.text });
  tx(s, "github.com/ViniciusCMB/satellite", { x: 0.55, y: 7.7, w: 8.9, h: 0.4, fontSize: 15, fontFace: MONO, color: LILAC });
  logoBar(s);
}

pres.writeFile({ fileName: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/slides/helike_sab.pptx` }).then(() => console.log("ok"));
