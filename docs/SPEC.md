# SEIR-Vector Malaria Model: Mathematical Specification

**Project:** A Compartmental SEIR-Vector Model for Malaria Transmission Dynamics under Climate Variability in Urban Environments

**Status:** Professor-approved. This file is the SOURCE OF TRUTH.
Do not change any equation, formula, or definition in Sections 1-5 without explicit approval.

---

## 1. Urban Drainage and Clogging Index

| Symbol | Meaning | Range / Value |
|--------|---------|---------------|
| D_d | Drainage Density | [0, 1] (dimensionless or km/km²) |
| M_i | Maintenance Efficiency Index | [0, 1] (0 = fully blocked, 1 = perfectly clear) |
| epsilon | Smoothing constant | 0.001 |
| Ω | Clogging Index (also written D_m) | derived |

```
Ω = D_m = (1 - M_i) / (D_d + epsilon)
```

---

## 2. Aquatic Carrying Capacity

```
K_v(R, Ω) = K_0 * (1 + eta * Ω) * R(t)
```

- R(t): daily rainfall (mm/day)

Larval flushing mortality:

```
μ_A(R(t)) = μ_base + μ_flush * max(0, (R(t) - R_flush) / (Ω + epsilon))
```

---

## 3. Climate-Dependent Thermal Response Functions

T = temperature (°C)

**Biting rate, Brière function:**
```
a(T) = c_a * T * (T - T_0) * sqrt(T_m - T)
```

**Parasite incubation rate, Degree-Day model:**
```
γ_m(T) = (T - T_min) / DD
```

**Adult mosquito mortality, quadratic curve:**
```
μ_v(T) = 1 / (q_0 + q_1*T + q_2*T^2)
```

---

## 4. State Variables (8 Compartments)

**Humans:** N_h = S_h + E_h + I_h + R_h
- S_h: Susceptible
- E_h: Exposed
- I_h: Infectious
- R_h: Recovered

**Vectors:** N_v = S_v + E_v + I_v (adults)
- A_v: Aquatic (eggs/larvae)
- S_v: Susceptible adult
- E_v: Exposed adult
- I_v: Infectious adult

---

## 5. Differential Equations (ODE System)

**Vector equations**
```
dA_v/dt = φ_v * (1 - A_v / K_v(R, Ω)) * (S_v + E_v + I_v) - (θ_A + μ_A(R)) * A_v

dS_v/dt = θ_A * A_v - a(T) * β_vh * (I_h / N_h) * S_v - μ_v(T) * S_v

dE_v/dt = a(T) * β_vh * (I_h / N_h) * S_v - (γ_m(T) + μ_v(T)) * E_v

dI_v/dt = γ_m(T) * E_v - μ_v(T) * I_v
```

**Human equations**
```
dS_h/dt = Λ_h - a(T) * β_hv * (I_v / N_h) * S_h - μ_h * S_h + ρ * R_h

dE_h/dt = a(T) * β_hv * (I_v / N_h) * S_h - (α_h + μ_h) * E_h

dI_h/dt = α_h * E_h - (γ_h + μ_h + δ_h) * I_h

dR_h/dt = γ_h * I_h - (ρ + μ_h) * R_h
```

### Parameter glossary (symbols as used above)

| Symbol | Meaning |
|--------|---------|
| φ_v | Vector oviposition (egg-laying) rate |
| θ_A | Aquatic-to-adult maturation rate |
| μ_base | Baseline larval mortality |
| μ_flush | Flushing mortality coefficient |
| R_flush | Rainfall threshold above which flushing occurs (mm/day) |
| K_0 | Baseline carrying-capacity scaling |
| eta | Sensitivity of carrying capacity to clogging Ω |
| β_vh | Human-to-vector transmission probability per bite |
| β_hv | Vector-to-human transmission probability per bite |
| Λ_h | Human recruitment (birth/immigration) rate |
| μ_h | Human natural mortality rate |
| ρ | Rate of loss of immunity (R_h to S_h) |
| α_h | Human incubation rate (E_h to I_h) |
| γ_h | Human recovery rate |
| δ_h | Disease-induced human mortality |
| c_a, T_0, T_m | Brière function constants (T_0 = lower, T_m = upper thermal limit) |
| T_min, DD | Minimum temperature for development and degree-days required |
| q_0, q_1, q_2 | Quadratic mortality curve coefficients |

---

## 6. Implementation Notes (NOT part of the approved spec)

These are open items for discussion with the professor. Claude must NOT silently
"fix" them. Propose a solution, wait for approval, mark the change in code with
`# DEVIATION:` and log it in `docs/DEVIATIONS.md`.

1. **Division by zero:** K_v = 0 whenever R(t) = 0, so A_v / K_v is undefined on dry days.
2. **Brière domain:** a(T) is undefined or negative outside T_0 < T < T_m
   (sqrt of a negative number, or sign flips).
3. **Degree-day domain:** γ_m(T) is negative when T < T_min.
4. **Mortality denominator:** μ_v(T) can blow up or become negative if
   q_0 + q_1*T + q_2*T^2 <= 0 at some temperature.
5. **Parameter values:** all parameter values are currently UNKNOWN. Every value in
   params.py must be labelled either with its literature source or
   `PLACEHOLDER - needs literature value`.
6. **Time and units:** time unit is days, temperature is °C, rainfall is mm/day.
   Rates are per day. Synthetic T(t) and R(t) are 365-day sinusoidal/monsoonal arrays
   until real data is available.
7. **Initial conditions:** not specified in the spec. Must be chosen and documented.
8. **Peak malaria cases** (heatmap metric) is defined as max over t of I_h(t),
   unless the professor specifies otherwise.