// Carrossel Dia 1 — Helike #213 — PptxGenJS (elementos nativos editáveis)
// Identidade: paleta do mission patch + Space Grotesk/JetBrains Mono + barra de logos
const pptxgen = require("pptxgenjs");
const A = "/home/vinicius/Documentos/projects/satellite/docs/mission-report/assets";

const pres = new pptxgen();
pres.defineLayout({ name: "P45", width: 10, height: 12.5 });
pres.layout = "P45";

// paleta (mission patch)
const BG = "1B1528", CARD = "151020", CARD2 = "1D1430";
const ORANGE = "F28749", LILAC = "907ABF", DEEP = "2D1959", BROWN = "8C4F2B";
const WHITE = "FFFFFF", GRAY = "8A85A0";
const FT = "Space Grotesk", MONO = "JetBrains Mono";

const GRID = "2E2545";
const addGrid = (s) => {
  for (let gx = 1.25; gx < 10; gx += 1.25)
    s.addShape(pres.ShapeType.rect, { x: gx, y: 0, w: 0.02, h: 10, fill: { color: GRID } });
  for (let gy = 1.25; gy < 10; gy += 1.25)
    s.addShape(pres.ShapeType.rect, { x: 0, y: gy, w: 10, h: 0.02, fill: { color: GRID } });
};

const marker = (s, n) => {
  s.background = { color: BG };
  addGrid(s);
  s.addText("MISSÃO HELIKE - #213", { x: 0.55, y: 0.4, w: 5, h: 0.4, fontSize: 13, fontFace: MONO, color: GRAY });
  s.addShape(pres.ShapeType.rect, { x: 0.57, y: 0.92, w: 1.0, h: 0.04, fill: { color: ORANGE } });
};

const logoBar = (s) => {
  s.addShape(pres.ShapeType.rect, { x: 0, y: 11.15, w: 10, h: 0.04, fill: { color: DEEP } });
  s.addImage({ path: `${A}/LOGO 2026 - BRANCA.png`, x: 0.55, y: 11.3, w: 1.15, h: 1.15 });
  s.addImage({ path: `${A}/mission_patch.png`, x: 4.42, y: 11.3, w: 1.15, h: 1.15 });
  s.addImage({ path: `${A}/logo_lasc.png`, x: 8.72, y: 11.3, w: 1.05, h: 1.15 });
};

const card = (s, x, y, w, h, opts = {}) => {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: opts.fill || CARD },
    line: opts.edge ? { color: opts.edge, width: 2 } : { color: opts.fill || CARD, width: 0 },
  });
};

// ============ SLIDE 1 — CAPA ============
{
  const s = pres.addSlide();
  marker(s, 1);
  card(s, 5.15, 1.9, 4.55, 3.65, { fill: BG, edge: DEEP });
  s.addImage({ path: `${A}/vista_isometrica_helike_asa3.png`, x: 5.3, y: 2.08, w: 4.25, h: 2.93 });
  s.addText([
    { text: "E SE A", options: { color: WHITE, breakLine: true } },
    { text: "RECUPERAÇÃO", options: { color: WHITE, breakLine: true } },
    { text: "NÃO TIVESSE", options: { color: WHITE, breakLine: true } },
    { text: "COMO FALHAR?", options: { color: LILAC } },
  ], { x: 0.55, y: 2.6, w: 4.7, h: 3.6, fontSize: 44, bold: true, fontFace: FT, lineSpacing: 52, shrinkText: true });
  s.addText([
    { text: "SEM SERVO.", options: { color: WHITE, breakLine: true } },
    { text: "SEM PIROTECNIA.", options: { color: WHITE, breakLine: true } },
    { text: "SEM SOFTWARE DECIDINDO NADA.", options: { color: LILAC } },
  ], { x: 0.55, y: 7.2, w: 4.8, h: 1.7, fontSize: 20, bold: true, fontFace: FT, lineSpacing: 28 });
  // raio heroicon-like (desenho nativo: bolt aproximado com chevron)
  logoBar(s);
}

