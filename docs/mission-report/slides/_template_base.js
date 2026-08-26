// ============================================================
// TEMPLATE BASE — Carrosséis Helike #213 (PptxGenJS)
// Formato 10x12.5in (1080x1350, 4:5 IG). Identidade mission patch.
// Uso: node <script.js>  (requer npm install pptxgenjs no diretório)
// Conversão PDF: /tmp/squashfs-root/opt/libreoffice25.8/program/soffice
//   --headless --convert-to pdf --outdir /tmp arquivo.pptx
// ============================================================
const pptxgen = require("pptxgenjs");
const A = "/home/vinicius/Documentos/projects/satellite/docs/mission-report/assets";

// ---------- tema ----------
const T = {
  dark:  { bg: "1B1528", card: "151020", card2: "1D1430", grid: "2E2545",
           text: "FFFFFF", muted: "8A85A0", logo: "LOGO 2026 - BRANCA.png" },
  light: { bg: "F2F2F2", card: "E8E4F0", card2: "DED8EC", grid: "C9C2DC",
           text: "2D1959", muted: "6B6580", logo: "LOGO 2026 - PRETA.png" },
  orange: "F28749", lilac: "907ABF", deep: "2D1959", brown: "8C4F2B",
  white: "FFFFFF",
};

const FT = "Space Grotesk", MONO = "JetBrains Mono";
const W = 10, H = 12.5;

function makePres() {
  const pres = new pptxgen();
  pres.defineLayout({ name: "P45", width: W, height: H });
  pres.layout = "P45";
  return pres;
}

// factory: helpers presos ao tema ativo
function helpers(pres, theme) {
  const t = T[theme];

  const addGrid = (s) => {
    for (let gx = 1.25; gx < W; gx += 1.25)
      s.addShape(pres.ShapeType.rect, { x: gx, y: 0, w: 0.02, h: H, fill: { color: t.grid } });
    for (let gy = 1.25; gy < H; gy += 1.25)
      s.addShape(pres.ShapeType.rect, { x: 0, y: gy, w: W, h: 0.02, fill: { color: t.grid } });
  };

  const marker = (s) => {
    s.background = { color: t.bg };
    addGrid(s);
    s.addText("MISSÃO HELIKE - #213", { x: 0.55, y: 0.4, w: 5, h: 0.4, fontSize: 13, fontFace: MONO, color: t.muted });
    s.addShape(pres.ShapeType.rect, { x: 0.57, y: 0.92, w: 1.0, h: 0.04, fill: { color: T.orange } });
  };

  const logoBar = (s) => {
    const y = 11.15, h = 1.15;
    s.addShape(pres.ShapeType.rect, { x: 0, y, w: W, h: 0.04, fill: { color: T.deep } });
    s.addImage({ path: `${A}/${t.logo}`, x: 0.55, y: y + 0.15, w: h, h: h });
    s.addImage({ path: `${A}/mission_patch.png`, x: 4.62, y: y + 0.15, w: h, h: h });
    s.addImage({ path: `${A}/logo_lasc.png`, x: 8.72, y: y + 0.15, w: h * 0.91, h });
  };

  const card = (s, x, y, w, h, opts = {}) => {
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w, h, rectRadius: 0.1,
      fill: { color: opts.fill || t.card },
      line: opts.edge ? { color: opts.edge, width: 2 } : { color: opts.fill || t.card, width: 0 },
    });
  };

  const tx = (s, text, o) => s.addText(text, { fontFace: FT, ...o });

  return { t, addGrid, marker, logoBar, card, tx };
}

module.exports = { makePres, helpers, T, FT, MONO, A };
