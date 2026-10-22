import streamlit as st
import streamlit.components.v1 as components
import re

# ===============================
# SVG DIAGRAM LIBRARY
# (same rendering pattern as the CV simulator: raw SVG wrapped in a
# tiny standalone HTML page, rendered through components.html)
# ===============================

def svg_wrap(inner, width=800, height=280, title="", subtitle=""):
    header = ""
    if title:
        header += f'<text x="{width//2}" y="24" text-anchor="middle" font-family="Inter,sans-serif" font-size="14" font-weight="600" fill="#ECF0F1">{title}</text>'
    if subtitle:
        header += f'<text x="{width//2}" y="42" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#95A5A6">{subtitle}</text>'
    offset = 50 if (title or subtitle) else 0
    total_h = height + offset + 60
    svg = f'''<svg viewBox="0 0 {width} {total_h}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet" style="width:100%;display:block;">
  <rect width="{width}" height="{total_h}" fill="#1A2638" rx="8"/>
  {header}
  <g transform="translate(0,{offset})">{inner}</g>
</svg>'''
    html = f'''<!DOCTYPE html><html><body style="margin:0;padding:0;background:#1A2638;box-sizing:border-box;">
<div style="background:#1A2638;border:1px solid #2C3E50;border-radius:10px;overflow:visible;">{svg}</div>
</body></html>'''
    aspect_h_per_w = total_h / width
    iframe_h = int(750 * aspect_h_per_w) + 40
    return html, iframe_h


ARROW_DEFS = '<defs><marker id="ah" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#95A5A6"/></marker></defs>'

TEAL = "#1ABC9C"
TEAL_DEEP = "#16A085"
AMBER = "#E67E22"
AMBER_DEEP = "#D35400"
RED = "#E74C3C"
SLATE = "#95A5A6"
GRID = "#2C3E50"


def svg_ph_gauge(pH):
    W, H = 700, 150
    ox, ex = 60, 640
    lo, hi = 6.9, 7.8

    def x(v):
        return ox + (v - lo) / (hi - lo) * (ex - ox)

    acid_end = x(7.36)
    alk_start = x(7.44)
    color = TEAL if pH < 7.36 else (AMBER if pH > 7.44 else SLATE)
    mx = x(pH)

    ticks = ""
    t = 6.9
    while t <= 7.81:
        tx = x(round(t, 1))
        ticks += f'<line x1="{tx}" y1="72" x2="{tx}" y2="80" stroke="{GRID}"/>'
        ticks += label(tx, 96, f"{t:.1f}", size=9)
        t += 0.1

    inner = f'''
    <rect x="{ox}" y="60" width="{acid_end-ox}" height="16" fill="{TEAL}" opacity="0.30" rx="3"/>
    <rect x="{acid_end}" y="60" width="{alk_start-acid_end}" height="16" fill="{SLATE}" opacity="0.45" rx="3"/>
    <rect x="{alk_start}" y="60" width="{ex-alk_start}" height="16" fill="{AMBER}" opacity="0.30" rx="3"/>
    {ticks}
    {label((acid_end+alk_start)/2, 72, "NORMAL", color="#DDD", size=9)}
    <line x1="{mx}" y1="20" x2="{mx}" y2="76" stroke="{color}" stroke-width="3"/>
    <polygon points="{mx-7},20 {mx+7},20 {mx},32" fill="{color}"/>
    {label(mx, 14, f"pH {pH:.2f}", color=color, size=14, weight="700")}
    '''
    return svg_wrap(inner, W, H, "pH Scale", "Acidemia (teal) vs. Alkalemia (amber)")


def svg_primary_bars(pco2, hco3, primary):
    W, H = 620, 260
    pco2_emph = "Respiratory" in primary
    bx1, bx2 = 160, 420
    base_y = 220
    scale_pco2 = 2.6
    scale_hco3 = 5.6
    h_pco2 = pco2 * scale_pco2
    h_hco3 = hco3 * scale_hco3
    norm_lo_p, norm_hi_p = 36 * scale_pco2, 44 * scale_pco2
    norm_lo_h, norm_hi_h = 22 * scale_hco3, 26 * scale_hco3
    c_pco2 = AMBER if pco2_emph else TEAL
    c_hco3 = TEAL if pco2_emph else AMBER
    inner = f'''
    <rect x="{bx1-45}" y="{base_y-norm_hi_p}" width="90" height="{norm_hi_p-norm_lo_p}" fill="{SLATE}" opacity="0.20" rx="3"/>
    <rect x="{bx1-35}" y="{base_y-h_pco2}" width="70" height="{h_pco2}" fill="{c_pco2}" opacity="0.85" rx="3"/>
    {label(bx1, base_y-h_pco2-10, str(pco2), color=c_pco2, size=13, weight="700")}
    {label(bx1, base_y+22, "PCO2", color="#DDD", size=11, weight="600")}
    {label(bx1, base_y+38, "(normal 36-44)", color=SLATE, size=9)}

    <rect x="{bx2-45}" y="{base_y-norm_hi_h}" width="90" height="{norm_hi_h-norm_lo_h}" fill="{SLATE}" opacity="0.20" rx="3"/>
    <rect x="{bx2-35}" y="{base_y-h_hco3}" width="70" height="{h_hco3}" fill="{c_hco3}" opacity="0.85" rx="3"/>
    {label(bx2, base_y-h_hco3-10, str(hco3), color=c_hco3, size=13, weight="700")}
    {label(bx2, base_y+22, "HCO3", color="#DDD", size=11, weight="600")}
    {label(bx2, base_y+38, "(normal 22-26)", color=SLATE, size=9)}

    <line x1="90" y1="{base_y}" x2="530" y2="{base_y}" stroke="{GRID}" stroke-width="2"/>
    '''
    return svg_wrap(inner, W, H, "Measured value vs. normal range", "The highlighted bar is the primary driver; the other is reacting as compensation")


def svg_anion_gap(Na, Cl, HCO3, AG):
    W, H = 480, 300
    scale = 220 / Na
    base_y = 250
    left_x, right_x = 130, 320
    bar_w = 90
    cl_h = Cl * scale
    hco3_h = HCO3 * scale
    ag_h = AG * scale
    na_h = Na * scale
    gap_color = AMBER if AG > 14 else "#7F8C8D"
    gap_label = "Gap (UA)" if AG > 14 else "Gap"
    inner = f'''
    {label(left_x+bar_w/2, base_y-na_h-12, f"Na+ {Na}", color="#DDD", size=12, weight="700")}
    <rect x="{left_x}" y="{base_y-na_h}" width="{bar_w}" height="{na_h}" fill="{SLATE}" opacity="0.55" rx="3"/>
    {label(left_x+bar_w/2, base_y+20, "CATION", color=SLATE, size=10)}

    <rect x="{right_x}" y="{base_y-cl_h}" width="{bar_w}" height="{cl_h}" fill="{TEAL}" opacity="0.55" rx="3"/>
    {label(right_x+bar_w/2, base_y-cl_h/2+5, f"Cl- {Cl}", color="#08332C", size=11, weight="700")}

    <rect x="{right_x}" y="{base_y-cl_h-hco3_h}" width="{bar_w}" height="{hco3_h}" fill="{TEAL_DEEP}" opacity="0.75" rx="3"/>
    {label(right_x+bar_w/2, base_y-cl_h-hco3_h/2+5, f"HCO3- {HCO3}", color="#EAFBF6", size=11, weight="700")}

    <rect x="{right_x}" y="{base_y-cl_h-hco3_h-ag_h}" width="{bar_w}" height="{ag_h}" fill="{gap_color}" opacity="0.9" rx="3"/>
    {label(right_x+bar_w/2, base_y-cl_h-hco3_h-ag_h/2+5, f"{gap_label} {AG}", color="#3A2200", size=11, weight="700")}
    {label(right_x+bar_w/2, base_y+20, "ANIONS", color=SLATE, size=10)}

    <line x1="{left_x+bar_w+15}" y1="{base_y-na_h}" x2="{right_x-15}" y2="{base_y-na_h}" stroke="{GRID}" stroke-dasharray="4,3"/>
    '''
    return svg_wrap(inner, W, H, "Electroneutrality ledger", "Cations must equal anions -- the gap is the unmeasured anion")