// ============ SLIDE 2 — O PROBLEMA ============
{
  const s = pres.addSlide();
  marker(s, 2);
  s.addText([
    { text: "TODO RECOVERY É UMA ", options: { color: WHITE } },
    { text: "CADEIA", options: { color: ORANGE } },
  ], { x: 1.2, y: 1.25, w: 8.5, h: 0.7, fontSize: 33, bold: true, fontFace: FT });
  const links = [
    ["01", "SENSOR", "decide quando abrir"],
    ["02", "ATUADOR", "servo ou pirotecnia dispara"],
    ["03", "ENERGIA", "precisa estar lá na hora exata"],
    ["04", "PARAQUEDAS", "precisa inflar"],
  ];
  let x = 0.55;
  links.forEach(([n, t, d], i) => {
    card(s, x, 3.4, 2.05, 3.1, i === 3 ? { edge: DEEP } : {});
    s.addText(n, { x: x + 0.15, y: 3.6, w: 1.7, h: 0.4, fontSize: 16, bold: true, fontFace: MONO, color: LILAC });
    s.addText(t, { x: x + 0.15, y: 4.15, w: 1.75, h: 0.5, fontSize: 18, bold: true, fontFace: FT, color: WHITE });
    s.addText(d, { x: x + 0.15, y: 4.9, w: 1.75, h: 1.4, fontSize: 14, fontFace: FT, color: GRAY, shrinkText: true });
    if (i < 3) s.addText("→", { x: x + 2.02, y: 4.55, w: 0.28, h: 0.5, fontSize: 22, bold: true, color: ORANGE, fontFace: FT, align: "center" });
    x += 2.3;
  });
  s.addText([
    { text: "QUEBROU UM ELO, ", options: { color: WHITE } },
  ], { x: 0.55, y: 7.6, w: 8.9, h: 0.6, fontSize: 27, bold: true, fontFace: FT });
  s.addText("PERDEU O SATÉLITE.", { x: 0.55, y: 8.3, w: 8.9, h: 0.6, fontSize: 27, bold: true, fontFace: FT, color: ORANGE });
  s.addText("Cada elo tem sua chance de falha. E elas se multiplicam:\nun mecanismo único carrega os quatro modos de falha de uma vez.",
    { x: 0.55, y: 9.3, w: 8.6, h: 0.9, fontSize: 16, fontFace: FT, color: GRAY });
  logoBar(s);
}

// ============ SLIDE 3 — CONTEXTO ============
{
  const s = pres.addSlide();
  marker(s, 3);
  s.addText("O QUE APRENDEMOS COM A", { x: 1.2, y: 1.4, w: 8.5, h: 0.65, fontSize: 36, bold: true, fontFace: FT, color: WHITE });
  s.addText("LASC 2025?", { x: 1.2, y: 2.15, w: 8.5, h: 0.65, fontSize: 36, bold: true, fontFace: FT, color: ORANGE });
  card(s, 0.55, 3.9, 4.5, 2.9);
  s.addText("APOGEU ATINGIDO.", { x: 0.85, y: 4.1, w: 3.9, h: 0.45, fontSize: 20, bold: true, fontFace: FT, color: LILAC });
  s.addText("Comunicação perdida no voo.\nO paraquedas não abriu.\nO voo terminou balístico.",
    { x: 0.85, y: 4.75, w: 3.9, h: 1.8, fontSize: 16, fontFace: FT, color: WHITE, lineSpacing: 22 });
  card(s, 5.35, 3.9, 4.5, 2.9);
  s.addText("NEM DÁ PRA SABER\nO QUE FALHOU.", { x: 5.65, y: 4.1, w: 3.9, h: 0.9, fontSize: 20, bold: true, fontFace: FT, color: LILAC });
  s.addText("Sem telemetria suficiente,\nmecânica ou eletrônica?\nImpossível distinguir.",
    { x: 5.65, y: 4.75, w: 3.9, h: 1.5, fontSize: 16, fontFace: FT, color: WHITE, lineSpacing: 22 });
  s.addText("SR Couto #100 + SR Coutinho #261 · zero redundância",
    { x: 0.55, y: 7.4, w: 8.9, h: 0.4, fontSize: 16, fontFace: MONO, color: GRAY });
  logoBar(s);
}

