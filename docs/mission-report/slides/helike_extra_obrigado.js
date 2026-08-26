// EXTRA 3 — 06/09 (encerramento/agradecimento) — Instagram — FUNDO ESCURO
const { makePres, helpers, T, FT, MONO, A } = require("./_template_base.js");

const pres = makePres();
const { t, marker, logoBar, card, tx } = helpers(pres, "dark");
const ORANGE = T.orange, LILAC = T.lilac, DEEP = T.deep;

// S1 capa
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "OBRIGADO,", { x: 0.55, y: 2.6, w: 9, h: 1.0, fontSize: 48, bold: true, color: t.text });
  tx(s, "LASC 2026.", { x: 0.55, y: 3.6, w: 9, h: 1.0, fontSize: 48, bold: true, color: ORANGE });
  tx(s, "[foto da equipe no stand]", { x: 0.55, y: 5.2, w: 8.9, h: 0.5, fontSize: 15, fontFace: MONO, color: t.muted, align: "center" });
  logoBar(s);
}
// S2 a equipe lá
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "A EQUIPE EM PESSOA", { x: 0.55, y: 1.3, w: 9, h: 0.7, fontSize: 32, bold: true, color: t.text });
  card(s, 0.55, 2.4, 8.9, 4.9);
  s.addImage({ path: `${A}/membro_segurando_a_versao_asa2_sem_fundo.png`, x: 1.55, y: 2.7, w: 6.9, h: 4.3, sizing: { type: "contain", w: 6.9, h: 4.3 } });
  tx(s, "Do workshop da primeira asa ao lançamento: seis pessoas,\ndois anos, um cubo de 5 cm.",
     { x: 0.55, y: 7.6, w: 8.9, h: 0.9, fontSize: 17, color: t.text });
  logoBar(s);
}
// S3 agradecimentos
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "OBRIGADO A TODOS QUE", { x: 0.55, y: 1.3, w: 9, h: 0.65, fontSize: 30, bold: true, color: t.text });
  tx(s, "FEZ ISSO ACONTECER", { x: 0.55, y: 2.0, w: 9, h: 0.65, fontSize: 30, bold: true, color: ORANGE });
  const thanks = [
    ["LASC", "pela oportunidade de voo e pela organização impecável"],
    ["Alba Orbital", "pelo frame 1P que viabilizou a missão"],
    ["IPRJ-UERJ", "pelo apoio à equipe e ao laboratório"],
    ["Comunidade", "por cada comentário, compartilhamento e torcida"],
  ];
  let y = 3.0;
  thanks.forEach(([k, d]) => {
    tx(s, k, { x: 0.55, y, w: 2.6, h: 0.5, fontSize: 17, bold: true, fontFace: MONO, color: LILAC });
    tx(s, d, { x: 3.3, y, w: 5.9, h: 0.75, fontSize: 14, color: t.text });
    y += 1.0;
  });
  tx(s, "[adicionar patrocinadores/apoios quando houver]", { x: 0.55, y: y + 0.1, w: 8.9, h: 0.4, fontSize: 13, fontFace: MONO, color: t.muted });
  logoBar(s);
}
// S4 o que vem depois
{
  const s = pres.addSlide();
  marker(s);
  tx(s, "E AGORA?", { x: 0.55, y: 2.4, w: 9, h: 0.8, fontSize: 36, bold: true, color: t.text });
  tx(s, "Post-mortem técnico completo com os dados do voo.", { x: 0.55, y: 3.4, w: 9, h: 0.6, fontSize: 19, color: t.text });
  tx(s, "O SRAB continua: da validação à tecnologia de voo para futuras missões PocketQube.",
     { x: 0.55, y: 4.2, w: 9, h: 0.9, fontSize: 17, color: t.text });
  tx(s, "Acompanhe a Serra Rocketry.", { x: 0.55, y: 5.4, w: 9, h: 0.6, fontSize: 20, bold: true, color: ORANGE });
  tx(s, "github.com/ViniciusCMB/satellite", { x: 0.55, y: 6.3, w: 9, h: 0.45, fontSize: 15, fontFace: MONO, color: LILAC });
  logoBar(s);
}

pres.writeFile({ fileName: "/tmp/helike_extra_obrigado.pptx" }).then(() => console.log("ok"));