def svg_corrected_bicarb(corrected):
    W, H = 640, 150
    lo = min(24, corrected) - 6
    hi = max(24, corrected) + 6
    ox, ex = 60, 580

    def x(v):
        return ox + (v - lo) / (hi - lo) * (ex - ox)

    target_x = x(24)
    val_x = x(corrected)
    color = TEAL if corrected == 24 else (AMBER if corrected > 24 else RED)
    inner = f'''
    <line x1="{ox}" y1="70" x2="{ex}" y2="70" stroke="{GRID}" stroke-width="3"/>
    <line x1="{target_x}" y1="40" x2="{target_x}" y2="100" stroke="{SLATE}" stroke-width="2" stroke-dasharray="5,4"/>
    {label(target_x, 28, "target 24", color=SLATE, size=10)}
    {label(target_x, 118, "(pure gap acidosis)", color=SLATE, size=9)}
    <circle cx="{val_x}" cy="70" r="8" fill="{color}"/>
    {label(val_x, 130, f"corrected {corrected}", color=color, size=13, weight="700")}
    '''
    return svg_wrap(inner, W, H, "Corrected bicarbonate vs. target", "")


def svg_comp_single(lo, hi, measured, unit_label):
    W, H = 640, 160
    axis_min = min(lo, measured) - 8
    axis_max = max(hi, measured) + 8
    ox, ex = 60, 580

    def x(v):
        return ox + (v - axis_min) / (axis_max - axis_min) * (ex - ox)

    band_x1, band_x2 = x(lo), x(hi)
    in_range = lo <= measured <= hi
    color = TEAL if in_range else RED
    mx = x(measured)
    inner = f'''
    <line x1="{ox}" y1="80" x2="{ex}" y2="80" stroke="{GRID}" stroke-width="3"/>
    <rect x="{band_x1}" y="72" width="{band_x2-band_x1}" height="16" fill="{SLATE}" opacity="0.4" rx="4"/>
    {label((band_x1+band_x2)/2, 60, f"expected {lo}-{hi}", color=SLATE, size=10)}
    <line x1="{mx}" y1="45" x2="{mx}" y2="115" stroke="{color}" stroke-width="3"/>
    <circle cx="{mx}" cy="80" r="7" fill="{color}"/>
    {label(mx, 30, f"measured {measured}", color=color, size=13, weight="700")}
    {label((ox+ex)/2, 140, unit_label, color=SLATE, size=10)}
    '''
    return svg_wrap(inner, W, H, "Measured vs. expected compensation", "")


def svg_comp_double(acute, chronic, measured, unit_label, winner):
    W, H = 640, 190
    lo = min(acute, chronic, measured) - 4
    hi = max(acute, chronic, measured) + 4
    ox, ex = 60, 580

    def x(v):
        return ox + (v - lo) / (hi - lo) * (ex - ox)

    ac_x, ch_x, m_x = x(acute), x(chronic), x(measured)
    ac_color = TEAL if winner == "acute" else "#5D6D7E"
    ch_color = TEAL if winner == "chronic" else "#5D6D7E"
    inner = f'''
    <line x1="{ox}" y1="95" x2="{ex}" y2="95" stroke="{GRID}" stroke-width="3"/>
    <line x1="{ac_x}" y1="55" x2="{ac_x}" y2="135" stroke="{ac_color}" stroke-width="{4 if winner=='acute' else 2}" stroke-dasharray="{'0' if winner=='acute' else '5,4'}"/>
    {label(ac_x, 44, f"acute {acute}", color=ac_color, size=11, weight=("700" if winner=="acute" else "400"))}
    <line x1="{ch_x}" y1="55" x2="{ch_x}" y2="135" stroke="{ch_color}" stroke-width="{4 if winner=='chronic' else 2}" stroke-dasharray="{'0' if winner=='chronic' else '5,4'}"/>
    {label(ch_x, 155, f"chronic {chronic}", color=ch_color, size=11, weight=("700" if winner=="chronic" else "400"))}
    <circle cx="{m_x}" cy="95" r="8" fill="{AMBER}"/>
    {label(m_x, 25, f"measured {measured}", color=AMBER_DEEP, size=13, weight="700")}
    {label((ox+ex)/2, 178, unit_label, color=SLATE, size=10)}
    '''
    return svg_wrap(inner, W, H, "Measured value vs. acute / chronic predictions", "")


