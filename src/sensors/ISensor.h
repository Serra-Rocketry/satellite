/**
 * @file ISensor.h
 * @brief Interface abstrata comum para todos os sensores
 *
 * Define o contrato minimo que todo sensor deve implementar:
 * iniciacao, atualizacao periodica, e sinalizacao de dados novos.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef ISENSOR_H
#define ISENSOR_H

#include <Arduino.h>

/**
 * @class ISensor
 * @brief Interface abstrata para sensores do satellite
 */
class ISensor {
public:
    virtual ~ISensor() {}

    /**
     * @brief Inicializa o sensor
     * @return true se inicializado com sucesso
     */
    virtual bool begin() = 0;

    /**
     * @brief Atualiza leituras do sensor
     * @note Chamar periodicamente no loop principal
     */
    virtual void update() = 0;

    /**
     * @brief Verifica se sensor esta operacional
     */
    virtual bool isReady() const = 0;

    /**
     * @brief Verifica se ha dados novos desde a ultima leitura
     */
    virtual bool hasNewData() const = 0;

    /**
     * @brief Marca que os dados foram lidos/consumidos
     */
    virtual void markDataRead() = 0;
};

#endif // ISENSOR_H