// ============ SLIDE 4 — A RESPOSTA ============
{
  const s = pres.addSlide();
  marker(s, 4);
  s.addText("O SRAB NÃO MELHORA A CADEIA.", { x: 0.55, y: 1.3, w: 9, h: 0.6, fontSize: 31, bold: true, fontFace: FT, color: WHITE });
  s.addText("ELE A ELIMINA.", { x: 0.55, y: 2.0, w: 9, h: 0.6, fontSize: 31, bold: true, fontFace: FT, color: ORANGE });
  // coluna paraquedas
  card(s, 0.55, 3.6, 4.5, 4.1);
  s.addText("× PARAQUEDAS", { x: 0.85, y: 3.8, w: 4.0, h: 0.45, fontSize: 19, bold: true, fontFace: FT, color: GRAY });
  s.addText([
    { text: "· sequenciador decide", options: { breakLine: true } },
    { text: "· atuador dispara", options: { breakLine: true } },
    { text: "· energia disponível", options: { breakLine: true } },
    { text: "· tecido infla", options: {} },
  ], { x: 0.85, y: 4.45, w: 3.9, h: 2.2, fontSize: 16, fontFace: FT, color: GRAY, lineSpacing: 26 });
  s.addText("4 modos de falha em série", { x: 0.85, y: 6.8, w: 3.9, h: 0.4, fontSize: 16, bold: true, fontFace: FT, color: GRAY });
  // coluna SRAB
  card(s, 5.35, 3.6, 4.5, 4.1, { fill: CARD2, edge: DEEP });
  s.addText("SRAB", { x: 5.65, y: 3.8, w: 4.0, h: 0.45, fontSize: 19, bold: true, fontFace: FT, color: LILAC });
  s.addText([
    { text: "· sem sequenciador", options: { breakLine: true } },
    { text: "· sem atuador", options: { breakLine: true } },
    { text: "· asas abrem por física na ejeção", options: { breakLine: true } },
    { text: "· recuperação é aerodinâmica", options: {} },
  ], { x: 5.65, y: 4.45, w: 3.9, h: 2.2, fontSize: 16, fontFace: FT, color: WHITE, lineSpacing: 26 });
  s.addText("zero atuadores · zero mecanismo", { x: 5.65, y: 6.8, w: 3.9, h: 0.4, fontSize: 16, bold: true, fontFace: FT, color: LILAC });
  s.addText('A classe de falha "deployment" sai do projeto inteira.',
    { x: 0.55, y: 8.6, w: 9, h: 0.5, fontSize: 20, bold: true, fontFace: FT, color: WHITE });
  logoBar(s);
}

// ============ SLIDE 5 — AGENDA ============
{
  const s = pres.addSlide();
  marker(s, 5);
  s.addText("ESTA SEMANA:", { x: 1.2, y: 1.4, w: 8.5, h: 0.6, fontSize: 32, bold: true, fontFace: FT, color: WHITE });
  s.addText("COMO A GENTE CONSTRUIU ISSO", { x: 1.2, y: 2.1, w: 8.5, h: 0.6, fontSize: 32, bold: true, fontFace: FT, color: LILAC });
  const agenda = [
    ["TER", "o formato 1P · 50×50×50 mm"],
    ["QUA", "a física da autorrotação"],
    ["QUI", "da semente ao código"],
    ["SEX", "o time"],
    ["SÁB", "os números da validação"],
    ["DOM", "countdown do lançamento"],
  ];
  let y = 3.7;
  agenda.forEach(([d, t]) => {
    card(s, 0.55, y, 1.05, 0.72, { fill: CARD2 });
    s.addText(d, { x: 0.55, y: y + 0.16, w: 1.05, h: 0.4, fontSize: 17, bold: true, fontFace: MONO, color: LILAC, align: "center" });
    s.addText(t, { x: 1.95, y: y + 0.16, w: 7.5, h: 0.4, fontSize: 19, fontFace: FT, color: WHITE });
    y += 0.92;
  });
  logoBar(s);
}

// ============ SLIDE 6 — CTA ============
{
  const s = pres.addSlide();
  marker(s, 6);
  s.addText("SIGA PARA ACOMPANHAR", { x: 0.55, y: 1.8, w: 9, h: 0.65, fontSize: 36, bold: true, fontFace: FT, color: WHITE });
  s.addText("CADA PASSO.", { x: 0.55, y: 2.65, w: 9, h: 0.65, fontSize: 36, bold: true, fontFace: FT, color: ORANGE });
  s.addText("↓", { x: 4.7, y: 3.9, w: 0.6, h: 0.7, fontSize: 40, bold: true, color: LILAC, fontFace: FT, align: "center" });
  // QR centralizado
  s.addImage({ path: `${A}/qr_code_link_repositorio.png`, x: 4.15, y: 5.0, w: 1.7, h: 1.7 });
  s.addText("aponte a câmera", { x: 3.0, y: 6.95, w: 4, h: 0.35, fontSize: 14, fontFace: MONO, color: GRAY, align: "center" });
  s.addText("github.com/ViniciusCMB/satellite", { x: 2.5, y: 7.45, w: 5, h: 0.4, fontSize: 17, bold: true, fontFace: MONO, color: LILAC, align: "center" });
  // patch + lasc
  s.addImage({ path: `${A}/mission_patch.png`, x: 2.3, y: 8.6, w: 1.4, h: 1.4 });
  s.addImage({ path: `${A}/logo_lasc.png`, x: 6.3, y: 8.6, w: 1.28, h: 1.4 });
  s.addText("LASC 2026 · SERRA ROCKETRY", { x: 3.0, y: 10.35, w: 4, h: 0.35, fontSize: 13, bold: true, fontFace: MONO, color: GRAY, align: "center" });
}

pres.writeFile({ fileName: `/home/vinicius/Documentos/projects/satellite/docs/mission-report/slides/helike_dia1.pptx` }).then(() => console.log("ok"));
