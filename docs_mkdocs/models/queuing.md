# Patient Choice & Queuing Model

The NHRA model uses a **Wardrop Equilibrium** approach to model endogenous demand at the Emergency Department (ED). Patients choose between the ED and General Practice (GP) based on relative utility.

## 1. Mathematical Formulation

The utility $U$ for a patient choosing an interface is defined as:

$$
U_{ED} = U_{base, ED} - \left( \frac{W_{ED}}{60} \times V_{time} \right)
$$

$$
U_{GP} = -( \frac{W_{GP}}{60} \times V_{time} ) - C_{OOP}
$$

Where:
- $W_{ED}$: Wait time in ED (minutes), derived from system occupancy.
- $W_{GP}$: Fixed wait time for a GP appointment.
- $V_{time}$: Value of patient time ($/hour).
- $C_{OOP}$: Out-of-pocket cost for GP.

## 2. Queuing Dynamics (M/M/s)

The ED wait time $W_{ED}$ is approximated using an M/M/s queuing model:

$$
W_{ED} = \frac{\rho^{\sqrt{2(s+1)}-1}}{s(1-\rho)} \times 60
$$

Where:
- $\rho$: System utilization (arrival rate / service rate).
- $s$: Number of servers (staffed beds).

## 3. Equilibrium Selection

We solve for the probability of choosing ED ($P_{ED}$) using a Logit choice model:

$$
P_{ED} = \frac{e^{\lambda U_{ED}}}{e^{\lambda U_{ED}} + e^{\lambda U_{GP}} + e^{\lambda U_{outside}}}
$$

The system iterates until demand $D_{ED} = D_{total} \times P_{ED}$ stabilizes.

## 4. Evidence Grounding
- **Time Value:** Grounded in ABS hourly wage data.
- **Wait Times:** Sourced from AIHW MyHospitals performance reports.
- **Costs:** Sourced from Medicare MBS data.
