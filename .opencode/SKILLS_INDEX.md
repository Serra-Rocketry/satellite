---
title: OpenCode Skills Index
date: 2026-04-06
status: active
---

# OpenCode Skills Index

Este arquivo lista todas as skills disponíveis no projeto Satellite e fornece acesso rápido à documentação.

## Skills Disponíveis

### 🏗️ Embedded Systems Architect
- **Caminho**: `.opencode/skills/embedded-architect/SKILL.md`
- **Especialidade**: Arquitetura embarcada, organizacao de tasks, otimizacao de performance
- **Use quando**: Planejar arquitetura, validar design, otimizar recursos
- **Responsabilidades**: Design de arquitetura, revisao tecnica, validacao de performance

**Arquivo**: [embedded-architect/SKILL.md](./skills/embedded-architect/SKILL.md)

---

### 💻 Firmware Developer
- **Caminho**: `.opencode/skills/firmware-developer/SKILL.md`
- **Especialidade**: C/C++ embarcado, integração de sensores, protocolos I2C/SPI/UART
- **Use quando**: Implementar drivers, adicionar módulos, corrigir bugs
- **Responsabilidades**: Desenvolvimento de código, integração de sensores, testes unitários

**Arquivo**: [firmware-developer/SKILL.md](./skills/firmware-developer/SKILL.md)

---

### ✅ Code Reviewer (Safety & Quality)
- **Caminho**: `.opencode/skills/code-reviewer/SKILL.md`
- **Especialidade**: Código safety-critical, análise estática, padrões de qualidade
- **Use quando**: Revisar PRs, verificar lógica de segurança, validar padrões
- **Responsabilidades**: Code review, validação de segurança, garantia de qualidade

**Arquivo**: [code-reviewer/SKILL.md](./skills/code-reviewer/SKILL.md)

---

### 🧪 Test Engineer
- **Caminho**: `.opencode/skills/test-engineer/SKILL.md`
- **Especialidade**: Unit tests, testes de hardware, simulacao Python, analise de dados
- **Use quando**: Criar testes, validar com simulator, testar hardware
- **Responsabilidades**: Planejamento de testes, validacao, analise de dados

**Arquivo**: [test-engineer/SKILL.md](./skills/test-engineer/SKILL.md)

---

### 📚 Documentation Specialist
- **Caminho**: `.opencode/skills/documentation-specialist/SKILL.md`
- **Especialidade**: Doxygen, ADRs, diagramas, documentação técnica
- **Use quando**: Atualizar docs, criar ADRs, documentar APIs
- **Responsabilidades**: Documentação técnica, ADRs, manutenção de docs

**Arquivo**: [documentation-specialist/SKILL.md](./skills/documentation-specialist/SKILL.md)

---

## Estrutura do Projeto

```
satellite/
├── AGENTS.md                    # Guia para agentes de IA (comandos build, code style)
├── CONTRIBUTING.md              # Padrões de código e processo de PR
├── .opencode/                   # OpenCode configuration
│   ├── README.md               # Visão geral de skills e workflows
│   ├── TEAM.md                 # Estrutura de equipe e matriz RACI
│   ├── opencode.yaml           # Configuração de skills (THIS FILE)
│   ├── SKILLS_INDEX.md         # Índice de skills (YOU ARE HERE)
│   └── skills/                 # Diretórios de skills
│       ├── embedded-architect/
│       │   └── SKILL.md
│       ├── firmware-developer/
│       │   └── SKILL.md
│       ├── code-reviewer/
│       │   └── SKILL.md
│       ├── test-engineer/
│       │   └── SKILL.md
│       └── documentation-specialist/
│           └── SKILL.md
├── firmware/
│   └── ...firmware sources
├── docs/
│   ├── software.md             # Arquitetura de software
│   ├── hardware.md             # Especificações de hardware
│   └── flowchart.md            # Fluxos operacionais
├── extras/
│   ├── wing-analysis/          # Estudos de asa e simulacao
│   └── ...
├── test_hardware/
│   ├── docs/                   # Guias e checklists de bancada
│   ├── sensor/                 # Sketches de sensores
│   └── integration/            # Sketches integrados
└── test/
    └── ...
```

## Workflow Rápido

### Para Implementar uma Nova Feature

1. **Consulte o Architect** (embedded-architect/SKILL.md)
   - Revisar `docs/software.md` para entender a arquitetura
   - Validar design da feature

2. **Implemente com o Developer** (firmware-developer/SKILL.md)
   - Seguir padrões de código em `AGENTS.md`
   - Implementar código seguindo guidelines

3. **Crie Testes com Test Engineer** (test-engineer/SKILL.md)
   - Unit tests com >80% cobertura
   - Validar com simulator Python
   - Testar em hardware

4. **Documente com Doc Specialist** (documentation-specialist/SKILL.md)
   - Adicionar Doxygen comments
   - Atualizar documentação
   - Criar ADR se necessário

5. **Revise com Code Reviewer** (code-reviewer/SKILL.md)
   - Safety-critical code review
   - Validação de padrões
   - Verificação de qualidade

6. **Final Review com Architect**
   - Validação final de arquitetura
   - Aprovação de merge

## Como Acessar uma Skill

### Via OpenCode (Recomendado)
```
"Quero adicionar suporte ao sensor BME280"
→ OpenCode carrega automaticamente as skills relevantes
```

### Manual
```
1. Abra o arquivo `.opencode/skills/[nome-skill]/SKILL.md`
2. Siga as responsabilidades e guidelines
3. Consulte o projeto context específico
```

## Atualizar Informações

Se precisar:
- **Adicionar uma nova skill**: Crie diretório em `.opencode/skills/nova-skill/` com `SKILL.md`
- **Atualizar skill existente**: Edite `.opencode/skills/[skill]/SKILL.md`
- **Atualizar este índice**: Edite este arquivo (`SKILLS_INDEX.md`)
- **Atualizar configuração OpenCode**: Edite `.opencode/opencode.yaml`

## Referências Externas

- [NASA C Coding Standard](https://ntrs.nasa.gov/citations/20080039927)
- [MISRA C Guidelines](https://www.misra.org.uk/)
- [Adafruit Sensor Libraries](https://github.com/adafruit)
- [Arduino Framework Documentation](https://www.arduino.cc/reference/)
- [ESP32 Documentation](https://docs.espressif.com/)

---

**Status**: ✅ Active  
**Última atualização**: 2026-04-06  
**Versão**: 1.0
