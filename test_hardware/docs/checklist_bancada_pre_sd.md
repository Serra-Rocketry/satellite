# Checklist de Bancada (Pre-SD)

Use este checklist para validar estabilidade antes de migrar do LittleFS para modulo SD.

## 1) Preparacao

- [ ] Alimentar o ESP32-C3 com fonte estavel (cabo USB confiavel).
- [ ] Confirmar pinagem fisica usada no firmware (I2C SDA/SCL, VCC, GND).
- [ ] Abrir Serial Monitor em `115200`.
- [ ] Resetar a placa com todos os modulos conectados.
- [ ] Confirmar esquema de particao atual compativel com LittleFS.

## 2) Boot e Inicializacao (Pass/Fail imediato)

- [ ] Inicializacao sem reboot em loop.
- [ ] Sensores detectados corretamente (BMP e ICM, se habilitado).
- [ ] Sem `WHO_AM_I = 0xFF`.
- [ ] LittleFS monta sem erro.
- [ ] Arquivo CSV e cabecalho criados na primeira inicializacao.

## 3) Teste Continuo (10-15 min)

- [ ] Rodar o sistema parado por 10-15 minutos.
- [ ] Sem travamento, watchdog ou reboot espontaneo.
- [ ] Sem erros recorrentes de I2C no log serial.
- [ ] Taxa de leitura coerente com `INTERVAL`.
- [ ] Dados continuam sendo anexados ao arquivo durante todo o periodo.

## 4) Validacao dos Dados

- [ ] Temperatura em faixa plausivel de ambiente.
- [ ] Pressao em faixa plausivel local (aprox. 90k a 103k Pa, conforme altitude/clima).
- [ ] Altitude sem saltos absurdos com o sistema em repouso.
- [ ] ICM (se habilitado): aceleracao coerente com gravidade e giro proximo de zero em repouso.

## 5) Estresse Curto

- [ ] Pressionar reset 5 vezes e confirmar inicializacao correta em todas.
- [ ] Desligar/ligar alimentacao 3 vezes e confirmar recuperacao limpa.
- [ ] (Opcional) Movimentar sensor e verificar resposta coerente no log.

## 6) Criterios para Avancar ao SD

- [ ] 0 reboots inesperados no teste continuo.
- [ ] 0 falhas de montagem de FS no boot.
- [ ] 0 leituras invalidas recorrentes (`0xFF`, `NaN`, valores impossiveis).
- [ ] CSV integro (cabecalho + linhas continuas, sem corrupcao).

---

# Checklist de Migracao para SD (Proximo Passo)

## 1) Hardware e Interface

- [ ] Confirmar interface do modulo SD (SPI) e pinagem no codigo.
- [ ] Garantir compatibilidade de nivel logico em 3.3V.
- [ ] Validar alimentacao do modulo SD com margem adequada.

## 2) Cartao e Formato

- [ ] Comecar com cartao confiavel (ex.: 4-16 GB).
- [ ] Formatar em FAT32 antes dos testes.
- [ ] Testar com outro cartao se houver erro intermitente.

## 3) Teste Funcional Basico de SD

- [ ] Montar SD com sucesso no boot.
- [ ] Criar arquivo de teste.
- [ ] Escrever, ler e validar conteudo.
- [ ] Executar ciclo `open/write/flush/close` repetidamente sem erro.

## 4) Integracao com Sensores

- [ ] Registrar dados dos sensores no SD por 10-15 minutos.
- [ ] Verificar se tempo de escrita nao quebra periodicidade do loop.
- [ ] Confirmar CSV final sem linhas truncadas/corrompidas.

## 5) Criterio de Aprovacao da Migracao

- [ ] Inicializacao estavel com SD em 100% dos boots de teste.
- [ ] Sem perda de amostras relevante durante escrita.
- [ ] Sem erro recorrente de I/O no SD.
- [ ] Dados consistentes e recuperaveis apos reboot.
