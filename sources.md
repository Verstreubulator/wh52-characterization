# Sources

## Manufacturer material

Ecowitt. (n.d.). *WH52 soil sensor*. https://www.ecowitt.com/shop/goodsDetail/371

Ecowitt. (2025). *WH51 soil moisture sensor manual*.
https://oss.ecowitt.net/uploads/20251226/WH51Manual.pdf

Federal Communications Commission. (n.d.). *FCC ID WA5WH51, Fine Offset
Electronics soil moisture sensor*. https://fccid.io/WA5WH51
Internal photographs are published. The schematic and block diagram are marked
confidential and are not available. No filing for the WH52 was located.

## Commodity module documentation

Seeed Technology. (2020). *Soil moisture, temperature and EC sensor user manual,
S-Temp&VWC&EC-02*.
https://files.seeedstudio.com/wiki/Soil_Moisture_Temperature_EC_Sensor/SoilMoisture_Temperature_ECSensorUserManual-S-Temp&VWC&EC-02.pdf
Source of the register map, the −40 to +80 °C range, the 0 to 10,000 µS/cm
conductivity range, and the 2 percent per degree conductivity temperature
coefficient discussed in [hardware.md](hardware.md).

DFRobot. (n.d.). *RS485 soil temperature, moisture and EC sensor, SEN0601*.
https://wiki.dfrobot.com/sen0601/
Publishes accuracy in two bands, ±3 percent to 10,000 µS/cm and ±5 percent from
10,000 to 20,000, which supports the presence of internal range switching.

## Soil physics

Topp, G. C., Davis, J. L., & Annan, A. P. (1980). Electromagnetic determination of
soil water content: Measurements in coaxial transmission lines. *Water Resources
Research, 16*(3), 574–582.
The standard conversion from dielectric permittivity to volumetric water content,
used in [interpretation.md](interpretation.md). Fitted for mineral soils.

Skierucha, W., & Wilczek, A. (2012). A FDR sensor for measuring complex soil
dielectric permittivity in the 10–500 MHz frequency range. *Sensors, 12*(8),
10890–10905. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3472864/
Reports water content over-estimation from salinity in FDR sensors, and a
correction method using measured conductivity as the indicator of dielectric loss.

Kizito, F., et al. *Response of the TEROS 12 soil moisture sensor under different
soils and variable electrical conductivity*.
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11014125/

*Advances in calibration methods for FDR-based capacitive soil moisture sensors*.
https://pmc.ncbi.nlm.nih.gov/articles/PMC13259125/

*Impact of soil salinity, texture and measurement frequency on the relations
between soil moisture and 20 MHz–3 GHz dielectric permittivity spectrum*.
https://www.sciencedirect.com/science/article/abs/pii/S002216941930890X

## Software

merbanan. *rtl_433*. https://github.com/merbanan/rtl_433
The WH52 decoder, `src/devices/fineoffset_wh52.c`, contributed as pull request
3602 and merged July 13, 2026. Sample captures contributed to
`merbanan/rtl_433_tests` as pull request 508.

vgabor99. *Improve WH52 battery and conductivity reporting*. Pull request 3668,
merged August 26, 2026. Corrected the battery voltage location to byte 20 and
renamed the conductivity field.

vgabor99. *Fix wh52 battery reporting 2*. `merbanan/rtl_433_tests` pull request
519, opened August 23, 2026. The paired change updating the regression
expectations for the rename above.

It was not merged, and for about two weeks the WH52 regression failed: the decoder
emitted the new field names while the tests still expected the old ones. The
expectations were corrected on September 10, 2026 in commit `046e7e2` by Christian
Zuckschwerdt, which fixed the suite without merging his pull request. That pull
request is still open and now has nothing left to do.

pbkhrv. *rtl_433 Home Assistant add-ons*.
https://github.com/pbkhrv/rtl_433-hass-addons
The add-on used for all radio captures in this work.
