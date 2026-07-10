// presets.mjs — pack de presets de trilha (estética hacker / cyberpunk / Mr. Robot).
// É um módulo .mjs (NÃO .json) de propósito: o navegador de workflows do ComfyUI trata todo
// arquivo .json da pasta como um grafo e tenta abri-lo — um .json de config abriria a tela VAZIA.
// Edite à vontade: 'tags' é o estilo (vale para fal E replicate). instrumental=true força faixa sem vocal.
// Para faixas COM vocal: instrumental=false e preencha 'lyrics' com [verse]/[chorus].
export default {
  defaults: {
    instrumental: true,
    duration: 60,
    lyrics: "[instrumental]",
  },
  presets: [
    { id: "menu",        nome: "Menu / exploracao furtiva de terminal", bpm: 80,  tags: "dark ambient, mysterious, deep drones, suspenseful, enigmatic textures, shadowy, slow-moving, 80 BPM" },
    { id: "tensao",      nome: "Tensao / invasao ativa",                bpm: 90,  tags: "trip-hop, mysterious, muted beats, noir atmosphere, shadowy bass, cinematic, late-night, 90 BPM" },
    { id: "perseguicao", nome: "Fuga / perseguicao",                    bpm: 135, tags: "industrial techno instrumental, aggressive, distorted synthesizers, heavy pulsating bass, analog arpeggios, 135 BPM, underground electronic" },
    { id: "ambiente",    nome: "Leito ambiente continuo (background)",  bpm: 70,  tags: "cyberpunk ambient, glassy synth pads, subtle glitch, rain-soaked neon, minimal, hypnotic, 70 BPM" },
    { id: "confronto",   nome: "Confronto / quebra de firewall",        bpm: 120, tags: "dark synthwave, driving analog arpeggios, ominous, pulsing bass, retro-futuristic, tense, 120 BPM" },
  ],
};
