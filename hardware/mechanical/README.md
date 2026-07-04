# Mechanical Assembly

Arquivos de modelagem 3D e montagem mecanica do satelite.

## Estrutura de pastas sugerida

```
mechanical/
├── assembly.*        (.SLDPRT, .STEP) - montagem completa
├── chassis.*         (.SLDPRT, .STEP, .STL) - corpo principal
├── plate.*           (.STEP, .STL) - PCB mounting plate
├── standoff.*        (.STEP, .STL) - separadores/roscas
├── antenna.*         (.STEP, .STL) - suporte antena
├──connector.*       (.STEP, .STL) - passagem de conector
├── README.md         (este arquivo)
```

## Convencoes

- `.SLDPRT` / `.iam` — arquivos nativos SolidWorks (part/assembly)
- `.STEP` — formato neutro para compartilhamento (AP214)
- `.STL` — para impressao 3D / visualizacao rapida
- Nome em minusculo, sem espacos, sufixo `_v2`, `_v3` para revisoes

## Como contribuir

1. Salve `.SLDPRT`/`.STEP` nativo + `.STEP` neutro + `.STL` (se impressivel)
2. Mantenha o STEP neutro sempre atualizado como fonte de verdade para corte/ CAM
3. Adicione nota aqui quando subir nova revisao