def label(x, y, text, color="#95A5A6", size=10, anchor="middle", weight="normal"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Inter,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{text}</text>'


# ===============================
# CLINICAL DATA + STEP BUILDER
# ===============================

def classify_ph(pH):
    if pH < 7.36:
        return "Acidemia"
    if pH > 7.44:
        return "Alkalemia"
    return "Normal pH"


def rotate(arr, seed_a, seed_b):
    seed = (seed_a * 13 + seed_b * 7) % len(arr)
    return arr[seed:] + arr[:seed]


def unique_near(true_val, seed_a, seed_b):
    seed = (seed_a * 17 + seed_b * 3) % 4
    delta_sets = [[-6, -3, 0, 4], [-4, 0, 3, 7], [-7, -2, 0, 3], [-3, 0, 5, 9]]
    deltas = delta_sets[seed]
    vals = [true_val + d for d in deltas]
    if true_val not in vals:
        vals[1] = true_val
    return sorted(set(vals))


def short_context(c):
    return c["title"].split("—")[1].strip() if "—" in c["title"] else c["title"]


RAW_CASES = [
    dict(
        id=0, tag="High Anion Gap · Compensated", difficulty="Intermediate",
        title="37M — motor vehicle collision",
        vignette=("37-year-old male, restrained driver in a high-speed MVC, transferred to the ED "
                   "with abdominal pain, dizziness, and left-upper-quadrant ecchymosis over the spleen. "
                   "BP 80/40, HR 150, RR 26, afebrile."),
        labs=dict(Na=136, K=5.8, Cl=100, HCO3=15, BUN=25, Cr=1.5, Alb=4.0),
        abg=dict(pH=7.30, pco2=29, po2=90),
        primary="Metabolic acidosis",
        ag=dict(value=21, high=True),
        corrected=dict(value=24, verdict="pure"),
        compensation=dict(type="winter", lo=28.5, hi=32.5, mid=30.5, measured=29, verdict="appropriate"),
        finalDx=("High anion-gap metabolic acidosis from hemorrhagic-shock lactic acidosis, "
                  "with appropriate respiratory compensation."),
        pearl=("Lactate is the unmeasured anion here — hypotension and tachycardia from splenic "
               "hemorrhage are producing tissue hypoperfusion. The lungs are already blowing off CO2 "
               "exactly as much as Winter's formula predicts, so there is no second respiratory "
               "disorder yet."),
    ),
    dict(
        id=1, tag="Mixed Metabolic Acidosis · Compensated", difficulty="Advanced",
        title="42M — diabetic with vomiting and diarrhea",
        vignette=("42-year-old man with type 1 diabetes presents with nausea, watery diarrhea, and "
                   "fever. Fingerstick glucose 500 mg/dL. T 39.0°C, HR 125, BP 90/60, RR 26."),
        labs=dict(Na=140, K=4.5, Cl=110, HCO3=10, BUN=25, Cr=1.5, Alb=4.0),
        abg=dict(pH=7.30, pco2=23, po2=85),
        primary="Metabolic acidosis",
        ag=dict(value=20, high=True),
        corrected=dict(value=18, verdict="nonAG-coexists"),
        compensation=dict(type="winter", lo=21, hi=25, mid=23, measured=23, verdict="appropriate"),
        finalDx=("Mixed acidosis: high anion-gap acidosis from DKA (ketoacids) plus non-anion-gap "
                  "acidosis from bicarbonate loss in diarrhea, with appropriate respiratory "
                  "compensation."),
        pearl=("Two acid-producing problems are stacked on one patient. DKA generates ketoacids "
               "(raises the gap); diarrhea loses HCO3 in the stool (drops bicarbonate without "
               "raising the gap). The corrected bicarbonate — not the gap alone — is what unmasks "
               "the second process."),
    ),
    dict(
        id=2, tag="Mixed Metabolic + Respiratory · Critical", difficulty="Advanced",
        title="38M — found performing CPR on his wife",
        vignette=("EMS is called for a man performing CPR on his asystolic wife. He appears agitated, "
                   "incoherent, and \u201cdrunk,\u201d though vitals are initially normal. In the ED he "
                   "develops abdominal pain, then over 45 minutes deteriorates to GCS 9, tachypnea, "
                   "seizures, and PEA arrest requiring intubation, epinephrine, and pacing."),
        labs=dict(Na=153, K=5.4, Cl=108, HCO3=5, BUN=None, Cr=None, Alb=None),
        abg=dict(pH=6.49, pco2=62, po2=None),
        primary="Metabolic acidosis",
        ag=dict(value=40, high=True),
        corrected=dict(value=33, verdict="advanced"),
        compensation=dict(type="winter", lo=13.5, hi=17.5, mid=15.5, measured=62, verdict="resp-acidosis"),
        finalDx=("Severe high anion-gap metabolic acidosis (ethylene glycol) with a superimposed "
                  "respiratory acidosis — the patient could not hyperventilate enough to compensate "
                  "and was instead hypoventilating toward arrest."),
        pearl=("This is the classic ethylene-glycol case from the lecture. A PCO2 of 62 is "
               "dramatically higher than the ~15.5 that Winter's formula predicts — the respiratory "
               "system isn't compensating, it's failing. That failure (CNS depression, seizures, "
               "arrest) is what turned a survivable poisoning into a fatal one."),
    ),
    dict(
        id=3, tag="Simple Metabolic Alkalosis · Compensated", difficulty="Intermediate",
        title="52M — post-appendectomy ileus",
        vignette=("52-year-old man, post-appendectomy, develops an ileus. A nasogastric tube is "
                   "placed for decompression and drains a large volume of gastric contents over two "
                   "days."),
        labs=dict(Na=139, K=3.6, Cl=96, HCO3=33, BUN=15, Cr=1.2, Alb=4.0),
        abg=dict(pH=7.48, pco2=48, po2=75),
        primary="Metabolic alkalosis",
        ag=dict(value=10, high=False),
        corrected=dict(value=None, verdict="n/a"),
        compensation=dict(type="metalk", lo=45.2, hi=49.2, mid=47.2, measured=48, verdict="appropriate"),
        finalDx=("Simple metabolic alkalosis from gastric acid (HCl) loss via NG suction, with "
                  "appropriate hypoventilatory compensation."),
        pearl=("Losing gastric HCl is a loss of acid, which is mathematically identical to gaining "
               "bicarbonate. The lungs respond by hypoventilating to raise PCO2 — but they can only "
               "push this so far before hypoxia becomes the limiting factor, which is why "
               "respiratory compensation for alkalosis is capped."),
    ),
    dict(
        id=4, tag="Chronic Respiratory Acidosis · Compensated", difficulty="Intermediate",
        title="75M — COPD, routine follow-up",
        vignette=("75-year-old man with longstanding COPD presents to clinic for a routine follow-up "
                   "visit. He is at his baseline functional status, with no acute complaints."),
        labs=dict(Na=140, K=3.6, Cl=100, HCO3=31, BUN=15, Cr=1.2, Alb=4.0),
        abg=dict(pH=7.35, pco2=60, po2=65),
        primary="Respiratory acidosis",
        ag=dict(value=9, high=False),
        corrected=dict(value=None, verdict="n/a"),
        compensation=dict(type="resp-acidosis", dPco2=20, acute=26, chronic=30, measured=31, verdict="chronic"),
        finalDx=("Chronic respiratory acidosis from longstanding COPD, with appropriate chronic "
                  "renal compensation (bicarbonate reabsorption)."),
        pearl=("The pH is nearly normal despite a PCO2 of 60 — that near-normalization only happens "
               "after days of renal compensation, which is why this pattern says 'chronic,' not "
               "'acute.'"),
    ),
    dict(
        id=5, tag="Acute Respiratory Alkalosis · Compensated", difficulty="Intermediate",
        title="62M — post-stroke, intubated in the ICU",
        vignette=("62-year-old man status-post acute cerebrovascular accident, intubated and "
                   "mechanically ventilated in the ICU. No prior pulmonary or renal disease."),
        labs=dict(Na=140, K=4.1, Cl=108, HCO3=22, BUN=15, Cr=0.9, Alb=4.0),
        abg=dict(pH=7.51, pco2=30, po2=89),
        primary="Respiratory alkalosis",
        ag=dict(value=10, high=False),
        corrected=dict(value=None, verdict="n/a"),
        compensation=dict(type="resp-alkalosis", dPco2=10, acute=22, chronic=20, measured=22, verdict="acute"),
        finalDx=("Acute respiratory alkalosis, most likely from a central hyperventilation drive "
                  "following acute CVA, with only the fast intracellular buffering expected this "
                  "early — no time yet for renal compensation."),
        pearl=("Onset was hours ago, not days — so the kidneys haven't had time to excrete "
               "bicarbonate yet. The measured HCO3 matches the 'acute' prediction almost exactly."),
    ),
]


def ph_explain(option, pH):
    in_range = 7.36 <= pH <= 7.44
    if option == "Acidemia":
        if pH < 7.36:
            return f"**Correct!** Acidemia is defined simply as pH below 7.36. This patient's pH of {pH:.2f} sits below that cutoff, meaning there is more free hydrogen ion in the blood than normal, regardless of which organ system caused it."
        return f"**Incorrect:** Acidemia requires a pH below 7.36. This patient's pH is {pH:.2f}, which is {'inside the normal 7.36-7.44 range' if in_range else 'above 7.44'}, so acidemia doesn't fit."
    if option == "Alkalemia":
        if pH > 7.44:
            return f"**Correct!** Alkalemia is defined simply as pH above 7.44. This patient's pH of {pH:.2f} sits above that cutoff, meaning there is less free hydrogen ion in the blood than normal, regardless of which organ system caused it."
        return f"**Incorrect:** Alkalemia requires a pH above 7.44. This patient's pH is {pH:.2f}, which is {'inside the normal 7.36-7.44 range' if in_range else 'below 7.36'}, so alkalemia doesn't fit."
    if in_range:
        return f"**Technically correct, but be careful:** a pH of {pH:.2f} is within the normal 7.36-7.44 range, yet that alone never rules out a disorder. Two opposing processes (an acidosis and an alkalosis happening together) can cancel out and leave the pH looking deceptively normal."
    return f"**Incorrect:** A pH of {pH:.2f} falls outside the normal 7.36-7.44 range, so it can't be called normal. Even when pH is normal, that never rules out a disorder -- it's a reminder to keep working through the algorithm, not a stopping point."


def primary_explain(option, case):
    pco2 = case["abg"]["pco2"]
    hco3 = case["labs"]["HCO3"]
    correct = case["primary"]
    requirement = {
        "Metabolic acidosis": f"a low HCO3 (normal 22-26) driving the pH down. Here HCO3 is {hco3}.",
        "Metabolic alkalosis": f"a high HCO3 (normal 22-26) driving the pH up. Here HCO3 is {hco3}.",
        "Respiratory acidosis": f"a high PCO2 (normal 36-44) driving the pH down. Here PCO2 is {pco2}.",
        "Respiratory alkalosis": f"a low PCO2 (normal 36-44) driving the pH up. Here PCO2 is {pco2}.",
    }
    if option == correct:
        other = f"PCO2 of {pco2}" if "Metabolic" in option else f"HCO3 of {hco3}"
        return f"**Correct!** {requirement[option]} That's the primary abnormality, and the {other} is only reacting to it as compensation."
    return f"**Incorrect:** {option} would require {requirement[option]} That's not what's driving this picture -- the pattern here actually points to {correct.lower()} instead."


def ag_explain(v, case):
    Na, Cl, HCO3 = case["labs"]["Na"], case["labs"]["Cl"], case["labs"]["HCO3"]
    ag_true = case["ag"]["value"]
    if v == ag_true:
        classification = "elevated, meaning an unmeasured anion is present" if v > 14 else "within the normal ~12 +/- 2 range"
        return f"**Correct!** {Na} - ({Cl} + {HCO3}) = {v}, which is {classification}."
    return f"**Incorrect:** Recalculating: {Na} - ({Cl} + {HCO3}) = {ag_true}, not {v}. The anion gap is sodium minus the sum of chloride and bicarbonate -- make sure Cl and HCO3 are added together first."


def corrected_explain(v, case):
    hco3 = case["labs"]["HCO3"]
    ag_true = case["ag"]["value"]
    corr_true = case["corrected"]["value"]
    if v == corr_true:
        if corr_true == 24:
            tail = "landing right at 24 -- the rise in the gap fully explains the fall in bicarbonate, so this is a pure high-anion-gap acidosis with no second metabolic process."
        elif corr_true > 24:
            tail = "landing above 24 -- there's more bicarbonate present than the gap alone explains. In milder cases that means a co-existing metabolic alkalosis; in a case this severe, it's a cue to look closely at the respiratory response next."
        else:
            tail = "landing below 24 -- bicarbonate fell by more than the rise in the gap accounts for, meaning a co-existing non-anion-gap acidosis is also present."
        return f"**Correct!** Measured HCO3 + (anion gap - 12) = {hco3} + ({ag_true} - 12) = {v}, {tail}"
    return f"**Incorrect:** The corrected bicarbonate is measured HCO3 + (anion gap - 12) = {hco3} + ({ag_true} - 12) = {corr_true}, not {v}."


def confirm_explain(option, case, correct_text):
    ag_val = case["ag"]["value"]
    if option == correct_text:
        return f"**Correct!** With a normal anion gap ({ag_val}), there's no organic or mineral acid accumulating that needs to be corrected for, so the next move is simply to check whether the respiratory or renal response is appropriately compensating."
    if "must still be corrected" in option:
        return f"**Incorrect:** The corrected-bicarbonate calculation only matters when the anion gap is elevated above roughly 12. With a normal gap here ({ag_val}), there's nothing for that formula to correct."
    return "**Incorrect:** The anion gap doesn't confirm or refute the primary disorder -- that was already established from the direction PCO2 and HCO3 moved. The gap only tells us whether an unmeasured anion is contributing on top of that."


def winter_explain(option, case):
    comp = case["compensation"]
    hco3 = case["labs"]["HCO3"]
    measured = comp["measured"]
    lo, hi, mid = comp["lo"], comp["hi"], comp["mid"]
    exp_text = f"Winter's formula predicts expected PCO2 = 1.5 x {hco3} + 8 = {mid} (range {lo}-{hi})."
    if option.startswith("Appropriately"):
        if comp["verdict"] == "appropriate":
            return f"**Correct!** {exp_text} The measured PCO2 of {measured} falls right inside that window, so the lungs are compensating exactly as expected."
        return f"**Incorrect:** {exp_text} The measured PCO2 of {measured} is far outside that window, so this isn't simple appropriate compensation -- something else is going on."
    if "alkalosis" in option:
        if comp["verdict"] == "appropriate":
            return f"**Incorrect:** {exp_text} The measured PCO2 of {measured} sits inside that range rather than below it, so there's no additional respiratory alkalosis."
        return f"**Incorrect:** A co-existing respiratory alkalosis would need the measured PCO2 to be lower than the expected {mid}. Here it's {measured} -- far higher, not lower."
    if comp["verdict"] == "resp-acidosis":
        return f"**Correct!** {exp_text} The measured PCO2 of {measured} is far above that entire range -- the respiratory system isn't just failing to fully compensate, it's adding its own acidosis on top."
    return f"**Incorrect:** A co-existing respiratory acidosis would need the measured PCO2 to be higher than the expected {mid}. Here it's {measured}, which falls right in the predicted range."


def metalk_explain(option, case):
    comp = case["compensation"]
    hco3 = case["labs"]["HCO3"]
    measured = comp["measured"]
    lo, hi, mid = comp["lo"], comp["hi"], comp["mid"]
    dhco3 = hco3 - 24
    exp_text = f"Expected PCO2 = 0.8 x (HCO3 - 24) + 40 = 0.8 x {dhco3} + 40 = {mid} (range {lo}-{hi})."
    if option.startswith("Appropriately"):
        return f"**Correct!** {exp_text} The measured PCO2 of {measured} falls right inside that window, so the lungs are hypoventilating exactly as much as this degree of alkalosis predicts."
    if "acidosis" in option:
        return f"**Incorrect:** {exp_text} A co-existing respiratory acidosis would need the measured PCO2 above that range; here it's {measured}, sitting inside the range instead."
    return f"**Incorrect:** {exp_text} A co-existing respiratory alkalosis would need the measured PCO2 below that range; here it's {measured}, sitting inside the range instead."


def resp_acidosis_explain(option, case):
    comp = case["compensation"]
    dpco2, acute, chronic, measured = comp["dPco2"], comp["acute"], comp["chronic"], comp["measured"]
    if option == "Acute respiratory acidosis":
        text = f"Acute compensation for a {dpco2} mmHg rise in PCO2 (fast intracellular buffering only) predicts HCO3 of about {acute}."
        if comp["verdict"] == "acute":
            return f"**Correct!** {text} The measured HCO3 of {measured} matches this."
        return f"**Incorrect:** {text} The measured HCO3 of {measured} is well above this and matches the chronic prediction instead."
    if option == "Chronic respiratory acidosis":
        text = f"Chronic compensation for a {dpco2} mmHg rise in PCO2 (days of renal bicarbonate retention) predicts HCO3 of about {chronic}."
        if comp["verdict"] == "chronic":
            return f"**Correct!** {text} The measured HCO3 of {measured} matches this closely, consistent with a longstanding, stable process."
        return f"**Incorrect:** {text} The measured HCO3 of {measured} doesn't match this -- it lines up with the acute prediction instead."
    return f"**Incorrect:** The measured HCO3 of {measured} is clearly elevated above the uncompensated baseline of 24 in the expected direction for respiratory acidosis, so some renal compensation has already occurred -- it isn't absent."


def resp_alkalosis_explain(option, case):
    comp = case["compensation"]
    dpco2, acute, chronic, measured = comp["dPco2"], comp["acute"], comp["chronic"], comp["measured"]
    if option == "Acute respiratory alkalosis":
        text = f"Acute compensation for a {dpco2} mmHg fall in PCO2 (fast intracellular buffering only) predicts HCO3 of about {acute}."
        if comp["verdict"] == "acute":
            return f"**Correct!** {text} The measured HCO3 of {measured} matches this almost exactly, consistent with an event that started hours, not days, ago."
        return f"**Incorrect:** {text} The measured HCO3 of {measured} doesn't match this -- it matches the chronic prediction instead."
    if option == "Chronic respiratory alkalosis":
        text = f"Chronic compensation for a {dpco2} mmHg fall in PCO2 (days of renal bicarbonate excretion) predicts HCO3 of about {chronic}."
        if comp["verdict"] == "chronic":
            return f"**Correct!** {text} The measured HCO3 of {measured} matches this closely."
        return f"**Incorrect:** {text} The measured HCO3 of {measured} is higher than this and matches the acute prediction instead."
    return f"**Incorrect:** The measured HCO3 of {measured} is clearly reduced below the uncompensated baseline of 24 in the expected direction for respiratory alkalosis, so some renal compensation has already occurred -- it isn't absent."


def dx_explain(option, case, all_cases):
    if option == case["finalDx"]:
        return f"**Correct!** {case['pearl']}"
    donor = next((k for k in all_cases if k["finalDx"] == option), None)
    donor_ctx = f" That description fits a patient like {short_context(donor)}, not this one." if donor else ""
    return f"**Incorrect for this patient.**{donor_ctx} Nothing in this patient's story or labs ({short_context(case)}) supports it -- always let the clinical scenario decide between look-alike diagnoses, then use the numbers to confirm it."


def build_dx_distractors(c, all_cases):
    others = [k["finalDx"] for k in all_cases if k["id"] != c["id"]]
    return [c["finalDx"], others[(c["id"] + 1) % len(others)], others[(c["id"] + 3) % len(others)]]


def comp_short_label(case):
    comp = case["compensation"]
    if comp["type"] in ("winter", "metalk"):
        if comp["verdict"] == "appropriate":
            return "appropriate"
        if comp["verdict"] == "resp-acidosis":
            return "+ resp. acidosis"
        return "mismatch"
    if comp["type"] == "resp-acidosis":
        return "chronic" if comp["verdict"] == "chronic" else "acute"
    return "acute" if comp["verdict"] == "acute" else "chronic"


def build_case_steps(c, all_cases):
    steps = []
    pH = c["abg"]["pH"]
    ph_class = classify_ph(pH)

    order = rotate(["Acidemia", "Alkalemia", "Normal pH — no disorder possible"], c["id"], 1)
    correct_idx = order.index(ph_class)
    explanations = [ph_explain(o, pH) for o in order]
    html, h = svg_ph_gauge(pH)
    steps.append(dict(
        question=f"The arterial pH is {pH:.2f}. What acid-base state does this represent?",
        options=order, correct_idx=correct_idx, explanations=explanations,
        svg_html=html, svg_height=h,
    ))

    order = rotate(["Metabolic acidosis", "Metabolic alkalosis", "Respiratory acidosis", "Respiratory alkalosis"], c["id"], 2)
    correct_idx = order.index(c["primary"])
    explanations = [primary_explain(o, c) for o in order]
    html, h = svg_primary_bars(c["abg"]["pco2"], c["labs"]["HCO3"], c["primary"])
    steps.append(dict(
        question="Looking at how PCO2 and HCO3 have each moved from normal, which is the primary disorder?",
        options=order, correct_idx=correct_idx, explanations=explanations,
        svg_html=html, svg_height=h,
    ))

    ag_true = c["ag"]["value"]
    ag_vals = unique_near(ag_true, c["id"], 3)
    options = [f"AG = {v} — {'elevated' if v > 14 else 'normal'}" for v in ag_vals]
    correct_idx = ag_vals.index(ag_true)
    explanations = [ag_explain(v, c) for v in ag_vals]
    html, h = svg_anion_gap(c["labs"]["Na"], c["labs"]["Cl"], c["labs"]["HCO3"], ag_true)
    steps.append(dict(
        question="Using this patient's Na, Cl, and HCO3, what is the anion gap — and is it elevated?",
        options=options, correct_idx=correct_idx, explanations=explanations,
        svg_html=html, svg_height=h,
    ))

    if c["ag"]["high"]:
        corr_true = c["corrected"]["value"]
        corr_vals = unique_near(corr_true, c["id"], 4)
        options = [f"Corrected HCO3 = {v}" for v in corr_vals]
        correct_idx = corr_vals.index(corr_true)
        explanations = [corrected_explain(v, c) for v in corr_vals]
        html, h = svg_corrected_bicarb(corr_true)
        steps.append(dict(
            question="This anion gap is elevated. Once you adjust the bicarbonate to account for it, what does the corrected value tell you?",
            options=options, correct_idx=correct_idx, explanations=explanations,
            svg_html=html, svg_height=h,
        ))
    else:
        confirm_text = "There is no unmeasured-anion process to account for — go straight to checking compensation"
        order = rotate([
            confirm_text,
            "The bicarbonate must still be corrected using the AG formula",
            "A normal AG means the primary disorder cannot be confirmed",
        ], c["id"], 4)
        correct_idx = order.index(confirm_text)
        explanations = [confirm_explain(o, c, confirm_text) for o in order]
        html, h = svg_anion_gap(c["labs"]["Na"], c["labs"]["Cl"], c["labs"]["HCO3"], ag_true)
        steps.append(dict(
            question="The anion gap here is normal. What does that tell you before moving on?",
            options=order, correct_idx=correct_idx, explanations=explanations,
            svg_html=html, svg_height=h,
        ))

    comp = c["compensation"]
    if comp["type"] == "winter":
        opts = [
            "Appropriately compensated — measured PCO2 falls in the expected range",
            "Additional respiratory alkalosis — measured PCO2 is lower than expected",
            "Additional respiratory acidosis — measured PCO2 is higher than expected",
        ]
        correct_idx = 0 if comp["verdict"] == "appropriate" else 2
        explanations = [winter_explain(o, c) for o in opts]
        question = "Given this degree of metabolic acidosis, has the respiratory system compensated appropriately?"
        html, h = svg_comp_single(comp["lo"], comp["hi"], comp["measured"], "PCO2 (mmHg)")
    elif comp["type"] == "metalk":
        opts = [
            "Appropriately compensated — measured PCO2 falls in the expected range",
            "Additional respiratory acidosis is present",
            "Additional respiratory alkalosis is present",
        ]
        correct_idx = 0
        explanations = [metalk_explain(o, c) for o in opts]
        question = "Given this degree of metabolic alkalosis, has the respiratory system compensated appropriately?"
        html, h = svg_comp_single(comp["lo"], comp["hi"], comp["measured"], "PCO2 (mmHg)")
    elif comp["type"] == "resp-acidosis":
        opts = ["Acute respiratory acidosis", "Chronic respiratory acidosis", "Neither — this is an uncompensated disorder"]
        correct_idx = 0 if comp["verdict"] == "acute" else 1
        explanations = [resp_acidosis_explain(o, c) for o in opts]
        question = "Given how long this elevated PCO2 has likely been present, does the bicarbonate fit an acute or a chronic compensatory pattern?"
        html, h = svg_comp_double(comp["acute"], comp["chronic"], comp["measured"], "HCO3 (mEq/L)", comp["verdict"])
    else:
        opts = ["Acute respiratory alkalosis", "Chronic respiratory alkalosis", "Neither — this is an uncompensated disorder"]
        correct_idx = 0 if comp["verdict"] == "acute" else 1
        explanations = [resp_alkalosis_explain(o, c) for o in opts]
        question = "Given how long this reduced PCO2 has likely been present, does the bicarbonate fit an acute or a chronic compensatory pattern?"
        html, h = svg_comp_double(comp["acute"], comp["chronic"], comp["measured"], "HCO3 (mEq/L)", comp["verdict"])

    steps.append(dict(question=question, options=opts, correct_idx=correct_idx, explanations=explanations, svg_html=html, svg_height=h))

    dx_opts = build_dx_distractors(c, all_cases)
    order = rotate(dx_opts, c["id"], 6)
    correct_idx = order.index(c["finalDx"])
    explanations = [dx_explain(o, c, all_cases) for o in order]
    steps.append(dict(
        question="Putting the labs together with the story at the bedside, what's the best overall interpretation?",
        options=order, correct_idx=correct_idx, explanations=explanations,
        svg_html=None, svg_height=0,
    ))

    return steps


def build_cases_data():
    data = {}
    for c in RAW_CASES:
        key = f"case{c['id']+1}"
        po2 = c["abg"]["po2"]
        initial_labs = {
            "pH": f"{c['abg']['pH']:.2f}",
            "PCO2": f"{c['abg']['pco2']} mmHg",
            "PO2": f"{po2} mmHg" if po2 is not None else "n/a",
            "HCO3": f"{c['labs']['HCO3']} mEq/L",
            "Na": f"{c['labs']['Na']} mEq/L",
            "K": f"{c['labs']['K']} mEq/L",
            "Cl": f"{c['labs']['Cl']} mEq/L",
        }
        if c["labs"]["BUN"] is not None:
            initial_labs["BUN"] = f"{c['labs']['BUN']} mg/dL"
            initial_labs["Cr"] = f"{c['labs']['Cr']} mg/dL"
            initial_labs["Albumin"] = f"{c['labs']['Alb']} g/dL"
        data[key] = dict(
            button_label=f"Case {c['id']+1}",
            difficulty=c["difficulty"],
            title=c["title"],
            tag=c["tag"],
            vignette=c["vignette"],
            initial_labs=initial_labs,
            steps=build_case_steps(c, RAW_CASES),
            pearl=c["pearl"],
            final_dx=c["finalDx"],
        )
    return data


CASES_DATA = build_cases_data()

# ===============================
# PAGE CONFIG & CSS
# ===============================
st.set_page_config(page_title="Acid-Base Bedside Simulator", layout="wide", page_icon="🩺", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, .stApp { background-color: #1A2638 !important; font-family: 'Inter', sans-serif; color: #ECF0F1; }
    [data-testid="stSidebar"] { background: #243447 !important; border-right: 1px solid #2C3E50; }
    [data-testid="stSidebar"] * { color: #ECF0F1 !important; }
    p, li, label, div, span { color: #ECF0F1; }
    h1, h2, h3, h4, h5 { color: #ECF0F1 !important; font-weight: 600; }

    .app-header {
        background: linear-gradient(135deg, #16A085 0%, #243447 60%);
        padding: 28px 32px 20px; border-radius: 12px; margin-bottom: 28px;
        border: 1px solid #16A085; position: relative; overflow: hidden;
    }
    .app-header::before { content: "🩺"; position: absolute; right: 24px; top: 50%; transform: translateY(-50%); font-size: 72px; opacity: 0.15; }
    .app-header h1 { font-size: 2.1rem !important; font-weight: 700 !important; margin: 0 0 6px !important; }
    .app-header p { color: rgba(236,240,241,0.75) !important; font-size: 0.95rem; margin: 0; }

    .vignette-box {
        background: #1E2E42; border: 1px solid #2C3E50; border-left: 4px solid #16A085;
        border-radius: 10px; padding: 22px 26px; font-size: 0.95rem; line-height: 1.75; margin-bottom: 20px;
    }
    .labs-strip {
        background: #243447; border: 1px solid #2C3E50; border-radius: 8px; padding: 12px 18px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; margin-bottom: 20px;
    }
    .labs-strip .lab-row { display: flex; flex-wrap: wrap; gap: 24px; align-items: center; margin-top: 8px; }
    .labs-strip .lab-item { display: flex; flex-direction: column; }
    .labs-strip .lab-label { color: #95A5A6 !important; font-size: 0.72rem; display: block; margin-bottom: 2px; }
    .labs-strip .lab-value { color: #1ABC9C !important; font-weight: 500; }

    .step-bar { display: flex; gap: 6px; margin-bottom: 20px; }
    .step-pip { height: 6px; flex: 1; border-radius: 3px; background: #2C3E50; }
    .step-pip.done { background: #27AE60; }
    .step-pip.active { background: #E67E22; }

    .question-card { background: #1E2E42; border: 1px solid #2C3E50; border-radius: 10px; padding: 22px 26px; margin-bottom: 16px; }
    .question-number { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #E67E22 !important; margin-bottom: 8px; }
    .question-text { font-size: 1.05rem; font-weight: 500; line-height: 1.5; }

    .stRadio > label { display: none; }
    div[data-testid="stRadio"] > div { gap: 8px !important; }
    div[data-testid="stRadio"] label { background: #1E2E42 !important; border: 1px solid #2C3E50 !important; border-radius: 8px !important; padding: 12px 16px !important; width: 100% !important; color: #ECF0F1 !important; }
    div[data-testid="stRadio"] label:hover { border-color: #16A085 !important; }

    div.stButton > button { background: #16A085 !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 10px 24px !important; width: 100% !important; }
    div.stButton > button:hover { background: #1ABC9C !important; }

    .opt-explain { font-size: 0.9rem; border-radius: 8px; padding: 12px 16px; margin: 6px 0; line-height: 1.65; }
    .opt-correct { background: rgba(39,174,96,0.14); border: 1px solid #27AE60; border-left: 4px solid #27AE60; color: #ECF0F1 !important; }
    .opt-wrong { background: rgba(231,76,60,0.12); border: 1px solid #E74C3C; border-left: 4px solid #E74C3C; color: #ECF0F1 !important; }
    .opt-explain strong { color: inherit !important; }

    .score-box { background: #1E2E42; border: 1px solid #2C3E50; border-radius: 10px; padding: 20px 24px; text-align: center; margin-bottom: 16px; }
    .score-number { font-size: 2.8rem; font-weight: 700; color: #1ABC9C !important; }
    .score-label { color: #95A5A6 !important; font-size: 0.85rem; }

    .complete-banner { background: linear-gradient(135deg, rgba(39,174,96,0.18), rgba(26,188,156,0.1)); border: 1px solid #1ABC9C; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 24px; }
    .complete-banner h2 { color: #1ABC9C !important; font-size: 1.5rem !important; }

    .stat-pill { background: #1E2E42; border: 1px solid #2C3E50; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
    .stat-pill .s-label { font-size: 0.8rem; color: #95A5A6 !important; }
    .stat-pill .s-value { font-size: 0.95rem; font-weight: 600; color: #1ABC9C !important; }

    .topic-badge { display: inline-block; background: rgba(22,160,133,0.18); border: 1px solid rgba(22,160,133,0.4); border-radius: 20px; padding: 3px 10px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: #1ABC9C !important; margin-bottom: 10px; }

    hr { border-color: #2C3E50 !important; }
    [data-testid="stMarkdownContainer"] { color: #ECF0F1; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #1A2638; }
    ::-webkit-scrollbar-thumb { background: #2C3E50; border-radius: 3px; }
    .streamlit-expanderHeader { background-color: #1E2E42 !important; color: #ECF0F1 !important; border-color: #2C3E50 !important; }
    .streamlit-expanderContent { background-color: #1E2E42 !important; border-color: #2C3E50 !important; }
</style>
""", unsafe_allow_html=True)


def md_to_html(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = text.replace('\n\n', '<br><br>').replace('\n', ' ')
    return text


# ===============================
# SESSION STATE
# ===============================
defaults = {
    "step": 0,
    "case_choice": None,
    "answered": False,
    "feedback": None,
    "scores": {},
    "current_labs": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def get_score_for_case(case_id):
    return st.session_state.scores.get(case_id, {"correct": 0, "total": 0})


def total_score():
    c = sum(v["correct"] for v in st.session_state.scores.values())
    t = sum(v["total"] for v in st.session_state.scores.values())
    return c, t


# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("## 🩺 Acid-Base Simulator")
    st.markdown("---")

    correct_total, attempted_total = total_score()
    pct = int(correct_total / attempted_total * 100) if attempted_total else 0

    st.markdown("### 📊 Session Stats")
    st.markdown(f"""
    <div class="stat-pill"><span class="s-label">Questions Answered</span><span class="s-value">{attempted_total}</span></div>
    <div class="stat-pill"><span class="s-label">Correct Answers</span><span class="s-value">{correct_total}</span></div>
    <div class="stat-pill"><span class="s-label">Overall Accuracy</span><span class="s-value">{pct}%</span></div>
    """, unsafe_allow_html=True)

    if st.session_state.case_choice:
        case_id = st.session_state.case_choice
        cs = get_score_for_case(case_id)
        active_case = CASES_DATA[case_id]
        total_steps = len(active_case["steps"])
        st.markdown("---")
        st.markdown("### 📋 Current Case")
        st.markdown(f"""
        <div class="stat-pill"><span class="s-label">Case</span><span class="s-value">{active_case['button_label']}</span></div>
        <div class="stat-pill"><span class="s-label">Correct / Total</span><span class="s-value">{cs['correct']} / {cs['total']}</span></div>
        <div class="stat-pill"><span class="s-label">Progress</span><span class="s-value">Step {min(st.session_state.step + 1, total_steps)} / {total_steps}</span></div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗂️ Case Index")
    for case_id, case in CASES_DATA.items():
        sc = get_score_for_case(case_id)
        steps_total = len(case["steps"])
        done = sc["total"] >= steps_total
        dot = "🟢" if done else ("🔵" if sc["total"] > 0 else "⚪")
        if st.button(f"{dot} {case['button_label']}", key=f"sidebar_{case_id}"):
            st.session_state.case_choice = case_id
            st.session_state.current_labs = CASES_DATA[case_id].get("initial_labs", {}).copy()
            st.session_state.step = 0
            st.session_state.answered = False
            st.session_state.feedback = None
            st.rerun()

    st.markdown("---")
    if st.button("🏠 Main Menu", key="sidebar_home"):
        st.session_state.case_choice = None
        st.session_state.step = 0
        st.session_state.answered = False
        st.session_state.feedback = None
        st.rerun()

# ===============================
# MAIN CONTENT
# ===============================
st.markdown("""
<div class="app-header">
    <h1>Acid-Base Bedside Simulator</h1>
    <p>Six patients, one algorithm. Work each case through the same six steps -- pH, primary disorder, anion gap, corrected bicarbonate, compensation, clinical correlation.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.case_choice:
    st.markdown("## Choose a case to begin")
    cols = st.columns(3)
    for i, (case_id, case) in enumerate(CASES_DATA.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="vignette-box" style="min-height:120px; display:flex; align-items:center; justify-content:center;">
                <h4 style="margin:0; font-size:1.3rem;">{case['button_label']}</h4>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start {case['button_label']}", key=f"start_{case_id}"):
                st.session_state.case_choice = case_id
                st.session_state.current_labs = case.get("initial_labs", {}).copy()
                st.session_state.step = 0
                st.session_state.answered = False
                st.session_state.feedback = None
                st.rerun()

    with st.expander("📖 Reference: every formula used in this simulator"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
**Normal values**
- pH 7.36–7.44 · PCO2 36–44 mmHg · HCO3 22–26 mEq/L
- Anion Gap = Na − (Cl + HCO3), normal ≈ 12 ± 2

**Metabolic acidosis (Winter's formula)**
- `Expected PCO2 = 1.5 × HCO3 + 8 (±2)`

**Corrected bicarbonate (if AG > 12)**
- `Corrected HCO3 = measured HCO3 + (AG − 12)`
- = 24 → pure high-AG acidosis
- > 24 → co-existing metabolic alkalosis
- < 24 → co-existing non-AG acidosis
            """)
        with c2:
            st.markdown("""
**Metabolic alkalosis**
- `Expected PCO2 = 0.8 × ΔHCO3 + 40 (±2)`, ΔHCO3 = HCO3 − 24

**Respiratory acidosis** (per 10 mmHg PCO2 rise)
- Acute: HCO3 rises ~1 mEq/L · Chronic: HCO3 rises ~3–4 mEq/L

**Respiratory alkalosis** (per 10 mmHg PCO2 fall)
- Acute: HCO3 falls ~2 mEq/L · Chronic: HCO3 falls ~4–5 mEq/L

**MUDPILES — high anion gap causes**
Methanol · Uremia · DKA · Propylene glycol · Isoniazid/Iron · Lactic acidosis · Ethylene glycol · Salicylates
            """)

else:
    case_id = st.session_state.case_choice
    active_case = CASES_DATA[case_id]
    step_idx = st.session_state.step
    total_steps = len(active_case["steps"])

    st.markdown(f"### {active_case['button_label']}: {active_case['title']}")

    pip_html = '<div class="step-bar">'
    for i in range(total_steps):
        cls = "done" if i < step_idx else ("active" if i == step_idx else "")
        pip_html += f'<div class="step-pip {cls}"></div>'
    pip_html += '</div>'
    st.markdown(pip_html, unsafe_allow_html=True)

    with st.expander("📄 Clinical Vignette", expanded=(step_idx == 0)):
        st.markdown(f'<div class="vignette-box">{active_case["vignette"]}</div>', unsafe_allow_html=True)

    lab_items = "".join([
        f'<div class="lab-item"><span class="lab-label">{k}</span><span class="lab-value">{v}</span></div>'
        for k, v in st.session_state.current_labs.items()
    ])
    st.markdown(f'<div class="labs-strip"><strong style="color:#95A5A6;font-size:0.78rem;">🧪 LABS &amp; ABG</strong><div class="lab-row">{lab_items}</div></div>', unsafe_allow_html=True)

    if step_idx >= total_steps:
        cs = get_score_for_case(case_id)
        pct_case = int(cs["correct"] / cs["total"] * 100) if cs["total"] else 0
        grade = "🏆 Excellent" if pct_case >= 80 else ("👍 Good" if pct_case >= 60 else "📚 Review Recommended")
        st.markdown(f"""
        <div class="complete-banner">
            <h2>✅ Case Complete!</h2>
            <p style="font-size:1.1rem;color:#ECF0F1;">You scored <strong style="color:#1ABC9C;">{cs['correct']} / {cs['total']}</strong> ({pct_case}%) — {grade}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="vignette-box"><strong style="color:#1ABC9C;">Final interpretation:</strong> {active_case["final_dx"]}<br><br><strong>Teaching pearl —</strong> {active_case["pearl"]}</div>', unsafe_allow_html=True)
        st.balloons()

        case_keys = list(CASES_DATA.keys())
        cur_pos = case_keys.index(case_id)
        if cur_pos < len(case_keys) - 1:
            if st.button("Next Case →"):
                nxt = case_keys[cur_pos + 1]
                st.session_state.case_choice = nxt
                st.session_state.current_labs = CASES_DATA[nxt].get("initial_labs", {}).copy()
                st.session_state.step = 0
                st.session_state.answered = False
                st.session_state.feedback = None
                st.rerun()
        else:
            if st.button("Restart from Case 1"):
                st.session_state.case_choice = case_keys[0]
                st.session_state.current_labs = CASES_DATA[case_keys[0]].get("initial_labs", {}).copy()
                st.session_state.step = 0
                st.session_state.answered = False
                st.session_state.feedback = None
                st.rerun()
    else:
        current_step = active_case["steps"][step_idx]

        st.markdown(f"""
        <div class="question-card">
            <div class="question-number">Question {step_idx + 1} of {total_steps}</div>
            <div class="question-text">{current_step['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        ans = st.radio("Select your answer:", current_step["options"], key=f"radio_{case_id}_{step_idx}", index=None)

        col_submit, col_next = st.columns([1, 1])

        with col_submit:
            if st.button("✅ Submit Answer", key=f"submit_{case_id}_{step_idx}", disabled=st.session_state.answered or ans is None):
                selected_idx = current_step["options"].index(ans)
                is_correct = (selected_idx == current_step["correct_idx"])

                # Score tracking — only count the first attempt per question
                if case_id not in st.session_state.scores:
                    st.session_state.scores[case_id] = {"correct": 0, "total": 0}
                if st.session_state.feedback is None:
                    st.session_state.scores[case_id]["total"] += 1
                    if is_correct:
                        st.session_state.scores[case_id]["correct"] += 1

                # Show only the explanation for the option the student picked
                exp_html = md_to_html(current_step["explanations"][selected_idx])
                st.session_state.feedback = ("correct" if is_correct else "wrong", ans, exp_html)

                # Only lock submission if correct; a wrong answer allows a retry
                if is_correct:
                    st.session_state.answered = True
                st.rerun()

        with col_next:
            if st.session_state.answered and step_idx < total_steps - 1:
                if st.button("Next Question ➡️", key=f"next_{case_id}_{step_idx}"):
                    st.session_state.step += 1
                    st.session_state.answered = False
                    st.session_state.feedback = None
                    st.rerun()
            elif st.session_state.answered and step_idx == total_steps - 1:
                if st.button("Finish Case 🏁", key=f"finish_{case_id}_{step_idx}"):
                    st.session_state.step += 1
                    st.session_state.answered = False
                    st.session_state.feedback = None
                    st.rerun()

        # Feedback for the selected answer only
        if st.session_state.feedback:
            kind, chosen, exp_html = st.session_state.feedback
            if kind == "correct":
                st.markdown(f'<div class="opt-explain opt-correct">✅ <strong>{chosen}</strong><br>{exp_html}</div>', unsafe_allow_html=True)
                if current_step["svg_html"]:
                    components.html(current_step["svg_html"], height=current_step["svg_height"], scrolling=True)
            else:
                st.markdown(f'<div class="opt-explain opt-wrong">❌ <strong>{chosen}</strong><br>{exp_html}</div>', unsafe_allow_html=True)
                st.markdown('<p style="color:#E67E22;font-size:0.85rem;margin-top:8px;">Review the explanation above and try again.</p>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("↩️ Return to Main Menu"):
        st.session_state.case_choice = None
        st.session_state.step = 0
        st.session_state.answered = False
        st.session_state.feedback = None