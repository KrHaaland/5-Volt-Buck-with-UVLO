# 5 Volt Buck with UVLO

A small 12 V to 5 V USB power adapter with an adjustable under-voltage lockout (UVLO),
built around the TI **TPS62933** 3 A synchronous buck converter.

It is meant for 12 V lead-acid systems (car, boat, cabin). The 5 V output switches off
when the battery sags to roughly 12.2 V and does not come back until the battery is being
charged again (roughly 13.3 V), so the adapter cannot flatten the battery.

The KiCad project files are named `USB-Adapter`.

## Specifications (as built)

| | |
|---|---|
| Input | 12 V nominal, Wago 2060-452 push-in terminal (J1). Converter range 3.8 V to 30 V. |
| Output | 5.16 V measured, USB-A receptacle (J2, TE 292303-1). Converter limit 3 A. |
| UVLO | Off at 12.1 to 12.3 V, on again at 13.3 to 13.4 V (measured, see tuning log) |
| Switching frequency | 1.2 MHz (RT pin tied to GND through R3) |
| Inductor | Würth 74439387068, WE-XHMI 7070, 6.8 µH |
| Soft start | C4 on the SS pin |
| Board | 40 × 18 mm, 2 layers |

## Resistor values: read this before building

**The resistor values in the schematic and in the exported BOM under `production/` are
not the values on the working boards.** The first boards were built with 5 % resistors,
which turned out to be too loose for both dividers, so the values were tuned by measuring
and swapping. The table below is the as-built, tested configuration.

| Function | Refs | As built (tested) | Schematic | `production/bom.csv` |
|---|---|---|---|---|
| UVLO divider (VIN → EN → GND) | R1 / R2 | **530 kΩ / 53 kΩ** | 330 kΩ / 33 kΩ | 511 kΩ / 88.7 kΩ |
| Output voltage (VBUS → FB → GND) | R6 / R7 | **130 kΩ / 24 kΩ** | 43 kΩ / 8.2 kΩ | 53.6 kΩ / 10.2 kΩ |

**Use 1 % resistors.** With 1 % parts the as-built values should land on target
without the tweaking described below. The 5 % parts used so far needed measuring and
testing against the specific batch.

### Output voltage (R6 / R7)

The TPS62933 regulates the FB pin to 0.8 V:

```
V_OUT = 0.8 V × (1 + R6 / R7)
130 kΩ / 24 kΩ  →  5.13 V calculated, 5.16 V measured
```

The output is deliberately a little above 5.00 V to make up for voltage drop in the
USB cable. USB allows 4.75 V to 5.25 V at the connector.

### Under-voltage lockout (R1 / R2)

The EN pin has a 1.21 V rising and 1.17 V falling threshold (typical). It also has an
internal pull-up of 0.7 µA that is always present, plus an extra 1.4 µA once the device
is enabled. That extra current is what creates the hysteresis across R1:

```
V_START ≈ 1.21 V × (R1 + R2) / R2  −  0.7 µA × R1
V_STOP  ≈ 1.17 V × (R1 + R2) / R2  −  2.1 µA × R1

530 kΩ / 53 kΩ  →  V_START ≈ 12.9 V, V_STOP ≈ 11.8 V (typical values)
```

Measured boards sit 0.3 to 0.5 V above these calculated numbers. That is consistent with
the EN threshold spread in the datasheet (rising threshold up to 1.28 V max) combined
with 5 % resistors. The hysteresis is about 1.1 V; the datasheet recommends more than
0.5 V.

**Disabling the UVLO:** leave out (or remove) R1 and R2. The EN pin then floats and the
converter's internal pull-up current enables it, so it simply runs over the chip's full
3.8 V to 30 V input range.

## Tuning log

Notes from bring-up of the first two boards, all with 5 % resistors.

### UVLO (R1 / R2)

| R1 / R2 | Cuts off at | Activates again at |
|---|---|---|
| 330 kΩ / 33 kΩ | 12.6 V | 13.4 V |
| 560 kΩ / 56 kΩ, board 1 | 12.3 V | 13.36 V |
| 560 kΩ / 56 kΩ, board 2 | 12.14 V | 13.31 V |

560 kΩ / 56 kΩ was used instead of 330 kΩ / 33 kΩ.

### Output voltage (R6 / R7)

| Try | R6 / R7 | Calculated | Measured | Note |
|---|---|---|---|---|
| 1 | 43 kΩ / 8.2 kΩ | 5.00 V | 4.88 V | Too low. |
| 2 | 56 kΩ / 10 kΩ | 5.28 V | 5.23 V | A bit much, should be lowered. |
| 3 | 82 kΩ / 15 kΩ | 5.17 V | 5.17 V | Fine. |
| 4 | 130 kΩ / 24 kΩ | 5.13 V | 5.16 V | Better. |
| 5 | 300 kΩ / 56 kΩ | 5.09 V | 5.22 V | |
| 6 | 130 kΩ / 24 kΩ | 5.13 V | 5.16 V | Went back to this. Good enough. |

The plan is to get 1 % resistors. The 5 % ones require tweaking and testing with the
specific batch.

## Repository contents

- `USB-Adapter.kicad_pro`, `.kicad_sch`, `.kicad_pcb`: KiCad project, schematic and board.
- `schematic.pdf`: plotted schematic.
- `production/`: JLCPCB export from the Fabrication Toolkit plugin (gerber zip, BOM,
  component positions, IPC netlist). This export is from an earlier revision: besides the
  resistor values above, it lists C4 as 33 nF while the schematic has 100 nF.
- `fabrication-toolkit-options.json`: settings used for the export.
