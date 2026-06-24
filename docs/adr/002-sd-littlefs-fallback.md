# ADR-002: SD Primario com LittleFS Fallback

## Status

Aceito.

## Contexto

O flight-computer utiliza LittleFS como storage primario para logging CSV.
O satellite possui um slot para SD card (test_hardware) mas o SD nao esta
presente em voo real.

O teste `test_hardware/storage/sd_littlefs_fallback` demonstra o padrao de
tentar SD primeiro e usar LittleFS como fallback.

## Decisao

Implementar o FilesystemModule com deteccao em runtime:

1. Tenta `SD.begin(CS)` primeiro
2. Se falhar, usa `LittleFS.begin(true)` como fallback
3. Dispatch automatico de operacoes baseado no tipo ativo

Sem flag de compilacao — o modulo sempre compila e detecta o storage disponivel
em runtime.

## Consequencias

**Positivos**:
- Funciona em bancada (com SD) e em voo (sem SD)
- Sem overhead de codigo morto quando SD nao presente
- Padrao ja validado nos testes de hardware

**Negativos**:
- SD card library adiciona ~2KB de flash mesmo quando nao usado
- Complexidade de codigo vs. apenas LittleFS
