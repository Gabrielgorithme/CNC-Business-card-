"""First-pass sizing of the orthoplanar spring legs (analytic, to be confirmed by FEA).

Each leg is treated as a fixed-guided beam bending out of plane:
    sigma_max = 3 * E * t * d / L^2          (per mm of platform travel d)
    k_leg     = E * w * t^3 / L^3
Curved legs also see torsion, and the leg roots have a stress concentration,
so a knock-down factor Kt is applied. Handbook fatigue values (R = -1, polished);
aluminium has no true endurance limit, the 5e8-cycle strength is used instead.
"""
MATERIALS = {
    #            E [MPa]  yield  S(1e5)  S(1e6)  S(5e8)   -- approximate handbook values
    "7075-T6": (71700,   503,   300,    230,    159),
    "6061-T6": (68900,   276,   200,    140,     97),
}
KT = 1.4          # fillet + torsion + machined-surface allowance
N_LEGS = 3
W = 1.2           # leg width [mm]: 3.21 between slot centrelines less the 2.0 slot (2.2 with the first 1.0 slots; stiffness scales with W, stress at a given travel does not)
TRAVEL_NORMAL = 1.0   # what a finger does when playing with it [mm]
TRAVEL_ABUSE = 3.0    # someone pushing it as far as a fingertip goes [mm]

def leg(E, t, L, d):
    sigma = KT * 3 * E * t * d / L**2
    k = N_LEGS * E * W * t**3 / L**3
    return sigma, k

if __name__ == "__main__":
    for name, (E, Sy, S5, S6, S8) in MATERIALS.items():
        print(f"\n{name}  (yield {Sy} MPa, fatigue {S5}/{S6}/{S8} MPa at 1e5/1e6/5e8 cycles)")
        print(" t[mm]  L[mm]  k[N/mm]  sigma@1mm  life@1mm     sigma@3mm  yields?")
        for t in (0.3, 0.4, 0.5, 0.6):
            for L in (20, 30):
                s1, k = leg(E, t, L, TRAVEL_NORMAL)
                s3, _ = leg(E, t, L, TRAVEL_ABUSE)
                life = ">5e8" if s1 <= S8 else ">1e6" if s1 <= S6 else ">1e5" if s1 <= S5 else "<1e5"
                print(f" {t:4.1f}  {L:5d}  {k:7.2f}  {s1:8.0f}   {life:>8}   {s3:9.0f}   {'YES' if s3 > Sy else 'no'}")
