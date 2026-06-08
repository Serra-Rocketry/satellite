# Equipe de Desenvolvimento - Helike PocketQube

Este documento define a estrutura da equipe de desenvolvimento e code review para a missao Helike PocketQube (Team #100), incluindo skills especializadas, agentes, e workflows.

## Visão Geral da Equipe

A equipe é composta por 5 especialistas que cobrem todas as áreas críticas do desenvolvimento de sistemas embarcados para aplicações aeroespaciais:

```
┌─────────────────────────────────────────────────────────────┐
│                    EQUIPE DE DESENVOLVIMENTO                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🏗️  Embedded Systems Architect                             │
│     └─ Arquitetura, tasks e validacao de dados              │
│                                                              │
│  💻 Firmware Developer                                       │
│     └─ Implementação C/C++, integração de sensores          │
│                                                              │
│  ✅ Code Reviewer (Safety & Quality)                         │
│     └─ Revisão de segurança, qualidade, padrões             │
│                                                              │
│  🧪 Test Engineer                                            │
│     └─ Testes unitários, HIL, simulação Python              │
│                                                              │
│  📚 Documentation Specialist                                 │
│     └─ Documentação técnica, ADRs, Doxygen                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Skills Disponíveis

### 1. Embedded Systems Architect
**Arquivo**: `.opencode/skills/embedded-architect.md`

**Quando usar**:
- Planejamento de arquitetura (tasks, estruturas de dados)
- Decisões de design (OOP vs procedural, sensor abstraction)
- Otimização de performance e memória
- Review de PRs para validação arquitetural

**Comandos típicos**:
- "Revise a arquitetura desta implementacao"
- "Como devo estruturar as tasks e periodicidade?"
- "Valide se esta implementação atende os requisitos de tempo real"

---

### 2. Firmware Developer
**Arquivo**: `.opencode/skills/firmware-developer.md`

**Quando usar**:
- Implementação de novos sensores (ISensor interface)
- Módulos de comunicação (LoRa, GPS, WiFi)
- Integração de hardware (I2C, SPI, UART)
- Resolução de bugs de firmware

**Comandos típicos**:
- "Implemente o driver para o sensor BME280"
- "Adicione suporte ao novo módulo GPS NEO-8M"
- "Corrija o bug de comunicação I2C"

---

### 3. Code Reviewer (Safety & Quality)
**Arquivo**: `.opencode/skills/code-reviewer.md`

**Quando usar**:
- Review de Pull Requests
- Análise de segurança (parachute deployment logic)
- Verificação de padrões de código
- Identificação de memory leaks e race conditions

**Comandos típicos**:
- "Revise este PR focando em safety-critical issues"
- "Analise esta implementação da lógica de paraquedas"
- "Verifique se ha race conditions neste fluxo"

---

### 4. Test Engineer
**Arquivo**: `.opencode/skills/test-engineer.md`

**Quando usar**:
- Criação de testes unitários (Unity framework)
- Testes de hardware (Arduino test firmware)
- Validação com Python simulator
- Análise de dados de voo

**Comandos típicos**:
- "Crie testes unitarios para o modulo BME280"
- "Valide os dados de bancada com scripts de analise"
- "Execute os testes de hardware para o módulo LoRa"

---

### 5. Documentation Specialist
**Arquivo**: `.opencode/skills/documentation-specialist.md`

**Quando usar**:
- Atualização de documentação (README, CHANGELOG)
- Criação de Architecture Decision Records (ADRs)
- Documentação de APIs (Doxygen)
- Diagramas e flowcharts (Mermaid)

**Comandos típicos**:
- "Atualize o README com as novas features"
- "Crie um ADR para o pipeline de telemetria"
- "Documente a API dos modulos de calculo"

---

## Workflow de Desenvolvimento

### 1. Nova Feature (Ciclo Completo)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PLANNING                                                  │
└─────────────────────────────────────────────────────────────┘
    ↓
    👤 Usuário: "Adicionar suporte ao sensor BME280"
    ↓
    🏗️ Architect:
       - Analisa impacto na arquitetura
       - Define estrutura de classes (ISensor)
       - Define budget de memória/performance
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. IMPLEMENTATION                                            │
└─────────────────────────────────────────────────────────────┘
    ↓
    💻 Firmware Developer:
       - Cria drivers de sensor conforme necessidade
       - Implementa interface de integracao
       - Adiciona validação de dados (NaN, range)
       - Implementa cálculo de velocidade vertical
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TESTING                                                   │
└─────────────────────────────────────────────────────────────┘
    ↓
    🧪 Test Engineer:
        - Cria unit tests (test/)
        - Cria hardware test (test_hardware/)
       - Valida com dados reais
       - Verifica edge cases (sensor disconnect, NaN)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. DOCUMENTATION                                             │
└─────────────────────────────────────────────────────────────┘
    ↓
    📚 Documentation Specialist:
       - Adiciona Doxygen comments
       - Atualiza README.md
       - Adiciona entrada no CHANGELOG.md
       - Cria usage example
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. CODE REVIEW                                               │
└─────────────────────────────────────────────────────────────┘
    ↓
    ✅ Code Reviewer:
       - Verifica safety issues
       - Valida padrões de código
       - Checa performance
       - Verifica documentação
    ↓
    🏗️ Architect:
       - Valida arquitetura
       - Verifica integração com sistema
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. MERGE & RELEASE                                           │
└─────────────────────────────────────────────────────────────┘
    ↓
     ✅ Aprovado → Merge para branch principal
```

---

### 2. Bug Fix (Ciclo Rapido)

```
👤 Usuário: "A telemetria LoRa parou de transmitir"
💻 Firmware Developer:
   - Diagnostica e implementa correção
    ↓
🧪 Test Engineer:
   - Valida correção com Python simulator
   - Testa com dados reais
    ↓
✅ Code Reviewer:
   - Review rápido (safety focus)
    ↓
📚 Documentation Specialist:
   - Atualiza CHANGELOG (Fixed section)
    ↓
✅ Merge e release patch
```

---

### 3. Refatoracao (Arquitetural)

```
👤 Usuário: "Refatorar loop para melhorar modularidade"
    ↓
🏗️ Architect:
   - Cria Architecture Decision Record (ADR)
   - Define task structure (FlightControl, Telemetry, Logger)
   - Especifica prioridades e core affinity
    - Documenta em docs/software.md
    ↓
👤 Aprovação do time
    ↓
💻 Firmware Developer:
   - Implementa tasks conforme necessidade
   - Adiciona queues e mutexes
   - Migra código para nova estrutura
    ↓
🧪 Test Engineer:
   - Testa timing de tasks (execution time)
   - Valida comportamento single-core
   - Testa synchronization (race conditions)
    ↓
✅ Code Reviewer:
   - Review profundo (safety + performance)
   - Verifica protecao de dados compartilhados
   - Valida constraints de tempo
    ↓
🏗️ Architect:
   - Valida implementação vs ADR
    ↓
📚 Documentation Specialist:
   - Finaliza ADR
   - Atualiza docs/software.md
   - Cria migration guide
    ↓
✅ Merge após validação completa
```

---

## Matriz de Responsabilidades (RACI)

 | Atividade | Architect | Developer | Reviewer | Tester | Doc Spec |
 |-----------|:---------:|:---------:|:--------:|:------:|:--------:|
| **Planning** |
| Definir arquitetura | **R** | C | C | I | I | I |
| Estimar recursos | **A** | C | I | I | I | I |
 | Definir thresholds de deteccao | C | **R** | I | **A** | I |
| **Implementation** |
| Escrever código | I | **R/A** | C | I | I | I |
 | Implementar deteccoes | C | **R** | I | I | I |
| Integrar sensores | C | **R/A** | I | I | I | I |
| **Testing** |
| Unit tests | I | C | I | I | **R/A** | I |
| Hardware tests | I | C | C | I | **R/A** | I |
 | Validacao de deteccoes | C | I | I | **R** | I |
| **Review** |
| Code review | **A** | I | I | **R** | C | I |
| Safety review | **A** | I | C | **R** | I | I |
| Architecture review | **R/A** | I | I | C | I | I |
| **Documentation** |
 | Doxygen comments | I | **R** | C | I | **A** |
| README/CHANGELOG | C | I | I | I | I | **R/A** |
| ADRs | **A** | I | I | I | I | **R** |

**Legenda**:
- **R** = Responsible (executa)
- **A** = Accountable (responsável final)
- **C** = Consulted (consultado)
- **I** = Informed (informado)

---

## Comandos por Tipo de Tarefa

### Implementar Nova Feature
```bash
# 1. Planning
"@embedded-architect Analise o impacto de adicionar o sensor BME280 na arquitetura atual"

# 2. Implementation
"@firmware-developer Implemente o driver BME280 seguindo a interface ISensor"

# 3. Testing
"@test-engineer Crie testes unitarios e de hardware para o BME280"

# 4. Documentation
"@documentation-specialist Documente o BME280 com Doxygen e atualize o README"

# 5. Review
"@code-reviewer Revise a implementacao do BME280 focando em safety e qualidade"
```

### Resolver Bug
```bash
# 1. Diagnóstico
"@firmware-developer Diagnostique por que a telemetria LoRa não transmite"

# 2. Correção
"@firmware-developer Corrija a rotina de transmissao LoRa"

# 3. Validação
"@test-engineer Valide a correção usando o simulador Python e dados reais"

# 4. Review
"@code-reviewer Revise a correção rapidamente, foco em safety"

# 5. Doc
"@documentation-specialist Atualize o CHANGELOG com o bug fix"
```

### Code Review de PR
```bash
# Review multi-especialista
"@code-reviewer Revise o PR #42 focando em safety-critical issues"
"@embedded-architect Valide se o PR #42 segue a arquitetura definida"
"@test-engineer Verifique se o PR #42 inclui testes adequados"
"@documentation-specialist Verifique se o PR #42 tem documentação completa"
```

---

## Processo de Code Review

### Checklist de Review (Multi-camada)

#### Camada 1: Automated Checks (CI/CD - Futuro)
```bash
✓ Build passa (pio run)
✓ Unit tests passam (pio test -e native)
✓ Linting OK (clang-tidy, cppcheck)
✓ Documentação gerada (doxygen)
```

#### Camada 2: Code Reviewer (Safety & Quality)
```
✅ Functional Correctness
   ✓ Implementa requisitos
   ✓ Edge cases tratados
   ✓ Validação de inputs
   
✅ Safety (Critical)
   ✓ Sem buffer overflows
   ✓ Sem null pointer dereferences
   ✓ Validação de dados de sensores (NaN)
   ✓ Lógica de paraquedas segura
   
✅ Code Quality
   ✓ Segue naming conventions
   ✓ Doxygen comments presentes
   ✓ Sem magic numbers
   
✅ Performance
   ✓ Sem dynamic allocation em critical paths
   ✓ Tasks atendem timing requirements
```

#### Camada 3: Architect (Architecture Compliance)
```
✅ Architecture
   ✓ Segue ISensor interface (se aplicável)
   ✓ Task priorities corretas
   ✓ Mutexes usados corretamente
   ✓ Memory budget respeitado
   
✅ Integration
   ✓ Integra com módulos existentes
   ✓ Não quebra APIs públicas
```

#### Camada 4: Test Engineer
```
✅ Testing
   ✓ Unit tests presentes (>80% coverage)
   ✓ Hardware test procedure documentado
    ✓ Validado com dados reais de bancada
```

#### Camada 5: Documentation Specialist
```
✅ Documentation
   ✓ Doxygen comments completos
   ✓ CHANGELOG.md atualizado
   ✓ README atualizado (se necessário)
   ✓ Usage examples fornecidos
```

### Severidades de Issues

#### 🔴 Critical (Blocking)
- Safety issues (parachute deployment)
- Memory corruption
- Race conditions
- Real-time violations

**Ação**: Block merge

#### 🟠 Major (Should Fix)
- Missing error handling
- Resource leaks
- Performance issues (>20% over budget)

**Ação**: Request changes

#### 🟡 Minor (Nice to Have)
- Code style
- Missing docs
- Refactoring suggestions

**Ação**: Approve with comments

---

## Como Usar Este Sistema

### Para Usuários/Desenvolvedores

#### 1. Ao Iniciar uma Nova Feature
```
Você: "Quero adicionar suporte ao sensor BME280"

OpenCode irá:
1. Invocar @embedded-architect para análise de arquitetura
2. Invocar @firmware-developer para implementação
3. Invocar @test-engineer para testes
4. Invocar @documentation-specialist para docs
5. Invocar @code-reviewer para review final
```

#### 2. Ao Encontrar um Bug
```
Você: "A telemetria LoRa parou de transmitir"

OpenCode irá:
1. Invocar @firmware-developer para diagnóstico e correção
2. Invocar @test-engineer para validação
3. Invocar @code-reviewer para review rápido
```

#### 3. Ao Fazer um Pull Request
```
Você: "Revise meu PR que adiciona o sensor BME280"

OpenCode irá:
1. Invocar @code-reviewer para safety/quality review
2. Invocar @embedded-architect para architecture review
3. Invocar @test-engineer para test coverage review
4. Invocar @documentation-specialist para doc review
5. Gerar relatório consolidado de review
```

---

## Referências

### Arquivos de Skills
- `.opencode/skills/embedded-architect.md`
- `.opencode/skills/firmware-developer.md`
- `.opencode/skills/code-reviewer.md`
- `.opencode/skills/test-engineer.md`
- `.opencode/skills/documentation-specialist.md`

### Documentação do Projeto
- `docs/software.md` - Arquitetura de software
- `CONTRIBUTING.md` - Guia de contribuição
- `docs/software.md` - Arquitetura de software
- `docs/hardware.md` - Especificações de hardware

### Padrões e Guidelines
- NASA C Coding Standard (referência para safety-critical)
- MISRA C Guidelines (automotive, aplicável a aerospace)
- Keep a Changelog (formato de CHANGELOG.md)
- Semantic Versioning (versionamento)

---

## Próximos Passos

### Implementação das Skills no OpenCode
As skills foram criadas como arquivos markdown em `.opencode/skills/`. Para ativá-las:

1. **Opção 1**: Integração futura do OpenCode com skills markdown
2. **Opção 2**: Converter para formato de agentes especializados
3. **Opção 3**: Usar como referência em prompts customizados

### Automação (Futuro)
- GitHub Actions para CI/CD
- Pre-commit hooks para linting
- Automated testing em PRs
- Automated documentation generation

---

**Versao**: 1.0  
**Data**: 2026-04-01  
**Autor**: Serra Rocketry Team
**Status**: Active
