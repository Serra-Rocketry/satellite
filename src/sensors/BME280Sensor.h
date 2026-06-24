/**
 * @file BME280Sensor.h
 * @brief Driver para sensor BME280 (temperatura, pressao, umidade)
 *
 * Comunicacao I2C. Fornece leituras de temperatura (C), pressao (Pa),
 * umidade (%) e altitude (m) calculada via formula barometrica.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef BME280_SENSOR_H
#define BME280_SENSOR_H

#include <Arduino.h>
#include <Adafruit_BME280.h>
#include "config.h"
#include "ISensor.h"

/**
 * @class BME280Sensor
 * @brief Abstracao para o sensor barometrico BME280
 */
class BME280Sensor : public ISensor {
public:
    /**
     * @brief Construtor
     * @param seaLevelPressure Pressao ao nivel do mar (hPa)
     */
    BME280Sensor(float seaLevelPressure = BME280_SEALEVEL_HPA);

    ///@name ISensor interface
    ///@{
    /**
     * @brief Retorna o estado atual de inicializacao
     *
     * Este overload de begin() nao inicializa o sensor fisicamente.
     * Apenas retorna o flag _ready, que e definido como true apos
     * a chamada explicita de begin(TwoWire&, uint8_t).
     *
     * @return true se o sensor ja foi inicializado via begin(TwoWire&, uint8_t)
     */
    bool begin() override { return _ready; }
    void update() override {}
    bool isReady() const override { return _ready; }
    bool hasNewData() const override { return _hasNewData; }
    void markDataRead() override { _hasNewData = false; }
    ///@}

    /**
     * @brief Inicializa o sensor I2C
     * @param wire Barramento I2C
     * @param addr Endereco I2C do sensor (0x76 ou 0x77)
     * @return true se inicializado com sucesso
     */
    bool begin(TwoWire &wire, uint8_t addr = BME280_ADDR);

    /**
     * @brief Le temperatura em Celsius
     * @return Temperatura ou NAN se erro
     */
    float getTemperature();

    /**
     * @brief Le pressao em Pa
     * @return Pressao ou NAN se erro
     */
    float getPressure();

    /**
     * @brief Le umidade em %
     * @return Umidade ou NAN se erro
     */
    float getHumidity();

    /**
     * @brief Calcula altitude em metros (relativa ao sea level)
     * @return Altitude ou NAN se erro
     */
    float getAltitude();

    /**
     * @brief Define pressao de referencia para altitude
     * @param pressure Pressao em hPa
     */
    void setSeaLevelPressure(float pressure);

    /**
     * @brief Retorna pressao de referencia (hPa)
     */
    float getSeaLevelPressure();

private:
    Adafruit_BME280 _bme;
    bool _ready;
    bool _hasNewData;
    float _seaLevelPressure;
};

#endif // BME280_SENSOR_H
