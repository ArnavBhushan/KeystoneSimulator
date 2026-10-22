import streamlit as st
import streamlit.components.v1 as components
import os
import math

import math

ARROW_DEFS = '<defs><marker id="ah" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#7B9BAE"/></marker><marker id="aht" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#0F9E8E"/></marker><marker id="aha" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#E6A817"/></marker><marker id="ahr" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#C0392B"/></marker></defs>'

def svg_wrap(inner, width=800, height=280, title="", subtitle=""):
    header = ""
    if title:
        header += f'<text x="{width//2}" y="24" text-anchor="middle" font-family="Inter,sans-serif" font-size="14" font-weight="600" fill="#E8F0F5">{title}</text>'
    if subtitle:
        header += f'<text x="{width//2}" y="42" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE">{subtitle}</text>'
    offset = 50 if (title or subtitle) else 0
    # Extra bottom padding so nothing clips
    total_h = height + offset + 100
    # SVG scales to fill full width; rendered pixel height = screen_width * (total_h/width)
    # Use a fixed generous screen_width assumption of 800px so iframe is always tall enough
    rendered_h = int(800 * total_h / width)
    svg = f'<svg viewBox="0 0 {width} {total_h}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet" style="width:100%;display:block;"><rect width="{width}" height="{total_h}" fill="#0D1B2A" rx="8"/>{header}<g transform="translate(0,{offset})">{inner}</g></svg>'
    html = f'<!DOCTYPE html><html><head><style>html,body{{margin:0;padding:0;background:#0D1B2A;}}div{{background:#0D1B2A;border:1px solid #1E3448;border-radius:10px;}}</style></head><body><div>{svg}</div></body></html>'
    # Add generous buffer; scrolling=True in components.html handles any overflow
    iframe_h = rendered_h + 60
    return html, iframe_h

# ─────────────────────────────────────────────────────────────────
# 1. SERUM OSMOLALITY — three branches of hyponatremia
# ─────────────────────────────────────────────────────────────────
def svg_serum_osm_branches():
    W, H = 800, 330
    inner = f"""{ARROW_DEFS}
  <!-- Draw lines FIRST so boxes render on top -->
  <line x1="400" y1="60" x2="400" y2="88" stroke="#7B9BAE" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="335" y1="116" x2="155" y2="168" stroke="#7B9BAE" stroke-width="1.8" marker-end="url(#ah)"/>
  <line x1="400" y1="128" x2="400" y2="168" stroke="#7B9BAE" stroke-width="1.8" marker-end="url(#ah)"/>
  <line x1="465" y1="116" x2="645" y2="168" stroke="#7B9BAE" stroke-width="1.8" marker-end="url(#ah)"/>
  <line x1="137" y1="236" x2="137" y2="264" stroke="#0F9E8E" stroke-width="2" marker-end="url(#aht)"/>

  <!-- Branch labels (on lines, before boxes) -->
  <text x="215" y="155" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">&lt; 275 mOsm/kg</text>
  <text x="400" y="155" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">275–295</text>
  <text x="582" y="155" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">&gt; 295 mOsm/kg</text>
  <text x="418" y="76" text-anchor="start" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Step 1</text>

  <!-- Na box -->
  <rect x="305" y="18" width="190" height="42" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2.5"/>
  <text x="400" y="44" text-anchor="middle" font-family="Inter,sans-serif" font-size="14" fill="#0F9E8E" font-weight="700">Na&#x207a; &lt; 135 mEq/L</text>

  <!-- Check plasma osm box -->
  <rect x="280" y="88" width="240" height="40" rx="8" fill="#E6A817"/>
  <text x="400" y="113" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#0D1B2A" font-weight="700">Check Plasma Osmolality</text>

  <!-- Three result boxes — drawn AFTER lines -->
  <rect x="26" y="168" width="220" height="68" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2.5"/>
  <text x="136" y="192" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#0F9E8E" font-weight="700">HYPOTONIC</text>
  <text x="136" y="210" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">True hyponatremia</text>
  <text x="136" y="228" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">&#8594; Continue algorithm</text>

  <rect x="290" y="168" width="220" height="68" rx="8" fill="#0D1B2A" stroke="#7B9BAE" stroke-width="1.8"/>
  <text x="400" y="192" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#7B9BAE" font-weight="700">ISOTONIC</text>
  <text x="400" y="210" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Pseudohyponatremia</text>
  <text x="400" y="228" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">High lipids / proteins</text>

  <rect x="554" y="168" width="220" height="68" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="2"/>
  <text x="664" y="192" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#C0392B" font-weight="700">HYPERTONIC</text>
  <text x="664" y="210" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Osmotic shift</text>
  <text x="664" y="228" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Glucose / Mannitol &#8593;</text>

  <!-- Next step box -->
  <rect x="26" y="264" width="220" height="38" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.8"/>
  <text x="136" y="287" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="600">&#8594; Check Urine Osm (ADH status)</text>
    """
    return svg_wrap(inner, W, H, "Step 1: Plasma Osmolality — Three Types of Hyponatremia", "Low osm = true dilution.  Normal osm = artifact.  High osm = osmotic shift.")


def svg_adh_triggers():
    W, H = 800, 310
    inner = f"""{ARROW_DEFS}
  <!-- Lines first -->
  <line x1="230" y1="75" x2="335" y2="138" stroke="#0F9E8E" stroke-width="2" marker-end="url(#aht)"/>
  <line x1="660" y1="75" x2="465" y2="138" stroke="#E6A817" stroke-width="2" marker-end="url(#aha)"/>
  <line x1="400" y1="180" x2="400" y2="222" stroke="#7B9BAE" stroke-width="2" marker-end="url(#ah)"/>

  <!-- Osmotic trigger box -->
  <rect x="26" y="20" width="210" height="90" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2"/>
  <text x="131" y="46" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#0F9E8E" font-weight="700">Osmotic Trigger</text>
  <text x="131" y="66" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Plasma osm &gt; 285–290</text>
  <text x="131" y="82" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Hypothalamic osmoreceptors</text>
  <text x="131" y="98" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">detect high solute conc.</text>

  <!-- Hemodynamic trigger box -->
  <rect x="560" y="20" width="215" height="90" rx="8" fill="#0D1B2A" stroke="#E6A817" stroke-width="2"/>
  <text x="667" y="46" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#E6A817" font-weight="700">Hemodynamic Trigger</text>
  <text x="667" y="66" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Low EABV / BP drop</text>
  <text x="667" y="82" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Baroreceptors detect</text>
  <text x="667" y="98" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">low perfusion pressure</text>

  <!-- ADH Released box -->
  <rect x="278" y="138" width="244" height="42" rx="8" fill="#0D1B2A" stroke="#E8F0F5" stroke-width="2.5"/>
  <text x="400" y="156" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#E8F0F5" font-weight="700">ADH Released</text>
  <text x="400" y="173" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Posterior pituitary &#8594; bloodstream</text>

  <!-- Kidney box -->
  <rect x="265" y="222" width="270" height="42" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2"/>
  <text x="400" y="241" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#0F9E8E" font-weight="600">Collecting Duct: AQP2 inserted</text>
  <text x="400" y="257" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Water reabsorbed &#8594; concentrated urine &#8593;</text>

  <!-- Key insight box -->
  <rect x="26" y="200" width="218" height="64" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="1.5"/>
  <text x="135" y="220" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="700">Key Insight</text>
  <text x="135" y="238" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Volume trumps tonicity.</text>
  <text x="135" y="254" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Hypovolemia activates ADH</text>
  <text x="135" y="270" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">even when plasma osm is LOW.</text>

  <!-- Urine Osm box -->
  <rect x="556" y="200" width="218" height="64" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.5"/>
  <text x="665" y="220" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="700">Urine Osm Guide</text>
  <text x="665" y="238" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">ADH ON: urine osm &gt; 285</text>
  <text x="665" y="254" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">ADH OFF: urine osm &lt; 100</text>
  <text x="665" y="270" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Borderline: 100–285</text>
    """
    return svg_wrap(inner, W, H, "ADH: Two Physiologic Triggers", "ADH responds to osmotic OR hemodynamic signals — whichever is stronger wins.")


def svg_volume_status():
    W, H = 800, 320
    inner = f"""{ARROW_DEFS}
  <!-- HYPOVOLEMIC -->
  <rect x="16" y="10" width="244" height="292" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="2"/>
  <text x="138" y="36" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#C0392B" font-weight="700">HYPOVOLEMIC</text>
  <text x="138" y="54" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Low total body Na + water</text>
  <line x1="26" y1="62" x2="250" y2="62" stroke="#1E3448" stroke-width="1"/>
  <text x="30" y="80" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Dry mucous membranes</text>
  <text x="30" y="96" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Orthostatic hypotension</text>
  <text x="30" y="112" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Tachycardia</text>
  <text x="30" y="128" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Dark concentrated urine</text>
  <text x="30" y="144" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; BUN/Cr &gt; 20</text>
  <line x1="26" y1="155" x2="250" y2="155" stroke="#1E3448" stroke-width="1"/>
  <text x="138" y="172" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">ADH: ON &#10003; (appropriate)</text>
  <text x="138" y="188" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">RAAS: ON &#10003; (urine Na &lt;20)</text>
  <text x="138" y="208" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Causes: vomiting, diarrhea,</text>
  <text x="138" y="222" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">diuretics, GI losses</text>
  <line x1="26" y1="232" x2="250" y2="232" stroke="#1E3448" stroke-width="1"/>
  <rect x="30" y="242" width="180" height="44" rx="6" fill="rgba(192,57,43,0.2)" stroke="#C0392B" stroke-width="1"/>
  <text x="120" y="260" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">Tx: Isotonic saline</text>
  <text x="120" y="278" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">restores volume &#8594; turns off ADH</text>

  <!-- EUVOLEMIC -->
  <rect x="278" y="10" width="244" height="292" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2"/>
  <text x="400" y="36" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#0F9E8E" font-weight="700">EUVOLEMIC</text>
  <text x="400" y="54" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Normal total body sodium</text>
  <line x1="288" y1="62" x2="512" y2="62" stroke="#1E3448" stroke-width="1"/>
  <text x="292" y="80" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Moist mucous membranes</text>
  <text x="292" y="96" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Normal blood pressure</text>
  <text x="292" y="112" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Normal HR</text>
  <text x="292" y="128" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; No edema, no JVD</text>
  <text x="292" y="144" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Normal skin turgor</text>
  <line x1="288" y1="155" x2="512" y2="155" stroke="#1E3448" stroke-width="1"/>
  <text x="400" y="172" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">ADH: ON &#10007; (inappropriate)</text>
  <text x="400" y="188" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="600">RAAS: OFF (urine Na &gt;20)</text>
  <text x="400" y="208" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Causes: SIADH, hypothyroidism,</text>
  <text x="400" y="222" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">adrenal insufficiency</text>
  <line x1="288" y1="232" x2="512" y2="232" stroke="#1E3448" stroke-width="1"/>
  <rect x="292" y="242" width="180" height="44" rx="6" fill="rgba(15,158,142,0.2)" stroke="#0F9E8E" stroke-width="1"/>
  <text x="382" y="260" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="600">Tx: Fluid restriction</text>
  <text x="382" y="278" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">+/- tolvaptan</text>

  <!-- HYPERVOLEMIC -->
  <rect x="540" y="10" width="244" height="292" rx="8" fill="#0D1B2A" stroke="#E6A817" stroke-width="2"/>
  <text x="662" y="36" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#E6A817" font-weight="700">HYPERVOLEMIC</text>
  <text x="662" y="54" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">High TBNa+H&#8322;O, low EABV</text>
  <line x1="550" y1="62" x2="774" y2="62" stroke="#1E3448" stroke-width="1"/>
  <text x="554" y="80" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Peripheral edema 2+</text>
  <text x="554" y="96" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Elevated JVP</text>
  <text x="554" y="112" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Bibasilar crackles</text>
  <text x="554" y="128" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Ascites (cirrhosis)</text>
  <text x="554" y="144" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">&#8226; Weight gain</text>
  <line x1="550" y1="155" x2="774" y2="155" stroke="#1E3448" stroke-width="1"/>
  <text x="662" y="172" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">ADH: ON (low EABV signal)</text>
  <text x="662" y="188" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">RAAS: ON (urine Na &lt;20)</text>
  <text x="662" y="208" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Causes: CHF, cirrhosis,</text>
  <text x="662" y="222" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">nephrotic syndrome</text>
  <line x1="550" y1="232" x2="774" y2="232" stroke="#1E3448" stroke-width="1"/>
  <rect x="554" y="242" width="180" height="44" rx="6" fill="rgba(230,168,23,0.2)" stroke="#E6A817" stroke-width="1"/>
  <text x="644" y="260" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E6A817" font-weight="600">Tx: Loop diuretic</text>
  <text x="644" y="278" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">+ treat underlying cause</text>
    """
    return svg_wrap(inner, W, H, "Step 3: Volume Status — The Three Categories", "")


def svg_raas_cascade():
    W, H = 800, 290
    # Draw all lines first, then boxes on top
    boxes = [
        (60,  110, 130, 52, "#C0392B", "Low EABV\n/ Low BP",        "SENSOR"),
        (212, 110, 130, 52, "#E6A817", "JG Cells\nRelease Renin",   "STEP 1"),
        (364, 110, 130, 52, "#E6A817", "Angio I\n&#8594; Angio II", "STEP 2"),
        (516, 110, 130, 52, "#0F9E8E", "Adrenal\nAldosterone",      "STEP 3"),
        (668, 110, 130, 52, "#0F9E8E", "Collect. Duct\nNa&#x207a; Reabs.", "RESULT"),
    ]
    lines = ""
    for i in range(len(boxes)-1):
        x1 = boxes[i][0] + boxes[i][2]
        x2 = boxes[i+1][0]
        y  = boxes[i][1] + 26
        lines += f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#7B9BAE" stroke-width="2" marker-end="url(#ah)"/>'

    box_svg = ""
    for bx, by, bw, bh, color, label, step in boxes:
        box_svg += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="7" fill="#0D1B2A" stroke="{color}" stroke-width="2"/>'
        box_svg += f'<text x="{bx+14}" y="{by-6}" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">{step}</text>'
        for j, ln in enumerate(label.split("\\n")):
            box_svg += f'<text x="{bx+bw//2}" y="{by+22+j*16}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="{color}" font-weight="600">{ln}</text>'

    inner = f"""{ARROW_DEFS}
  {lines}
  {box_svg}
  <!-- Result annotation -->
  <rect x="550" y="178" width="240" height="72" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.5"/>
  <text x="670" y="198" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="600">Urine Na Interpretation</text>
  <text x="670" y="216" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">RAAS ON &#8594; Urine Na &lt; 20 mEq/L</text>
  <text x="670" y="232" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Kidney conserves every Na&#x207a;</text>
  <text x="670" y="248" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">RAAS OFF &#8594; Urine Na &gt; 20 mEq/L</text>

  <rect x="10" y="178" width="240" height="72" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="1.5"/>
  <text x="130" y="198" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="600">CHF Paradox</text>
  <text x="130" y="216" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Total Na is HIGH</text>
  <text x="130" y="232" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">but RAAS is ON because</text>
  <text x="130" y="248" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">EABV is LOW &#8594; urine Na &lt;20</text>
    """
    return svg_wrap(inner, W, H, "Step 4: RAAS Cascade — Why Urine Na Reflects Aldosterone", "Urine Na is the functional readout of RAAS. Low = aldosterone active. High = RAAS off.")


def svg_eabv_chf():
    W, H = 800, 310
    inner = f"""{ARROW_DEFS}
  <!-- Lines first -->
  <line x1="278" y1="130" x2="372" y2="130" stroke="#7B9BAE" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="535" y1="100" x2="615" y2="78" stroke="#C0392B" stroke-width="2" marker-end="url(#ahr)"/>
  <line x1="535" y1="162" x2="615" y2="168" stroke="#C0392B" stroke-width="2" marker-end="url(#ahr)"/>
  <path d="M 692 226 Q 692 278 400 278 Q 200 278 200 208" stroke="#E6A817" stroke-width="2" fill="none" stroke-dasharray="6,3" marker-end="url(#aha)"/>

  <!-- Failing Heart box -->
  <rect x="46" y="82" width="230" height="96" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="2.5"/>
  <text x="161" y="106" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#C0392B" font-weight="700">Failing Heart</text>
  <text x="161" y="124" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Low cardiac output</text>
  <text x="161" y="140" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">&#8595; Forward flow</text>
  <text x="161" y="158" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">EABV is LOW</text>

  <!-- Total fluid label -->
  <rect x="26" y="210" width="330" height="34" rx="6" fill="#0D1B2A" stroke="#E6A817" stroke-width="1.8"/>
  <text x="191" y="231" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E6A817" font-weight="600">Total Body Fluid: HIGH (edema, JVD, crackles)</text>

  <!-- Baroreceptors box -->
  <rect x="374" y="104" width="160" height="56" rx="8" fill="#0D1B2A" stroke="#7B9BAE" stroke-width="1.8"/>
  <text x="454" y="126" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE" font-weight="700">Baroreceptors</text>
  <text x="454" y="142" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Carotid / Aortic arch</text>
  <text x="454" y="156" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Sense low perfusion</text>

  <!-- ADH box -->
  <rect x="616" y="46" width="162" height="52" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="1.8"/>
  <text x="697" y="68" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="700">ADH Released</text>
  <text x="697" y="84" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Urine osm &#8593; &#8594; H&#8322;O retained</text>

  <!-- RAAS box -->
  <rect x="616" y="148" width="162" height="52" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="1.8"/>
  <text x="697" y="170" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="700">RAAS Activated</text>
  <text x="697" y="186" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Urine Na &#8595; &#8594; Na&#x207a; retained</text>

  <!-- Vicious cycle label -->
  <text x="400" y="295" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E6A817">Vicious cycle: more retention &#8594; more congestion &#8594; worse pump &#8594; more retention</text>
    """
    return svg_wrap(inner, W, H, "CHF: Effective Arterial Blood Volume (EABV) Concept", "The kidney responds to EABV, not total body water. CHF fools the kidney into thinking it is hypovolemic.")


def svg_siadh_pattern():
    W, H = 800, 300
    inner = f"""{ARROW_DEFS}
  <!-- Lines first -->
  <line x1="196" y1="62" x2="244" y2="62" stroke="#C0392B" stroke-width="2" marker-end="url(#ahr)"/>
  <line x1="336" y1="84" x2="336" y2="128" stroke="#C0392B" stroke-width="2" marker-end="url(#ahr)"/>
  <line x1="336" y1="168" x2="336" y2="204" stroke="#7B9BAE" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="582" y1="90" x2="582" y2="128" stroke="#0F9E8E" stroke-width="2" marker-end="url(#aht)"/>

  <!-- Lung cancer box -->
  <rect x="18" y="30" width="176" height="64" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="2"/>
  <text x="106" y="54" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="700">Small Cell Ca.</text>
  <text x="106" y="70" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Ectopic ADH secretion</text>
  <text x="106" y="85" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">(paraneoplastic)</text>

  <!-- ADH ON box -->
  <rect x="246" y="38" width="180" height="46" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="2.5"/>
  <text x="336" y="60" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#C0392B" font-weight="700">ADH ON</text>
  <text x="336" y="77" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">No physiologic trigger</text>

  <!-- Urine osm box -->
  <rect x="246" y="128" width="180" height="40" rx="7" fill="#0D1B2A" stroke="#E6A817" stroke-width="1.8"/>
  <text x="336" y="148" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#E6A817" font-weight="600">Urine Osm: HIGH &#8593;</text>
  <text x="336" y="163" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Water retained &#8594; dilutes serum</text>

  <!-- Serum Na box -->
  <rect x="246" y="204" width="180" height="40" rx="7" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.8"/>
  <text x="336" y="224" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E">Serum Na: LOW</text>
  <text x="336" y="239" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Plasma osm &lt; 275 mOsm/kg</text>

  <!-- Euvolemic + RAAS OFF box -->
  <rect x="482" y="30" width="200" height="60" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2"/>
  <text x="582" y="52" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="700">Euvolemic Exam</text>
  <text x="582" y="68" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">No baroreceptor trigger</text>
  <text x="582" y="83" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#0F9E8E">&#8594; RAAS OFF</text>

  <!-- Urine Na box -->
  <rect x="482" y="128" width="200" height="40" rx="7" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2"/>
  <text x="582" y="150" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="700">Urine Na: HIGH &#8593;</text>
  <text x="582" y="165" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">RAAS OFF &#8594; Na freely excreted</text>

  <!-- SIADH signature box -->
  <rect x="18" y="204" width="200" height="60" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2"/>
  <text x="118" y="224" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="700">SIADH Signature</text>
  <text x="118" y="240" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E8F0F5">Low plasma osm + High urine osm</text>
  <text x="118" y="254" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E8F0F5">+ Euvolemic + High urine Na</text>

  <!-- Tx box -->
  <rect x="482" y="204" width="200" height="60" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.5"/>
  <text x="582" y="224" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="700">Treatment</text>
  <text x="582" y="240" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E8F0F5">Fluid restriction (500–1000 mL/day)</text>
  <text x="582" y="256" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Tolvaptan for refractory cases</text>
    """
    return svg_wrap(inner, W, H, "SIADH: Pathophysiology and Diagnostic Signature", "Ectopic ADH fires autonomously — no osmotic or hemodynamic trigger needed.")


def svg_polydipsia_math():
    W, H = 800, 300
    inner = f"""{ARROW_DEFS}
  <!-- Normal scenario -->
  <rect x="14" y="14" width="370" height="258" rx="8" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2"/>
  <text x="199" y="40" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#0F9E8E" font-weight="700">Normal Kidneys (reference)</text>
  <line x1="24" y1="50" x2="374" y2="50" stroke="#1E3448" stroke-width="1"/>
  <text x="30" y="72" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Daily solute intake (normal diet):</text>
  <text x="374" y="72" text-anchor="end" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="600">600–900 mOsm/day</text>
  <text x="30" y="94" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Min urine osm (ADH OFF):</text>
  <text x="374" y="94" text-anchor="end" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="600">~50 mOsm/kg</text>
  <text x="30" y="116" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Max free water excretion:</text>
  <text x="374" y="116" text-anchor="end" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="600">600 &#247; 50 = 12 L/day</text>
  <rect x="30" y="128" width="330" height="32" rx="5" fill="rgba(15,158,142,0.15)" stroke="#0F9E8E" stroke-width="1"/>
  <text x="195" y="148" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="600">Can handle up to ~12 L/day intake</text>
  <line x1="24" y1="172" x2="374" y2="172" stroke="#1E3448" stroke-width="1"/>
  <text x="199" y="194" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE">Formula: Max water excretion =</text>
  <rect x="60" y="204" width="260" height="36" rx="6" fill="rgba(15,158,142,0.1)" stroke="#0F9E8E" stroke-width="1"/>
  <text x="190" y="227" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#0F9E8E" font-weight="700">Daily Osmoles &#247; Min Urine Osm</text>
  <text x="199" y="258" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">ADH must be OFF to maximize excretion</text>

  <!-- Low solute scenario -->
  <rect x="416" y="14" width="370" height="258" rx="8" fill="#0D1B2A" stroke="#C0392B" stroke-width="2"/>
  <text x="601" y="40" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#C0392B" font-weight="700">Low Solute + Polydipsia</text>
  <line x1="426" y1="50" x2="776" y2="50" stroke="#1E3448" stroke-width="1"/>
  <text x="430" y="72" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Daily solute (poor diet):</text>
  <text x="776" y="72" text-anchor="end" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">~150 mOsm/day</text>
  <text x="430" y="94" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Min urine osm (ADH OFF):</text>
  <text x="776" y="94" text-anchor="end" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">~50 mOsm/kg</text>
  <text x="430" y="116" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Max free water excretion:</text>
  <text x="776" y="116" text-anchor="end" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">150 &#247; 50 = only 3 L/day</text>
  <rect x="430" y="128" width="330" height="32" rx="5" fill="rgba(192,57,43,0.15)" stroke="#C0392B" stroke-width="1"/>
  <text x="595" y="148" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#C0392B" font-weight="600">But drinks &gt;10 L/day &#8594; hyponatremia</text>
  <line x1="426" y1="172" x2="776" y2="172" stroke="#1E3448" stroke-width="1"/>
  <text x="601" y="194" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">ADH is OFF — kidneys doing everything right.</text>
  <text x="601" y="210" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">The problem is a math problem:</text>
  <text x="601" y="230" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="600">intake exceeds excretion capacity.</text>
  <text x="601" y="254" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Tx: Reduce intake + increase dietary solute</text>
    """
    return svg_wrap(inner, W, H, "Psychogenic Polydipsia: Why Low Solute Causes Hyponatremia", "Even with ADH OFF, insufficient solute limits the kidney's ability to excrete free water.")


def svg_urine_osm_adh():
    W, H = 800, 280
    inner = f"""{ARROW_DEFS}
  <!-- ADH OFF zone -->
  <rect x="40" y="50" width="150" height="44" rx="4" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2.5"/>
  <text x="115" y="76" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#0F9E8E" font-weight="700">ADH OFF</text>
  <!-- Borderline zone -->
  <rect x="190" y="50" width="150" height="44" fill="#0D1B2A" stroke="#7B9BAE" stroke-width="1.5"/>
  <text x="265" y="76" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#7B9BAE" font-weight="600">Borderline</text>
  <!-- ADH ON zone -->
  <rect x="340" y="50" width="420" height="44" rx="4" fill="#0D1B2A" stroke="#E6A817" stroke-width="2.5"/>
  <text x="550" y="76" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#E6A817" font-weight="700">ADH ON (concentrating)</text>

  <!-- Tick marks -->
  <line x1="190" y1="44" x2="190" y2="98" stroke="#7B9BAE" stroke-width="2"/>
  <text x="190" y="114" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE">100</text>
  <line x1="340" y1="44" x2="340" y2="98" stroke="#E6A817" stroke-width="2.5"/>
  <text x="340" y="114" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#E6A817" font-weight="700">285</text>
  <line x1="550" y1="94" x2="550" y2="98" stroke="#7B9BAE" stroke-width="1"/>
  <text x="550" y="114" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE">500</text>
  <line x1="720" y1="94" x2="720" y2="98" stroke="#7B9BAE" stroke-width="1"/>
  <text x="720" y="114" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE">800+</text>

  <!-- Axis label -->
  <text x="400" y="134" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#7B9BAE">Urine Osmolality (mOsm/kg)</text>

  <!-- Generic markers — no case spoilers -->
  <line x1="85" y1="94" x2="85" y2="150" stroke="#0F9E8E" stroke-width="2" stroke-dasharray="4,2"/>
  <rect x="20" y="152" width="130" height="44" rx="6" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.5"/>
  <text x="85" y="170" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#0F9E8E" font-weight="600">~50 mOsm/kg</text>
  <text x="85" y="186" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">e.g. polydipsia</text>

  <line x1="500" y1="94" x2="500" y2="150" stroke="#E6A817" stroke-width="2" stroke-dasharray="4,2"/>
  <rect x="380" y="152" width="240" height="44" rx="6" fill="#0D1B2A" stroke="#E6A817" stroke-width="1.5"/>
  <text x="500" y="170" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E6A817" font-weight="600">400-550 mOsm/kg</text>
  <text x="500" y="186" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">e.g. SIADH, CHF, hypovolemia</text>

  <!-- Bottom info boxes -->
  <rect x="20" y="210" width="260" height="58" rx="6" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.5"/>
  <text x="150" y="230" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="600">ADH OFF (urine osm &lt; 100)</text>
  <text x="150" y="247" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Kidneys diluting maximally</text>
  <text x="150" y="263" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">&#8594; ADH-independent pathway</text>

  <rect x="520" y="210" width="260" height="58" rx="6" fill="#0D1B2A" stroke="#E6A817" stroke-width="1.5"/>
  <text x="650" y="230" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#E6A817" font-weight="600">ADH ON (urine osm &gt; 285)</text>
  <text x="650" y="247" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">Kidneys concentrating urine</text>
  <text x="650" y="263" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">&#8594; Assess volume status next</text>
    """
    return svg_wrap(inner, W, H, "Step 2: Urine Osmolality — ADH Status", "Determines which branch of the algorithm to follow: ADH-dependent or independent.")


def svg_urine_na_comparison():
    W, H = 800, 280
    inner = f"""{ARROW_DEFS}
  <!-- Low zone -->
  <rect x="40" y="50" width="280" height="44" rx="4" fill="#0D1B2A" stroke="#C0392B" stroke-width="2.5"/>
  <text x="180" y="76" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#C0392B" font-weight="700">RAAS ON — Conserving Na&#x207a;</text>
  <!-- High zone -->
  <rect x="320" y="50" width="440" height="44" rx="4" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="2.5"/>
  <text x="540" y="76" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#0F9E8E" font-weight="700">RAAS OFF — Spilling Na&#x207a;</text>

  <!-- Cutoff line + label -->
  <line x1="320" y1="40" x2="320" y2="100" stroke="#E6A817" stroke-width="3"/>
  <text x="320" y="116" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#E6A817" font-weight="700">20 mEq/L cutoff</text>

  <!-- Axis -->
  <text x="400" y="138" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#7B9BAE">Urine Sodium (mEq/L)</text>
  <text x="60" y="138" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE">0</text>
  <text x="740" y="138" font-family="Inter,sans-serif" font-size="11" fill="#7B9BAE">60+</text>

  <!-- Generic markers — no case spoilers -->
  <line x1="130" y1="94" x2="130" y2="152" stroke="#C0392B" stroke-width="2" stroke-dasharray="4,2"/>
  <rect x="40" y="154" width="180" height="54" rx="6" fill="#0D1B2A" stroke="#C0392B" stroke-width="1.5"/>
  <text x="130" y="174" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="600">&lt; 20 mEq/L</text>
  <text x="130" y="190" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Hypovolemia</text>
  <text x="130" y="204" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">or low EABV (CHF)</text>

  <line x1="570" y1="94" x2="570" y2="152" stroke="#0F9E8E" stroke-width="2" stroke-dasharray="4,2"/>
  <rect x="480" y="154" width="180" height="54" rx="6" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.5"/>
  <text x="570" y="174" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="600">&gt; 20 mEq/L</text>
  <text x="570" y="190" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Euvolemia</text>
  <text x="570" y="204" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">(RAAS inactive)</text>

  <!-- Bottom boxes -->
  <rect x="20" y="220" width="340" height="50" rx="6" fill="#0D1B2A" stroke="#C0392B" stroke-width="1.5"/>
  <text x="190" y="240" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#C0392B" font-weight="600">Urine Na &lt; 20 = RAAS ON</text>
  <text x="190" y="256" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Hypovolemia OR low EABV (CHF/cirrhosis/nephrotic)</text>

  <rect x="440" y="220" width="340" height="50" rx="6" fill="#0D1B2A" stroke="#0F9E8E" stroke-width="1.5"/>
  <text x="610" y="240" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#0F9E8E" font-weight="600">Urine Na &gt; 20 = RAAS OFF</text>
  <text x="610" y="256" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Euvolemia (SIADH) OR renal salt wasting</text>
    """
    return svg_wrap(inner, W, H, "Step 4: Urine Sodium — RAAS Activity", "The 20 mEq/L threshold separates aldosterone-driven Na retention from free excretion.")


def svg_final_summary():
    W, H = 800, 310
    patterns = [
        ("Hypovolemic",        "#C0392B", "ADH ON",  "RAAS ON",  "Urine osm > 285", "Urine Na < 20", "Tx: Isotonic saline"),
        ("Hypervolemic\n(low EABV)", "#E6A817", "ADH ON",  "RAAS ON",  "Urine osm > 285", "Urine Na < 20", "Tx: Loop diuretic"),
        ("Euvolemic\n(SIADH)", "#0F9E8E", "ADH ON",  "RAAS OFF", "Urine osm > 285", "Urine Na > 20", "Tx: Fluid restrict"),
        ("ADH-Independent",    "#7B9BAE", "ADH OFF", "RAAS OFF", "Urine osm < 100", "Urine Na < 20", "Tx: Reduce intake"),
    ]
    inner = ARROW_DEFS
    for i, (vol, color, adh, raas, uosm, una, tx) in enumerate(patterns):
        x = 12 + i * 196
        inner += f'<rect x="{x}" y="10" width="184" height="290" rx="8" fill="#0D1B2A" stroke="{color}" stroke-width="2"/>'
        for j, line in enumerate(vol.split("\n")):
            inner += f'<text x="{x+92}" y="{34+j*16}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="{color}" font-weight="700">{line}</text>'
        inner += f'<line x1="{x+10}" y1="68" x2="{x+174}" y2="68" stroke="#1E3448" stroke-width="1"/>'
        adh_c = "#C0392B" if adh == "ADH ON" else "#0F9E8E"
        raas_c = "#C0392B" if raas == "RAAS ON" else "#0F9E8E"
        inner += f'<text x="{x+92}" y="88" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#7B9BAE">Plasma Osm: LOW</text>'
        inner += f'<text x="{x+92}" y="108" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="{adh_c}" font-weight="600">{adh}</text>'
        inner += f'<text x="{x+92}" y="126" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">{uosm}</text>'
        inner += f'<text x="{x+92}" y="146" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="{raas_c}" font-weight="600">{raas}</text>'
        inner += f'<text x="{x+92}" y="164" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E8F0F5">{una}</text>'
        inner += f'<line x1="{x+10}" y1="176" x2="{x+174}" y2="176" stroke="#1E3448" stroke-width="1"/>'
        inner += f'<rect x="{x+12}" y="184" width="162" height="32" rx="5" fill="rgba(22,37,53,0.6)" stroke="{color}" stroke-width="1"/>'
        inner += f'<text x="{x+93}" y="204" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="{color}" font-weight="600">{tx}</text>'
        inner += f'<line x1="{x+10}" y1="224" x2="{x+174}" y2="224" stroke="#1E3448" stroke-width="1"/>'
        inner += f'<text x="{x+92}" y="246" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#7B9BAE">Pattern — not case-specific</text>'
    return svg_wrap(inner, W, H, "Hyponatremia Patterns: Hormonal Signatures", "Four diagnostic patterns — compare ADH/RAAS status to understand each type.")


DIAGRAMS = {
    "serum_osm_branches": svg_serum_osm_branches,
    "adh_triggers":       svg_adh_triggers,
    "urine_osm_adh":      svg_urine_osm_adh,
    "volume_status":      svg_volume_status,
    "raas_cascade":       svg_raas_cascade,
    "urine_na_comparison":svg_urine_na_comparison,
    "eabv_chf":           svg_eabv_chf,
    "siadh_pattern":      svg_siadh_pattern,
    "polydipsia_math":    svg_polydipsia_math,
    "final_summary":      svg_final_summary,
}


# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Hyponatremia Simulator",
    layout="wide",
    page_icon="💧",
    initial_sidebar_state="expanded"
)

# ===============================
# THEME CSS
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --navy:       #0D1B2A;
        --navy-mid:   #1B2D3E;
        --teal:       #0F9E8E;
        --teal-light: #1BBCAB;
        --amber:      #E6A817;
        --crimson:    #C0392B;
        --slate:      #2E4A5E;
        --card:       #162535;
        --border:     #1E3448;
        --text:       #E8F0F5;
        --muted:      #7B9BAE;
        --success:    #27AE60;
        --error:      #C0392B;
    }

    html, body, .stApp {
        background-color: var(--navy) !important;
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: var(--navy-mid) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * { color: var(--text) !important; }

    p, li, label, div, span { color: var(--text); }
    h1, h2, h3, h4, h5 { color: var(--text) !important; font-weight: 600; }

    /* Header banner */
    .app-header {
        background: linear-gradient(135deg, #0A4D6E 0%, #0D1B2A 65%);
        padding: 28px 36px 22px;
        border-radius: 14px;
        margin-bottom: 28px;
        border: 1px solid var(--teal);
        position: relative;
        overflow: hidden;
    }
    .app-header::before {
        content: "💧";
        position: absolute; right: 28px; top: 50%;
        transform: translateY(-50%);
        font-size: 80px; opacity: 0.12;
    }
    .app-header h1 { font-size: 2rem !important; font-weight: 700 !important; margin: 0 0 6px !important; letter-spacing: -0.5px; }
    .app-header p { color: rgba(232,240,245,0.72) !important; font-size: 0.92rem; margin: 0; }

    /* Case cards */
    .case-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 10px;
        transition: border-color 0.2s;
        cursor: pointer;
    }
    .case-card:hover { border-color: var(--teal); }
    .case-card h4 { margin: 0 0 6px; font-size: 1rem; }
    .case-card p { color: var(--muted) !important; font-size: 0.82rem; margin: 0; }

    /* Vignette */
    .vignette-box {
        background: var(--card);
        border: 1px solid var(--border);
        border-left: 4px solid var(--teal);
        border-radius: 10px;
        padding: 22px 26px;
        font-size: 0.94rem;
        line-height: 1.8;
        margin-bottom: 18px;
    }

    /* Labs strip */
    .labs-strip {
        background: var(--navy-mid);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px 20px;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 18px;
    }
    .labs-strip .lab-header { color: var(--muted) !important; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px; display: block; }
    .labs-strip .lab-row { display: flex; flex-wrap: wrap; gap: 20px; }
    .labs-strip .lab-item { display: flex; flex-direction: column; }
    .labs-strip .lab-label { color: var(--muted) !important; font-size: 0.7rem; margin-bottom: 2px; display: block; }
    .labs-strip .lab-value { color: var(--teal-light) !important; font-size: 0.95rem; font-weight: 500; }
    .labs-strip .lab-value.abnormal { color: var(--amber) !important; }

    /* Step progress */
    .step-bar { display: flex; gap: 5px; margin-bottom: 22px; }
    .step-pip { height: 5px; flex: 1; border-radius: 3px; background: var(--border); }
    .step-pip.done { background: var(--success); }
    .step-pip.active { background: var(--teal); }

    /* Algorithm badge */
    .algo-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(15,158,142,0.15); border: 1px solid var(--teal);
        border-radius: 20px; padding: 4px 12px;
        font-size: 0.75rem; font-weight: 600;
        color: var(--teal-light) !important; margin-bottom: 12px;
    }

    /* Question card */
    .question-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 16px;
    }
    .question-num { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--teal) !important; margin-bottom: 8px; display: block; }
    .question-text { font-size: 1.05rem; font-weight: 500; line-height: 1.5; }

    /* Radio */
    .stRadio > label { display: none; }
    div[data-testid="stRadio"] > div { gap: 8px !important; }
    div[data-testid="stRadio"] label {
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; padding: 12px 16px !important;
        width: 100% !important; color: var(--text) !important;
        transition: border-color 0.15s !important;
    }
    div[data-testid="stRadio"] label:hover { border-color: var(--teal) !important; }

    /* Buttons */
    div.stButton > button {
        background: var(--teal) !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; padding: 10px 24px !important;
        width: 100% !important; transition: background 0.2s !important;
    }
    div.stButton > button:hover { background: var(--teal-light) !important; }

    /* Feedback */
    .feedback-correct {
        background: rgba(39,174,96,0.1); border: 1px solid var(--success);
        border-left: 4px solid var(--success); border-radius: 8px;
        padding: 16px 20px; margin-top: 14px;
        font-size: 0.92rem; line-height: 1.75; color: var(--text) !important;
    }
    .feedback-wrong {
        background: rgba(192,57,43,0.1); border: 1px solid var(--error);
        border-left: 4px solid var(--error); border-radius: 8px;
        padding: 16px 20px; margin-top: 14px;
        font-size: 0.92rem; line-height: 1.75; color: var(--text) !important;
    }
    .feedback-correct strong { color: #2ECC71 !important; }
    .feedback-wrong strong { color: #E74C3C !important; }

    /* Stat pill */
    .stat-pill {
        background: var(--card); border: 1px solid var(--border);
        border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .stat-pill .s-label { font-size: 0.78rem; color: var(--muted) !important; }
    .stat-pill .s-value { font-size: 0.92rem; font-weight: 600; color: var(--teal-light) !important; }

    /* Summary box */
    .summary-box {
        background: rgba(15,158,142,0.08); border: 1px solid var(--teal);
        border-radius: 10px; padding: 20px 24px; margin-top: 18px;
    }
    .summary-box h4 { color: var(--teal-light) !important; margin: 0 0 10px; }

    /* Complete banner */
    .complete-banner {
        background: linear-gradient(135deg, rgba(39,174,96,0.15), rgba(15,158,142,0.1));
        border: 1px solid var(--success); border-radius: 12px;
        padding: 24px; text-align: center; margin-bottom: 22px;
    }
    .complete-banner h2 { color: #2ECC71 !important; font-size: 1.5rem !important; }

    /* Algorithm image container */
    .algo-container {
        background: var(--card); border: 1px solid var(--border);
        border-radius: 10px; padding: 16px; margin-top: 14px;
    }
    .algo-container .algo-title {
        font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em;
        text-transform: uppercase; color: var(--amber) !important; margin-bottom: 10px; display: block;
    }

    hr { border-color: var(--border) !important; }
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--navy); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

    .stSelectbox div[data-baseweb="select"] { background-color: var(--card) !important; border-color: var(--border) !important; }
    .streamlit-expanderHeader { background-color: var(--card) !important; border-color: var(--border) !important; }
    .streamlit-expanderContent { background-color: var(--card) !important; border-color: var(--border) !important; }

    /* Image caption */
    .img-caption { font-size: 0.78rem; color: var(--muted) !important; text-align: center; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# ===============================
# SESSION STATE
# ===============================
defaults = {
    "step": 0,
    "case_choice": None,
    "answered": False,
    "last_correct": False,
    "visible_labs": ["Na⁺"],
    "scores": {},
    "total_questions": 0,
    "correct_answers": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ===============================
# LAB DATA
# ===============================
LAB_VALUES = {
    "case1": {
        "Na⁺":      ("121 mEq/L",  True),
        "Plasma Osm":("258 mOsm/kg",True),
        "Urine Osm":("520 mOsm/kg",False),
        "Urine Na": ("7 mEq/L",    False),
        "BUN/Cr":   ("48 / 1.5",   True),
    },
    "case2": {
        "Na⁺":      ("124 mEq/L",  True),
        "Plasma Osm":("265 mOsm/kg",True),
        "Urine Osm":("470 mOsm/kg",False),
        "Urine Na": ("9 mEq/L",    False),
    },
    "case3": {
        "Na⁺":      ("118 mEq/L",  True),
        "Plasma Osm":("255 mOsm/kg",True),
        "Urine Osm":("410 mOsm/kg",False),
        "Urine Na": ("38 mEq/L",   True),
    },
    "case4": {
        "Na⁺":      ("119 mEq/L",  True),
        "Plasma Osm":("260 mOsm/kg",True),
        "Urine Osm":("55 mOsm/kg", False),
        "Urine Na": ("14 mEq/L",   False),
    },
}

CASE_META = {
    "case1": {"label": "Case A", "preview": "45F · nausea, vomiting, lightheadedness"},
    "case2": {"label": "Case B", "preview": "72M · CHF, worsening dyspnea, leg edema"},
    "case3": {"label": "Case C", "preview": "63M · lung cancer, confusion, unsteady gait"},
    "case4": {"label": "Case D", "preview": "37M · schizophrenia, polydipsia, confusion"},
}

# ─── STEP QUESTIONS ───────────────────────────────────────────────────────────
# ===============================
# HELPER FUNCTIONS
# ===============================
def display_labs():
    case = st.session_state.case_choice
    labs = LAB_VALUES[case]
    items = ""
    for k in st.session_state.visible_labs:
        if k in labs:
            val, abnormal = labs[k]
            cls = "lab-value abnormal" if abnormal else "lab-value"
            items += f'<div class="lab-item"><span class="lab-label">{k}</span><span class="{cls}">{val}</span></div>'
    st.markdown(f'''<div class="labs-strip"><span class="lab-header">🧪 Active Labs</span><div class="lab-row">{items}</div></div>''', unsafe_allow_html=True)

def show_vignette():
    case = st.session_state.case_choice
    vignettes = {
        "case1": "A 45-year-old woman presents with four days of nausea and repeated vomiting. She feels lightheaded when standing and her urine is dark.<br><br>Exam: <strong>dry mucous membranes</strong>, BP <strong>92/58 → 84/50 orthostatic</strong>, HR <strong>120 bpm</strong>, delayed cap refill. Lungs clear, no edema.",
        "case2": "A 72-year-old man with CHF has worsening dyspnea, orthopnea, and leg swelling. He missed several diuretic doses and has gained 6 lb this week.<br><br>Exam: BP 142/85, HR 102. <strong>JVP elevated</strong>, <strong>bibasilar crackles</strong>, <strong>2+ pitting edema</strong> bilaterally.",
        "case3": "A 63-year-old man with small cell lung cancer has progressive confusion and unsteady gait over one week. No vomiting or excess water intake.<br><br>Exam: Alert but <strong>disoriented to time</strong>. Vital signs stable. <strong>Moist mucous membranes, no edema, normal skin turgor</strong>. No volume depletion or overload.",
        "case4": "A 37-year-old man with schizophrenia drinks gallons of water daily. Diet consists mostly of crackers and juice.<br><br>Exam: <strong>Normal vitals</strong>, moist mucous membranes, normal skin turgor, <strong>no edema</strong>. Neither dehydrated nor fluid overloaded."
    }
    with st.expander("📋 Clinical Vignette", expanded=(st.session_state.step == 1)):
        st.markdown(f'<div class="vignette-box">{vignettes[case]}</div>', unsafe_allow_html=True)

def show_algo_image(img_path, caption):
    if os.path.exists(img_path):
        st.markdown('<div class="algo-container"><span class="algo-title">📍 Where You Are in the Algorithm</span>', unsafe_allow_html=True)
        st.image(img_path, use_container_width=True)
        st.markdown(f'<p class="img-caption">{caption}</p></div>', unsafe_allow_html=True)

def step_bar(current, total):
    pips = ""
    for i in range(total):
        cls = "done" if i < current - 1 else ("active" if i == current - 1 else "")
        pips += f'<div class="step-pip {cls}"></div>'
    st.markdown(f'<div class="step-bar">{pips}</div>', unsafe_allow_html=True)

def question_card(num, total, text):
    st.markdown(f'<div class="question-card"><span class="question-num">Step {num} of {total}</span><div class="question-text">{text}</div></div>', unsafe_allow_html=True)

def render_diagram(key):
    fn = DIAGRAMS.get(key)
    if fn:
        html, h = fn()
        components.html(html, height=h, scrolling=True)

STEPS = {
    "case1": [
        {
            "q": "A 45-year-old woman presents with Na⁺ of 121 mEq/L after four days of vomiting. What is the FIRST step in evaluating her hyponatremia?",
            "options": [
                "Check clinical volume status",
                "Check plasma osmolality",
                "Check urine sodium",
                "Check urine osmolality"
            ],
            "correct": 1,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! Even though this patient's vomiting strongly suggests hypovolemic hyponatremia, you must always start with <strong>plasma osmolality</strong>. Sodium can appear low for three different reasons — true dilution (hypotonic), high osmoles pulling water out of cells (hypertonic), or lab artifact from high lipids/proteins (isotonic). Only plasma osmolality distinguishes these. Skipping this step risks misclassifying and mistreating the wrong type of hyponatremia.",
            "wrong_fb": {
                0: "Tempting — her presentation does suggest hypovolemia, and you will assess volume status. But volume status is step 3, not step 1. You first need to confirm this is true hypotonic hyponatremia via plasma osmolality.",
                2: "Urine sodium is a critical step in this case, but it comes several steps later. Jumping to RAAS without confirming true hyponatremia first skips the essential early branches of the algorithm.",
                3: "Urine osmolality (ADH status) is step 2 in the algorithm — but you cannot proceed there without first confirming true hypotonic hyponatremia with plasma osmolality.",
            },
            "algo_img_pre": "step1hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 1 — Check plasma osmolality. Na < 135 has been established. Now confirm it is truly hypotonic.",
            "unlock_lab": "Plasma Osm",
        },
        {
            "q": "Plasma osmolality returns at 258 mOsm/kg. A classmate argues this is borderline and could represent artifact from her elevated BUN. How do you respond?",
            "options": [
                "Agree — BUN contributes to measured osmolality, so 258 could be falsely low; repeat after hydration",
                "Disagree — 258 is below 275 regardless of BUN contribution, confirming true hypotonic hyponatremia",
                "Agree — BUN elevation in this patient could be causing pseudohyponatremia; check lipid panel",
                "Disagree — 258 is hypertonic, suggesting glucose or mannitol is shifting water into the vasculature"
            ],
            "correct": 1,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! BUN is an ineffective osmole — it freely crosses cell membranes and does NOT cause water shifts. BUN contributes to <strong>measured osmolality</strong> but not to <strong>effective osmolality (tonicity)</strong>. Even accounting for this, her measured osm of 258 is well below 275 mOsm/kg, confirming true hypotonic hyponatremia. Her blood is genuinely diluted. Note the direction, too: urea adds to measured osmolality, so an elevated BUN would make the measured plasma osm HIGHER, not falsely low — her effective osmolality is actually even lower than 258.",
            "wrong_fb": {
                0: "This gets the direction wrong. Elevated BUN (urea) INCREASES measured plasma osmolality — it cannot make 258 falsely low. Because urea is an ineffective osmole that does not cause water shifts, her effective osmolality (tonicity) is actually even lower than 258. A plasma osm of 258 confirms true dilution. Repeating is unnecessary.",
                2: "BUN does NOT cause pseudohyponatremia. Pseudohyponatremia comes from high lipids or proteins occupying plasma volume. High BUN means the kidneys are underperfused — which is actually consistent with hypovolemia here.",
                3: "258 mOsm/kg is clearly LOW, not hypertonic. Hypertonic hyponatremia from glucose or mannitol would give elevated osmolality above 295.",
            },
        },
        {
            "q": "True hypotonic hyponatremia is confirmed. What is the NEXT diagnostic step?",
            "options": [
                "Assess volume status",
                "Check urine sodium",
                "Check urine osmolality",
                "Calculate the fractional excretion of sodium (FENa) to assess renal handling"
            ],
            "correct": 2,
            "svg": "urine_osm_adh",
            "correct_fb": "Correct! After confirming true hypotonic hyponatremia, the next branch is <strong>urine osmolality</strong> — which tells you if ADH is active. High urine osm (>285) means ADH is ON and the kidneys are concentrating urine. Low urine osm (<100) means ADH is OFF and the kidneys are diluting urine. This ADH status determines which side of the algorithm tree you follow before volume status.",
            "wrong_fb": {
                0: "You will assess volume status — but it is step 3, not step 2. The algorithm requires ADH status first because it determines whether you even need to assess volume status at all (ADH-independent cases stop here).",
                1: "Urine sodium comes after urine osmolality. Knowing RAAS status without first knowing ADH status puts you out of algorithmic sequence.",
                3: "FENa is used to differentiate prerenal from intrinsic renal failure — it is not part of the standard hyponatremia algorithm.",
            },
            "algo_img_pre": "step2hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 2 — Check urine osmolality to determine if ADH is ON or OFF.",
            "unlock_lab": "Urine Osm",
        },
        {
            "q": "Urine osmolality is 520 mOsm/kg. A colleague says: 'ADH must be inappropriately elevated — her plasma osm is already low, so ADH should be suppressed.' Do you agree?",
            "options": [
                "Yes — a urine osm of 520 with a plasma osm of 258 proves ADH is autonomously secreted and inappropriate",
                "No — her urine osm of 520 is actually appropriately elevated given that her intravascular volume is depleted",
                "Yes — urine osm above 300 is always inappropriate in the setting of hyponatremia",
                "No — urine osm of 520 simply reflects normal tubular reabsorption; ADH is not responsible"
            ],
            "correct": 1,
            "svg": "adh_triggers",
            "correct_fb": "Correct! ADH can be activated by two signals: high plasma osmolality OR low effective arterial blood volume. In this patient, her plasma osm is low — which would normally suppress ADH. <strong>However, her profound hypovolemia from vomiting is a much stronger, overriding stimulus for ADH release.</strong> The body prioritizes volume over tonicity. High urine osm here is <strong>appropriate</strong> — the brain is telling the kidneys to hold water to maintain perfusion, even at the cost of worsening hyponatremia.",
            "wrong_fb": {
                0: "Incorrect — inappropriate ADH secretion (SIADH) occurs in euvolemic patients where there is NO physiologic reason for ADH to be active. This patient is hypovolemic, which is a legitimate trigger for ADH. The ADH secretion here is appropriate.",
                2: "Incorrect — a high urine osm is not automatically inappropriate in hyponatremia. ADH can be appropriately elevated if volume is depleted, even when plasma osm is low. Context determines appropriateness.",
                3: "Incorrect — urine osm of 520 absolutely reflects ADH action. ADH acts on V2 receptors in the collecting duct to insert aquaporin-2 channels, concentrating urine. This does not occur by passive tubular reabsorption alone.",
            },
        },
        {
            "q": "ADH is ON. What is the NEXT step in narrowing the diagnosis?",
            "options": [
                "Check urine sodium to determine RAAS activity",
                "Determine clinical volume status",
                "Calculate plasma-urine osmolal gap to quantify free water retention",
                "Check TSH and morning cortisol to rule out secondary causes of ADH excess"
            ],
            "correct": 1,
            "svg": "volume_status",
            "correct_fb": "Correct! With ADH ON, the next critical branch in the algorithm is <strong>clinical volume status</strong>. Volume status answers the fundamental question: WHY is ADH on? Hypovolemia triggers ADH via baroreceptors. Hypervolemia with low effective arterial blood volume (CHF, cirrhosis, nephrotic syndrome) also triggers ADH. Euvolemia with ADH on suggests SIADH. Physical exam — orthostatics, JVD, edema, mucous membranes — determines which branch you follow.",
            "wrong_fb": {
                0: "Urine sodium is an important step — but it comes AFTER volume status. The algorithm sequences volume status first because it determines the physiologic context for interpreting urine sodium.",
                2: "Osmolal gap calculation is not part of the standard hyponatremia algorithm. It has limited clinical utility here.",
                3: "TSH and cortisol are checked when the workup suggests euvolemic hyponatremia as secondary causes of SIADH. Volume status must be assessed first.",
            },
            "algo_img_pre": "step4hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 3 — ADH is ON. Now determine volume status to identify the cause.",
        },
        {
            "q": "BP 92/58 sitting → 84/50 standing, HR 120, dry mucous membranes, dark urine, BUN/Cr 48/1.5. What is her volume status?",
            "options": [
                "Euvolemic with redistributed fluid — her Na is low because ADH is secreting inappropriately",
                "Hypervolemic — her elevated BUN suggests renal failure causing fluid overload",
                "Hypovolemic — multiple clinical and laboratory markers confirm intravascular volume depletion",
                "Hypovolemic from third-spacing — the fluid has shifted into the interstitium not the vasculature"
            ],
            "correct": 2,
            "svg": "volume_status",
            "correct_fb": "Correct! She is unambiguously <strong>hypovolemic</strong>. The orthostatic blood pressure drop (92→84 systolic from sitting to standing) confirms inadequate intravascular volume to maintain pressure with positional change. Tachycardia is a compensatory response. Dry mucous membranes and dark urine indicate systemic dehydration. A BUN/Cr ratio >20 indicates prerenal physiology — the kidneys are underperfused and retaining urea. All of these together paint a clear picture of true intravascular volume depletion from vomiting.",
            "wrong_fb": {
                0: "Incorrect. Euvolemia means normal total body fluid and normal effective circulation. This patient has tachycardia, orthostatic hypotension, dry membranes, and prerenal azotemia — none of which are consistent with euvolemia.",
                1: "Incorrect. An elevated BUN/Cr ratio in this context reflects prerenal azotemia (poor kidney perfusion from hypovolemia), not fluid overload from renal failure. There is no edema, JVD, or weight gain here.",
                3: "Third-spacing can occur with pancreatitis, burns, or bowel obstruction but is not the mechanism here. Her volume loss is from GI losses via vomiting.",
            },
        },
        {
            "q": "She is hypovolemic with ADH ON. Which test best determines if RAAS is activated?",
            "options": [
                "Fractional excretion of sodium (FENa)",
                "Urine sodium concentration",
                "Serum aldosterone level",
                "Urine sodium-to-creatinine ratio"
            ],
            "correct": 1,
            "svg": "raas_cascade",
            "correct_fb": "Correct! <strong>Urine sodium</strong> is the practical, bedside test for RAAS activity. Aldosterone acts on the collecting duct to reabsorb sodium — so if aldosterone is high (RAAS ON), the kidney reabsorbs sodium and urine Na will be LOW (<20 mEq/L). If RAAS is off, sodium is excreted freely and urine Na will be HIGH (>20 mEq/L). A spot urine Na is fast, cheap, and directly reflects what the kidneys are actually doing.",
            "wrong_fb": {
                0: "FENa is useful for differentiating prerenal AKI from ATN, but it is not typically used to assess RAAS activity in hyponatremia workup. Spot urine sodium is the standard.",
                2: "Serum aldosterone measures the hormone directly, but it requires a specialized assay and is affected by posture, time of day, and salt intake. Urine sodium gives you the functional output of aldosterone's effect, which is more clinically practical.",
                3: "Urine Na-to-creatinine ratio improves accuracy in concentrated or dilute urine specimens, but the simple spot urine sodium is the standard clinical tool and sufficient here.",
            },
            "unlock_lab": "Urine Na",
            "unlock_lab2": "BUN/Cr",
        },
        {
            "q": "Urine sodium is 7 mEq/L. Is RAAS activated?",
            "options": [
                "No — urine Na of 7 simply reflects poor urine output from dehydration, not RAAS activation",
                "Yes — urine Na below 20 mEq/L confirms aldosterone-driven sodium conservation",
                "Indeterminate — urine sodium must be interpreted alongside urine creatinine to be meaningful",
                "No — RAAS would cause urine Na to be HIGH as the kidneys filter more sodium"
            ],
            "correct": 1,
            "svg": "urine_na_comparison",
            "correct_fb": "Correct! Urine Na of <strong>7 mEq/L is far below the 20 mEq/L threshold</strong>. The kidneys are retaining virtually all filtered sodium. This is the functional signature of maximal aldosterone activity — RAAS is fully ON. Her body perceived low perfusion (from vomiting-induced hypovolemia) and activated renin → angiotensin → aldosterone to rescue circulating volume by pulling sodium (and water) back into the bloodstream. This is the correct physiologic response to her situation.",
            "wrong_fb": {
                0: "Incorrect. Low urine output from dehydration might concentrate the urine (raising urine osm), but a urine Na of 7 mEq/L is specifically low — not just concentrated. This reflects active aldosterone-driven sodium reabsorption, not simply dehydration lowering urine volume.",
                2: "Urine Na-to-creatinine ratio adds precision in borderline cases, but a urine Na of 7 mEq/L is so definitively low that the ratio is unnecessary here.",
                3: "Incorrect — RAAS causes sodium RETENTION, meaning it drives urine Na DOWN. High aldosterone = kidneys keep sodium = low urine Na.",
            },
        },
        {
            "q": "Integrating all findings: Na 121, plasma osm 258, urine osm 520, urine Na 7, BUN/Cr 48/1.5, hypovolemic exam — what is the most likely diagnosis and mechanism?",
            "options": [
                "SIADH — ectopic ADH from an unidentified source; treat with fluid restriction",
                "Hypovolemic hyponatremia — GI losses triggered appropriate ADH and RAAS activation; treat with isotonic saline",
                "Beer potomania — low solute intake has overwhelmed the kidney's diluting capacity despite ADH suppression",
                "Cerebral salt wasting — the brain is driving inappropriate natriuresis, causing volume depletion and hyponatremia"
            ],
            "correct": 1,
            "svg": "final_summary",
            "correct_fb": "Correct! 🎉 This is <strong>hypovolemic hyponatremia from GI losses</strong>. The complete hormonal signature: low plasma osm (true hyponatremia) + high urine osm (ADH appropriately ON to preserve volume) + very low urine Na (RAAS ON, aldosterone conserving sodium). Every hormone is responding correctly — the body is fighting volume depletion. Treatment is <strong>isotonic saline</strong>: restoring volume turns off the baroreceptor-driven ADH and RAAS, allowing the kidneys to auto-correct the sodium at a safe rate.",
            "wrong_fb": {
                0: "SIADH requires euvolemia and a HIGH urine Na (>20 mEq/L) because RAAS is OFF in a euvolemic patient. This patient has a urine Na of 7 and is clinically hypovolemic — SIADH is excluded.",
                2: "Beer potomania features ADH suppression (urine osm <100) because the problem is inadequate solute, not volume depletion. This patient has ADH ON (urine osm 520), which rules out ADH-independent etiologies.",
                3: "Cerebral salt wasting causes hypovolemia with HIGH urine Na (the kidney inappropriately wastes sodium). This patient has LOW urine Na — the kidney is correctly conserving sodium in response to hypovolemia.",
            },
            "final": True,
            "algo_img_pre": "step5hyponatremia.PNG",
            "algo_caption_pre": "You are here: Final diagnosis — integrate all findings using the complete algorithm.",
        },
    ],

    "case2": [
        {
            "q": "A 72-year-old man with CHF has a Na⁺ of 124 mEq/L. What is the FIRST step in the hyponatremia algorithm?",
            "options": [
                "Assess volume status",
                "Check urine osmolality",
                "Check plasma osmolality",
                "Check urine sodium"
            ],
            "correct": 2,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! Although CHF is a known cause of hyponatremia, you must still confirm with <strong>plasma osmolality</strong> first. CHF does not cause pseudohyponatremia, but the algorithm must always start at the same point — confirming true hypotonic hyponatremia. This ensures no alternative cause (e.g., hyperglycemia from diabetes) is missed.",
            "wrong_fb": {
                0: "Volume status (step 3) will be obvious here — but you still need plasma osmolality first to confirm this is true hypotonic, not isotonic or hypertonic hyponatremia.",
                1: "Urine osmolality (ADH status) is step 2. You cannot proceed to step 2 without completing step 1.",
                3: "Urine sodium (RAAS status) is step 4. Jumping directly there skips three required steps.",
            },
            "algo_img_pre": "step1hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 1 — Plasma osmolality first, regardless of the suspected diagnosis.",
            "unlock_lab": "Plasma Osm",
        },
        {
            "q": "Plasma osmolality is 265 mOsm/kg. A student notes that his BUN is elevated and argues this 'artificially raises' the measured osmolality, making the true osm even lower. Is this reasoning correct?",
            "options": [
                "Yes — elevated BUN inflates the measured osm, so the true effective osm is below 265 and even more hypotonic",
                "Partially — BUN raises measured osm but is an ineffective osmole; 265 still confirms hypotonic hyponatremia either way",
                "No — BUN lowers measured osmolality because it competes with sodium for osmotic effect",
                "No — BUN elevation in CHF indicates congestive hepatopathy, not osmolality changes"
            ],
            "correct": 1,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! The student has the right idea but wrong conclusion. BUN DOES contribute to <strong>measured osmolality</strong> but it is an <strong>ineffective osmole</strong> — it crosses cell membranes freely and does not create osmotic gradients. So the effective osmolality (tonicity) is even lower than 265. Either way, a measured plasma osm of 265 is below 275 mOsm/kg, confirming true hypotonic hyponatremia. The student's point actually strengthens the finding, not weakens it.",
            "wrong_fb": {
                0: "Partially correct reasoning but incorrect conclusion. Yes, BUN does raise measured osm — but this means the effective osm is lower than measured, making the hyponatremia more severe, not questioning whether it exists.",
                2: "Incorrect. BUN raises (not lowers) measured osmolality because it contributes to total solute concentration. However, because it is an ineffective osmole, it does not affect tonicity or water movement.",
                3: "BUN elevation in CHF reflects prerenal azotemia from poor forward flow and reduced renal perfusion — not hepatopathy.",
            },
        },
        {
            "q": "True hypotonic hyponatremia is confirmed. To understand the cause of his hyponatremia, what is the NEXT diagnostic step?",
            "options": [
                "Assess volume status — his JVD and edema make this immediately obvious",
                "Give IV furosemide — he is clearly hypervolemic and needs decongestion",
                "Check urine osmolality",
                "Check urine sodium — RAAS activity in CHF is the key driver of his sodium retention"
            ],
            "correct": 2,
            "svg": "urine_osm_adh",
            "correct_fb": "Correct! <strong>Urine osmolality</strong> is step 2. Even in obvious CHF, you follow the algorithm: ADH status before volume status. In CHF, you will find ADH ON despite total body fluid overload — because the failing heart creates low effective arterial blood volume (EABV), triggering baroreceptors that activate ADH. Understanding this mechanism is more important than just observing the clinical picture.",
            "wrong_fb": {
                0: "Volume status is step 3. Even when it seems clinically obvious (as in CHF), following the algorithm order ensures you understand the mechanism — not just the diagnosis.",
                1: "A loop diuretic is reasonable for his symptomatic volume overload, and you would not hold it while waiting for urine studies. But it is a treatment, not a diagnostic step — it does not tell you why his sodium is low. Understanding the cause of the hyponatremia requires urine osmolality.",
                3: "Urine sodium is step 4 in the algorithm. Sequence matters.",
            },
            "algo_img_pre": "step2hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 2 — Check urine osmolality to determine ADH status.",
            "unlock_lab": "Urine Osm",
        },
        {
            "q": "Urine osmolality is 470 mOsm/kg. His total body water is clearly elevated. Why is ADH still ON?",
            "options": [
                "ADH is secreted by damaged myocardium in CHF, independent of normal physiologic triggers",
                "ADH is inappropriately secreted because CHF activates the hypothalamus via inflammatory cytokines",
                "ADH is appropriately elevated because baroreceptors sense low effective arterial blood volume, not total body water",
                "ADH is elevated because urinary sodium losses have created a hyperosmolar state in the collecting duct"
            ],
            "correct": 2,
            "svg": "adh_triggers",
            "correct_fb": "Correct! This is the central concept of CHF-related hyponatremia. ADH responds to <strong>effective arterial blood volume (EABV)</strong>, not total body water. The failing heart cannot pump blood forward effectively, so baroreceptors in the carotid sinus, aortic arch, and afferent arterioles sense LOW perfusion pressure — and respond by activating ADH (and RAAS). The body literally cannot tell the difference between cardiogenic 'perceived hypovolemia' and real volume depletion. Urine osm of 470 confirms ADH is very much active.",
            "wrong_fb": {
                0: "ADH in CHF is not secreted by the myocardium. It comes from the hypothalamus and posterior pituitary in response to baroreceptor signaling from low EABV.",
                1: "While inflammatory cytokines have complex cardiac effects, ADH activation in CHF is primarily baroreceptor-mediated from low forward cardiac output — not a direct hypothalamic effect of cytokines.",
                3: "Urinary sodium losses lower total sodium but do not create a hyperosmolar state in the collecting duct that stimulates ADH. ADH here is triggered by hemodynamic signals.",
            },
        },
        {
            "q": "ADH is ON. What is the NEXT diagnostic step?",
            "options": [
                "Check urine sodium immediately",
                "Calculate effective arterial blood volume using echocardiographic parameters",
                "Determine clinical volume status",
                "Check serum BNP"
            ],
            "correct": 2,
            "svg": "volume_status",
            "correct_fb": "Correct! <strong>Volume status</strong> is step 3. Physical exam — JVD, peripheral edema, crackles, orthostatics — determines the branch. Hypervolemia + ADH ON points to states like CHF, cirrhosis, and nephrotic syndrome (low EABV despite fluid overload). Hypovolemia + ADH ON points to GI losses, diuretics. Euvolemia + ADH ON points to SIADH.",
            "wrong_fb": {
                0: "Urine sodium comes AFTER volume status in the algorithm. The two tests distinguish causes within the same volume category, not the volume category itself.",
                1: "Echo-derived EABV estimation is an advanced and non-standard approach. Clinical exam determines volume status at the bedside.",
                3: "BNP confirms cardiac dysfunction but is not part of the hyponatremia diagnostic algorithm and does not change the algorithmic sequence.",
            },
            "algo_img_pre": "step4hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 3 — ADH is ON. Now classify volume status.",
        },
        {
            "q": "JVD, bibasilar crackles, 2+ pitting edema, 6 lb weight gain, BP 142/85. What is the volume status, and what is the pathophysiologic explanation?",
            "options": [
                "Hypovolemic — his diuretic doses were missed, causing sodium depletion and volume contraction",
                "Euvolemic — CHF causes redistributed fluid but total body volume is normal",
                "Hypervolemic with low effective arterial blood volume — total body water is high but cardiac output is insufficient",
                "Hypervolemic from renal sodium retention — his kidneys are failing to excrete sodium"
            ],
            "correct": 2,
            "svg": "eabv_chf",
            "correct_fb": "Correct! He is <strong>hypervolemic with low EABV</strong> — this is the hallmark of CHF-related hyponatremia. JVD, crackles, and edema prove total body fluid is excessive. But the failing heart cannot pump blood forward, so arterial baroreceptors sense low perfusion. The kidneys and hypothalamus interpret this as hypovolemia, activating both ADH (water retention) and RAAS (sodium retention). This creates a vicious cycle: more fluid retained → more congestion → worse pump function → more perceived hypovolemia → more retention.",
            "wrong_fb": {
                0: "Incorrect. Missing diuretics causes fluid accumulation (hypervolemia), not depletion. His exam findings — JVD, edema, weight gain — are definitively hypervolemic.",
                1: "Incorrect. Euvolemia means normal total body fluid and normal effective circulation. This patient has clear signs of fluid overload on exam.",
                3: "While renal sodium retention is present in CHF, it is secondary to neurohormonal activation (RAAS), not primary renal failure.",
            },
        },
        {
            "q": "He is hypervolemic with ADH ON. Which best explains why his urine sodium will be LOW despite total body sodium excess?",
            "options": [
                "Low urine Na reflects tubular damage from chronic CHF, impairing sodium secretion",
                "Low urine Na reflects aldosterone-driven sodium reabsorption triggered by low EABV, not total body sodium",
                "Low urine Na reflects suppressed ANP — the failing heart cannot produce adequate natriuretic peptide",
                "Low urine Na reflects glomerular filtration reduction, limiting sodium delivery to the tubule"
            ],
            "correct": 1,
            "svg": "raas_cascade",
            "correct_fb": "Correct! This is the essential concept. Even though total body sodium is HIGH, aldosterone is driven by <strong>perceived low EABV</strong> — not actual sodium content. RAAS responds to perfusion pressure, not total sodium stores. Aldosterone then drives the kidney to reabsorb even more sodium at the collecting duct. The result: urine Na stays LOW (<20 mEq/L) while the patient remains fluid-overloaded. This makes CHF one of the clearest examples of how the body's hormonal response can work against itself.",
            "wrong_fb": {
                0: "CHF causes prerenal physiology in the kidney (from low forward flow), not intrinsic tubular damage. Tubular function is typically preserved early in CHF.",
                2: "ANP is actually elevated in CHF (released by atrial stretch) and does promote natriuresis — but the RAAS-driven sodium retention overwhelms the natriuretic peptide effect, resulting in net sodium retention.",
                3: "Reduced GFR decreases filtered sodium load, but the dominant mechanism for low urine Na in CHF is aldosterone-driven tubular reabsorption at the collecting duct.",
            },
            "unlock_lab": "Urine Na",
        },
        {
            "q": "Urine sodium is 9 mEq/L. Is RAAS activated?",
            "options": [
                "No — urine Na of 9 reflects tubular reabsorption from diuretic washout, not RAAS",
                "Yes — urine Na below 20 mEq/L confirms aldosterone-driven sodium conservation from perceived low EABV",
                "Indeterminate — urine Na must be interpreted with serum sodium to calculate FENa",
                "Yes — but this RAAS activation is inappropriate and distinguishes CHF from SIADH"
            ],
            "correct": 1,
            "svg": "urine_na_comparison",
            "correct_fb": "Correct! A urine Na of <strong>9 mEq/L confirms RAAS is maximally ON</strong>. Despite a body full of fluid, aldosterone is telling the kidneys to retain every milliequivalent of sodium. This is because RAAS is driven by EABV, not total body sodium. This low urine Na in a hypervolemic patient is the hallmark that separates CHF, cirrhosis, and nephrotic syndrome from SIADH (which has high urine Na because the patient is euvolemic and RAAS is OFF).",
            "wrong_fb": {
                0: "He missed diuretic doses — so diuretic effect has waned. The low urine Na reflects active RAAS-driven sodium retention, not residual diuretic effect.",
                2: "FENa is useful for AKI workup but is not required to interpret urine sodium in hyponatremia. A urine Na of 9 mEq/L is unambiguously low.",
                3: "Partially correct that RAAS ON with hypervolemia is physiologically paradoxical — but it is not 'inappropriate' in the same sense as SIADH. It is a predictable consequence of low EABV signaling. The distinction from SIADH is euvolemia vs. hypervolemia, not RAAS appropriateness.",
            },
        },
        {
            "q": "Integrating all findings: Na 124, plasma osm 265, urine osm 470, urine Na 9, JVD + edema + crackles — what is the diagnosis and its treatment principle?",
            "options": [
                "SIADH from cardiac cytokines",
                "Hypovolemic hyponatremia from missed diuretics",
                "Hypervolemic hyponatremia from CHF",
                "Hypervolemic hyponatremia from renal failure"
            ],
            "correct": 2,
            "svg": "final_summary",
            "correct_fb": "Correct! 🎉 This is <strong>hypervolemic hyponatremia from CHF with low EABV</strong>. The complete signature: low plasma osm + ADH ON (urine osm 470) + RAAS ON (urine Na 9) + hypervolemic exam. Treatment targets the root cause — the failing pump. <strong>Loop diuretics</strong> reduce congestion and improve forward flow, which turns off baroreceptor-driven ADH and RAAS, allowing the kidneys to correct sodium. ACE inhibitors and beta-blockers address pump failure long-term. Free water restriction is an adjunct.",
            "wrong_fb": {
                0: "SIADH is euvolemic with HIGH urine Na (>20 mEq/L). This patient is hypervolemic with low urine Na — definitively not SIADH.",
                1: "His exam shows volume overload (JVD, edema, weight gain), not volume depletion. Giving saline would worsen his congestion.",
                3: "Renal failure can cause hypervolemic hyponatremia, but his labs (BUN/Cr, urine Na pattern) and clinical context point to CHF as the primary driver.",
            },
            "final": True,
            "algo_img_pre": "step5hyponatremia.PNG",
            "algo_caption_pre": "You are here: Final diagnosis — integrate all findings.",
        },
    ],

    "case3": [
        {
            "q": "A 63-year-old man with small cell lung cancer has a Na⁺ of 118 mEq/L and new confusion. What is the FIRST step?",
            "options": [
                "Order urgent brain MRI — new confusion with cancer requires neuroimaging before the hyponatremia workup",
                "Check plasma osmolality",
                "Check urine osmolality — ectopic ADH from the tumor is the most likely cause; confirm ADH is ON",
                "Assess volume status"
            ],
            "correct": 1,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! Even with a compelling clinical story (small cell lung cancer + confusion + hyponatremia = SIADH until proven otherwise), the algorithm always starts with <strong>plasma osmolality</strong>. You cannot assume SIADH without ruling out isotonic or hypertonic causes. More practically, confirming this is step by step also reinforces the diagnostic reasoning you will need to reproduce on exams.",
            "wrong_fb": {
                0: "Brain MRI may ultimately be needed for his neurologic symptoms, but it is not part of the hyponatremia algorithm. Workup the hyponatremia first — cerebral edema from hyponatremia itself is the most likely cause of his confusion.",
                2: "You are correct that ADH status is step 2 — but you cannot proceed to step 2 without first completing step 1 (plasma osmolality).",
                3: "His exam appearance suggesting euvolemia is a clinical impression, not a completed algorithmic step. The algorithm always starts at plasma osmolality.",
            },
            "algo_img_pre": "step1hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 1 — Plasma osmolality. Even with a clear clinical story, the algorithm starts here.",
            "unlock_lab": "Plasma Osm",
        },
        {
            "q": "Plasma osmolality is 255 mOsm/kg. A student notes that his measured osm should be recalculated as effective osm by subtracting BUN. Is this necessary, and does it change the interpretation?",
            "options": [
                "Yes — you must calculate effective osm because BUN inflates the measured value; effective osm may be normal",
                "No — effective osm calculation is only needed when osm gap is elevated; 255 confirms hypotonic hyponatremia regardless",
                "Yes — subtracting BUN from measured osm is required before any interpretation; standard formula: effective osm = measured osm − (BUN/2.8)",
                "No — effective osm equals measured osm in euvolemic patients because BUN does not change across the membrane"
            ],
            "correct": 1,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! You do not need to formally calculate effective osmolality here. Effective osm (tonicity) = measured osm − (BUN/2.8). BUN is an ineffective osmole and subtracting it gives the true water-driving force. However, in this case, even without subtracting BUN, a measured osm of 255 is already well below 275 mOsm/kg. Recalculating would make the effective osm even lower — it can only strengthen the diagnosis, not change it. The calculation matters when measured osm is borderline (275–285 range).",
            "wrong_fb": {
                0: "Subtracting BUN would make the effective osm lower than 255, not potentially normal. BUN raises measured osm, so removing it reduces the number. This makes the hyponatremia more severe, not questionable.",
                2: "The osmolal gap (measured − calculated osm) is used to detect unmeasured osmoles (e.g., methanol, ethylene glycol) — not for the plasma osm interpretation step in hyponatremia workup.",
                3: "BUN does cross membranes freely (that is why it is an ineffective osmole), but this is true in ALL patients, not just euvolemic ones. BUN always reduces effective osm relative to measured osm.",
            },
        },
        {
            "q": "True hypotonic hyponatremia confirmed. What is the NEXT step, and why does sequence matter?",
            "options": [
                "Check urine osmolality",
                "Assess volume status",
                "Check urine sodium",
                "Check serum cortisol — euvolemic hyponatremia from adrenal insufficiency must be excluded first"
            ],
            "correct": 0,
            "svg": "urine_osm_adh",
            "correct_fb": "Correct! <strong>Urine osmolality is step 2</strong>, and sequence matters critically because ADH status determines the entire branch of the algorithm you follow. If ADH is OFF (urine osm <100), you are in an ADH-independent pathway and <strong>skip volume status entirely</strong> — going directly to ADH-independent causes (beer potomania, psychogenic polydipsia). If ADH is ON (urine osm >285), you proceed to volume status. The sequence is not arbitrary — it reflects the pathophysiologic logic of water handling.",
            "wrong_fb": {
                1: "Even if you are clinically confident about volume status, the algorithm requires ADH status first. An ADH-OFF result would change your entire diagnostic path, regardless of volume appearance.",
                2: "Urine sodium (RAAS status) is step 4. Jumping there without ADH status and volume status skips critical branches.",
                3: "Adrenal insufficiency is a cause of euvolemic hyponatremia — but you must first determine ADH status and volume status before considering specific secondary causes.",
            },
            "algo_img_pre": "step2hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 2 — Urine osmolality determines ADH status and which branch to follow.",
            "unlock_lab": "Urine Osm",
        },
        {
            "q": "Urine osmolality is 410 mOsm/kg. His plasma osm is 255. A colleague argues this proves SIADH definitively. Do you agree?",
            "options": [
                "Yes — a urine osm of 410 with a plasma osm of 255 is diagnostic of SIADH; volume assessment is unnecessary",
                "Partially — a high urine osm with low plasma osm suggests inappropriate ADH, but you must still confirm euvolemia and high urine Na before diagnosing SIADH",
                "No — a urine osm of 410 is only mildly elevated and does not reliably indicate ADH activity",
                "No — SIADH requires urine osm above 500 mOsm/kg; 410 suggests only partial ADH activation"
            ],
            "correct": 1,
            "svg": "adh_triggers",
            "correct_fb": "Correct! Your colleague is close but not complete. A urine osm of 410 with a plasma osm of 255 does suggest inappropriate ADH activity — plasma osm is low and should suppress ADH, but it hasn't. However, <strong>SIADH is a diagnosis of exclusion</strong> that requires confirming: (1) euvolemia — ruling out hypovolemia and hypervolemia, and (2) high urine Na (>20 mEq/L) — ruling out RAAS activation. Until you complete those steps, 'inappropriate ADH' is the finding, not yet the full diagnosis of SIADH.",
            "wrong_fb": {
                0: "Incorrect. High urine osm with low plasma osm is highly suggestive but not diagnostic alone. SIADH requires euvolemia and high urine Na to exclude other causes of ADH activation.",
                2: "Incorrect. A urine osm of 410 clearly reflects ADH activity. ADH concentrates urine to above the plasma osm (285). A urine osm of 410 is significantly above 285 — ADH is active.",
                3: "Incorrect. SIADH does not require urine osm >500. Any urine osm >100 mOsm/kg in the setting of hyponatremia and low plasma osm is significant. The threshold is often cited as urine osm >100, indicating ADH is not appropriately suppressed.",
            },
        },
        {
            "q": "ADH is ON. What is the NEXT step?",
            "options": [
                "Check urine sodium immediately",
                "Determine clinical volume status",
                "Start fluid restriction empirically",
                "Check serum TSH and morning cortisol"
            ],
            "correct": 1,
            "svg": "volume_status",
            "correct_fb": "Correct! Volume status (step 3) comes before urine sodium (step 4). Volume status determines the physiologic context: hypovolemia + ADH ON = appropriate ADH from baroreceptors. Euvolemia + ADH ON = inappropriate ADH (SIADH or secondary SIADH from hypothyroidism/adrenal insufficiency). Hypervolemia + ADH ON = CHF/cirrhosis/nephrotic. Without this branch, urine sodium alone cannot tell you why ADH is on.",
            "wrong_fb": {
                0: "Urine sodium comes after volume status. Knowing RAAS is off (high urine Na) could mean SIADH or simply euvolemia — you need volume status to interpret it correctly.",
                2: "Fluid restriction is a treatment for SIADH. You cannot initiate disease-specific treatment without a complete diagnosis.",
                3: "TSH and cortisol are relevant secondary workup for SIADH — but they come after establishing the diagnosis through the algorithm, not before.",
            },
            "algo_img_pre": "step4hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 3 — ADH is ON. Now classify volume status.",
        },
        {
            "q": "Stable vitals, moist membranes, no edema, no JVD, normal skin turgor. What is the volume status, and what does this reveal about the ADH secretion?",
            "options": [
                "Euvolemic — ADH is firing without a physiologic trigger, strongly suggesting autonomous (inappropriate) secretion",
                "Mildly hypovolemic — cancer-related poor oral intake has depleted volume enough to trigger ADH",
                "Euvolemic — ADH is ON because his plasma osm briefly exceeded 285 during the vomiting-free interval",
                "Hypervolemic — cancer causes a protein-losing state that shifts fluid from the vasculature to the interstitium"
            ],
            "correct": 0,
            "svg": "volume_status",
            "correct_fb": "Correct! He is <strong>euvolemic</strong> — no signs of depletion or overload. This is the key finding. ADH has two physiologic triggers: high plasma osm (osmotic stimulus) and low EABV (hemodynamic stimulus). His plasma osm is LOW (255) and his effective volume is NORMAL. Neither stimulus for ADH is present. Yet ADH is ON. This means the ADH secretion is <strong>autonomous and inappropriate</strong> — the definition of SIADH. In this patient, the small cell lung cancer is secreting ADH ectopically.",
            "wrong_fb": {
                1: "Cancer can cause poor intake, but his exam shows no signs of volume depletion. More importantly, mild hypovolemia sufficient to trigger ADH would typically show tachycardia or mucous membrane dryness.",
                2: "His plasma osm is currently 255 — well below the osmotic threshold for ADH release (~285-290). There is no scenario in which osm transiently exceeded 285 and then fell without volume changes.",
                3: "Hypovolemia from protein-losing states (nephrotic syndrome, protein-losing enteropathy) causes ascites and edema, but this patient has no edema or other signs of hypervolemia.",
            },
        },
        {
            "q": "Euvolemic + ADH ON. What test most efficiently distinguishes SIADH from adrenal insufficiency and hypothyroidism at this stage?",
            "options": [
                "Urine sodium",
                "Serum cortisol and TSH",
                "Plasma ADH level",
                "Trial of isotonic saline and observe the sodium response"
            ],
            "correct": 1,
            "svg": "urine_na_comparison",
            "correct_fb": "Correct! <strong>Serum cortisol and TSH</strong>. SIADH is a diagnosis of exclusion. Secondary adrenal insufficiency and severe hypothyroidism can produce the same picture as SIADH: euvolemia, inappropriately concentrated urine (urine osm >100), and natriuresis (urine Na >30). Urine studies therefore cannot separate these three — you must rule out the endocrine causes directly before diagnosing SIADH (Adrogué &amp; Madias, NEJM 2023). Urine sodium is still checked, mainly to support your clinical volume assessment.",
            "wrong_fb": {
                0: "Urine sodium helps confirm your clinical volume assessment, but it does not distinguish SIADH from secondary adrenal insufficiency or severe hypothyroidism — all three can show a high urine Na with an elevated urine osm. Only endocrine testing (cortisol and TSH) excludes them.",
                2: "Plasma ADH levels are rarely measured in clinical practice — they are impractical (must be sent to specialized labs) and difficult to interpret. ADH can be elevated in all three conditions, so it would not separate them anyway.",
                3: "An isotonic saline trial does not identify an endocrine cause, and in SIADH it can worsen the hyponatremia (the sodium is excreted while the water is retained). Cortisol and TSH are needed to exclude adrenal insufficiency and hypothyroidism.",
            },
            "unlock_lab": "Urine Na",
        },
        {
            "q": "Urine sodium is 38 mEq/L. How does this single result narrow the diagnosis between SIADH and adrenal insufficiency?",
            "options": [
                "It doesn't — both SIADH and adrenal insufficiency can cause urine Na >20 mEq/L in euvolemic patients",
                "Urine Na of 38 confirms SIADH — adrenal insufficiency would cause RAAS activation and low urine Na",
                "Urine Na of 38 favors adrenal insufficiency — cortisol deficiency causes renal salt wasting directly",
                "Urine Na of 38 is non-diagnostic — it only becomes meaningful if serum potassium is also checked"
            ],
            "correct": 1,
            "svg": "siadh_pattern",
            "correct_fb": "Correct! A urine Na of <strong>38 mEq/L (>20 mEq/L) confirms RAAS is OFF</strong>. The kidneys are freely excreting sodium because perfusion is adequate — euvolemia means no trigger for aldosterone. This pattern (euvolemia + ADH ON + RAAS OFF) is the hallmark of SIADH. In contrast, adrenal insufficiency causes relative hypovolemia (cortisol deficiency impairs vascular tone) → RAAS activates → LOW urine Na (<20 mEq/L). The urine Na of 38 rules out adrenal insufficiency as the primary driver here.",
            "wrong_fb": {
                0: "Incorrect. Adrenal insufficiency causes functional hypovolemia via vasodilation and mineralocorticoid deficiency (primary adrenal insufficiency) → RAAS activation → LOW urine Na. High urine Na in euvolemia is specific to SIADH and similar conditions.",
                2: "Incorrect. Adrenal insufficiency does not cause salt wasting directly in secondary adrenal insufficiency (which lacks cortisol but has intact aldosterone). Primary adrenal insufficiency does cause salt wasting — but then urine Na is HIGH and the clinical picture includes hyperkalemia and hypotension.",
                3: "Incorrect. While hyperkalemia helps identify primary adrenal insufficiency (from aldosterone deficiency), urine Na of 38 mEq/L in a euvolemic patient is meaningful on its own — it confirms RAAS is off.",
            },
        },
        {
            "q": "Na 118, plasma osm 255, urine osm 410, urine Na 38, euvolemic, small cell lung cancer — final diagnosis and first-line treatment?",
            "options": [
                "Hypovolemic hyponatremia from cancer-related poor intake",
                "Beer potomania — low solute from chemotherapy has limited urinary water excretion; increase dietary solutes",
                "SIADH from ectopic ADH secretion by the small cell lung cancer",
                "Cerebral salt wasting from intracranial involvement"
            ],
            "correct": 2,
            "svg": "final_summary",
            "correct_fb": "Correct! 🎉 This is <strong>SIADH from ectopic ADH secretion</strong> — the classic paraneoplastic syndrome of small cell lung cancer. Complete pattern: low plasma osm + ADH ON (urine osm 410) + euvolemic + RAAS OFF (urine Na 38). Small cell lung cancer secretes ADH autonomously without responding to normal osmotic or hemodynamic feedback. First-line treatment is <strong>fluid restriction</strong> to 500-1000 mL/day. Refractory cases: tolvaptan (V2 receptor antagonist) or urea supplementation. The lung cancer itself must be treated.",
            "wrong_fb": {
                0: "Hypovolemic hyponatremia would show low urine Na (<20 mEq/L) from RAAS activation. His urine Na is 38 — RAAS is off, confirming euvolemia and ruling this out.",
                1: "Beer potomania has ADH OFF (urine osm <100) because the kidneys are trying to excrete water but can't due to low solute. His urine osm of 410 confirms ADH is ON — not ADH-independent.",
                3: "Cerebral salt wasting involves brain-mediated natriuresis causing HYPOVOLEMIA with high urine Na — the opposite of SIADH which is euvolemic. Without evidence of intracranial pathology and with euvolemic exam findings, CSW is not the diagnosis here.",
            },
            "final": True,
            "algo_img_pre": "step5hyponatremia.PNG",
            "algo_caption_pre": "You are here: Final diagnosis — SIADH pathway confirmed.",
        },
    ],

    "case4": [
        {
            "q": "A 37-year-old man with schizophrenia drinking 'gallons of water' daily has a Na⁺ of 119 mEq/L. What is the FIRST step?",
            "options": [
                "Check urine osmolality",
                "Check plasma osmolality",
                "Assess volume status",
                "Restrict free water"
            ],
            "correct": 1,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! Even with the obvious history of polydipsia, the algorithm always starts with <strong>plasma osmolality</strong>. The sequence matters because it trains systematic thinking — and because polydipsia is not the only cause of hyponatremia in a patient with schizophrenia. Antipsychotic medications (particularly older typical antipsychotics) can cause SIADH, which would require a completely different algorithmic path and treatment.",
            "wrong_fb": {
                0: "Urine osmolality (ADH status) is step 2, not step 1. You must confirm true hypotonic hyponatremia first.",
                2: "Volume status is step 3. Skipping the first two steps risks missing a co-existing cause like SIADH from his antipsychotic medication.",
                3: "Water restriction is appropriate treatment for psychogenic polydipsia — but treatment without diagnosis risks overcorrecting if the true cause is SIADH (which needs different management).",
            },
            "algo_img_pre": "step1hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 1 — Plasma osmolality. The algorithm starts here even when the cause seems obvious.",
            "unlock_lab": "Plasma Osm",
        },
        {
            "q": "Plasma osmolality is 260 mOsm/kg. A student says: 'This confirms psychogenic polydipsia — the plasma is diluted from water intake.' Is the reasoning correct?",
            "options": [
                "Yes — a plasma osm of 260 from massive water intake is pathognomonic of psychogenic polydipsia",
                "Partially — 260 confirms true hypotonic hyponatremia, but you cannot determine the cause from plasma osm alone",
                "No — psychogenic polydipsia would cause a normal plasma osm because the kidneys compensate immediately",
                "Partially — 260 could also represent mannitol or glucose infusion; check for those first"
            ],
            "correct": 1,
            "svg": "serum_osm_branches",
            "correct_fb": "Correct! The student is right that 260 mOsm/kg confirms <strong>true hypotonic hyponatremia</strong> — but wrong to jump to a specific diagnosis. Plasma osmolality tells you the TYPE of hyponatremia (hypotonic, isotonic, or hypertonic), not the CAUSE. Both psychogenic polydipsia and SIADH (which could be caused by his antipsychotic) would both show low plasma osm. The algorithm continues through ADH status, volume status, and urine sodium to distinguish them.",
            "wrong_fb": {
                0: "Incorrect. A low plasma osm confirms true dilution but is seen in MANY causes of hyponatremia including SIADH, CHF, GI losses, and polydipsia. It is not pathognomonic of any single cause.",
                2: "Incorrect. In severe polydipsia, the kidney's maximum water excretion capacity can be overwhelmed, causing the plasma osm to fall. His plasma osm of 260 confirms the kidneys cannot compensate fast enough.",
                3: "Mannitol and glucose cause hypertonic hyponatremia with HIGH plasma osm — the opposite of this patient's picture.",
            },
        },
        {
            "q": "True hypotonic hyponatremia is confirmed. What is the NEXT step, and why is the result particularly critical in this case?",
            "options": [
                "Check urine sodium",
                "Assess volume status",
                "Check urine osmolality",
                "Check serum potassium"
            ],
            "correct": 2,
            "svg": "urine_osm_adh",
            "correct_fb": "Correct! <strong>Urine osmolality is particularly critical here</strong> because it will definitively split two very different diagnoses: (1) if urine osm is LOW (<100) → ADH is OFF → ADH-independent → psychogenic polydipsia or beer potomania → algorithm ends here, no volume workup needed. (2) If urine osm is HIGH (>285) → ADH is ON → the algorithm continues through volume status and urine Na → could be SIADH from his antipsychotic. The entire diagnostic and treatment path hinges on this one result.",
            "wrong_fb": {
                0: "Urine sodium (RAAS status) is step 4. You cannot assess RAAS activity without first knowing ADH status (step 2) and volume status (step 3).",
                1: "Volume status comes after ADH status. And even if volume status seems obvious clinically, you need ADH status first to know whether volume assessment is even required.",
                3: "Hypokalemia from poor intake is possible, but checking potassium is not the next step in the hyponatremia algorithm.",
            },
            "algo_img_pre": "step2hyponatremia.PNG",
            "algo_caption_pre": "You are here: Step 2 — Urine osmolality. This result is the critical branch point in this case.",
            "unlock_lab": "Urine Osm",
        },
        {
            "q": "Urine osmolality is 55 mOsm/kg. His antipsychotic-prescribing psychiatrist insists this is SIADH from the medication. How do you respond?",
            "options": [
                "Agree — antipsychotics cause SIADH, and SIADH can present with suppressed ADH in some patients",
                "Disagree — SIADH requires ADH to be ON (urine osm >100–285); a urine osm of 55 proves ADH is maximally suppressed, ruling out SIADH",
                "Agree — a urine osm of 55 is borderline and could represent mild SIADH with partial ADH suppression",
                "Disagree — SIADH from antipsychotics only occurs with urine osm below 100; his 55 confirms it"
            ],
            "correct": 1,
            "svg": "adh_triggers",
            "correct_fb": "Correct! You respectfully disagree. <strong>SIADH by definition requires ADH to be inappropriately elevated</strong>, which concentrates the urine (urine osm >100, typically >285 mOsm/kg). A urine osm of 55 is maximally dilute — the kidneys are producing nearly pure water. This is the opposite of SIADH. ADH is completely suppressed. The psychiatrist's hypothesis is physiologically impossible given this result. This is ADH-independent hyponatremia from polydipsia overwhelming the kidneys' excretory capacity.",
            "wrong_fb": {
                0: "Incorrect. SIADH cannot present with suppressed ADH — that is a contradiction in terms. SIADH = Syndrome of Inappropriate ADH secretion = ADH must be active. A urine osm of 55 proves ADH is off.",
                2: "Incorrect. A urine osm of 55 is not borderline — it is at the extreme dilute end of the spectrum. There is no SIADH with a urine osm this low.",
                3: "Incorrect. SIADH from antipsychotics presents with HIGH urine osm (ADH ON), not low. The confusion here is that antipsychotics can cause SIADH, but this patient's labs show ADH-independent hyponatremia.",
            },
        },
        {
            "q": "Urine osm 55 (ADH OFF) + plasma osm 260 + polydipsia + crackers-and-juice diet. What is the diagnosis and the key pathophysiologic concept?",
            "options": [
                "SIADH from atypical antipsychotic",
                "Hypovolemic hyponatremia from poor dietary intake",
                "ADH-independent hyponatremia from psychogenic polydipsia with insufficient solute intake",
                "Hypervolemic hyponatremia from polydipsia"
            ],
            "correct": 2,
            "svg": "polydipsia_math",
            "correct_fb": "Correct! 🎉 This is <strong>ADH-independent hyponatremia from psychogenic polydipsia compounded by low solute intake</strong>. The key concept: to excrete 1 liter of free water, the kidneys need approximately 50–100 mOsm of solute to carry it out as dilute urine. His crackers-and-juice diet provides almost no osmoles. So even though ADH is completely suppressed and the kidneys are making maximally dilute urine (osm 55), the sheer volume of water he drinks exceeds the kidneys' excretory capacity. Treatment: <strong>behavioral counseling</strong> to reduce water intake, and increase dietary solute intake. Fluid restriction alone is insufficient.",
            "wrong_fb": {
                0: "SIADH requires ADH ON (urine osm >100-285). His urine osm of 55 proves ADH is off — SIADH is physiologically excluded.",
                1: "He is not volume-depleted — his exam shows normal vitals, moist membranes, no tachycardia. Saline would worsen his hyponatremia by adding more free water alongside the sodium.",
                3: "While his total body water is high, this is not 'hypervolemic' in the clinical sense. He has no edema, no JVD, no weight gain from sodium retention. The water excess here is from pure free water intake, not sodium-and-water retention.",
            },
            "final": True,
            "algo_img_pre": "step5hyponatremia.PNG",
            "algo_caption_pre": "You are here: Final diagnosis — ADH-independent pathway confirmed.",
        },
    ],
}


# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("## 💧 Hyponatremia Sim")
    st.markdown("---")

    total_q = st.session_state.total_questions
    correct = st.session_state.correct_answers
    pct = int(correct / total_q * 100) if total_q else 0

    st.markdown("### 📊 Session Stats")
    st.markdown(f"""
    <div class="stat-pill"><span class="s-label">Questions Answered</span><span class="s-value">{total_q}</span></div>
    <div class="stat-pill"><span class="s-label">Correct Answers</span><span class="s-value">{correct}</span></div>
    <div class="stat-pill"><span class="s-label">Accuracy</span><span class="s-value">{pct}%</span></div>
    """, unsafe_allow_html=True)

    if st.session_state.case_choice:
        case_id = st.session_state.case_choice
        steps = STEPS[case_id]
        total = len(steps)
        current = st.session_state.step - 1
        st.markdown("---")
        st.markdown("### 📋 Current Case")
        st.markdown(f"""
        <div class="stat-pill"><span class="s-label">Case</span><span class="s-value">{CASE_META[case_id]['label']}</span></div>
        <div class="stat-pill"><span class="s-label">Step</span><span class="s-value">{min(current+1, total)} / {total}</span></div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗂️ Cases")
    for cid, meta in CASE_META.items():
        if st.button(f"{meta['label']}", key=f"side_{cid}"):
            st.session_state.case_choice = cid
            st.session_state.step = 1
            st.session_state.answered = False
            st.session_state.last_correct = False
            st.session_state.visible_labs = ["Na⁺"]
            st.session_state.feedback_shown = False
            st.rerun()

    st.markdown("---")
    if st.button("🏠 Main Menu", key="sidebar_home"):
        st.session_state.step = 0
        st.session_state.answered = False
        st.rerun()

# ===============================
# MAIN APP
# ===============================

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
<h1>Hyponatremia Clinical Reasoning Simulator</h1>
<p>M2-Level · Algorithm-Based · Step-by-Step Diagnostic Reasoning · 4 Cases</p>
</div>
""", unsafe_allow_html=True)

# ── HOME SCREEN ──────────────────────────────────────────────────────────────
if st.session_state.step == 0:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("### Select a Case")
        st.markdown("Each case walks you through the hyponatremia algorithm step by step, from plasma osmolality through to final diagnosis.")
    with col_r:
        if st.session_state.total_questions > 0:
            st.markdown(f"""<div class="score-box" style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;text-align:center;">
            <div style="font-size:2.4rem;font-weight:700;color:var(--teal-light);">{correct}/{total_q}</div>
            <div style="color:var(--muted);font-size:0.82rem;">Questions Correct · {pct}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    cols = st.columns(4)
    for i, (cid, meta) in enumerate(CASE_META.items()):
        with cols[i]:
            st.markdown(f"""<div class="case-card">
                <h4>{meta['label']}</h4>
                <p>{meta['preview']}</p>
                <p style="margin-top:10px;font-size:0.75rem;color:var(--teal);">{len(STEPS[cid])} diagnostic steps</p>
            </div>""", unsafe_allow_html=True)
            if st.button(f"▶ Start {meta['label']}", key=f"home_{cid}"):
                st.session_state.case_choice = cid
                st.session_state.step = 1
                st.session_state.answered = False
                st.session_state.last_correct = False
                st.session_state.visible_labs = ["Na⁺"]
                if "feedback_shown" not in st.session_state:
                    st.session_state.feedback_shown = False
                else:
                    st.session_state.feedback_shown = False
                st.rerun()

    # Algorithm overview
    st.markdown("---")
    st.markdown("### 🧠 The Hyponatremia Algorithm")
    st.markdown("Each case follows the same diagnostic framework:")
    c1, c2, c3, c4, c5 = st.columns(5)
    steps_labels = [
        ("1", "Serum\nOsmolality", "Is it true hypotonic hyponatremia?"),
        ("2", "Urine\nOsmolality", "Is ADH on or off?"),
        ("3", "Volume\nStatus", "Hypo / Eu / Hypervolemic?"),
        ("4", "Urine\nSodium", "Is RAAS activated?"),
        ("5", "Final\nDiagnosis", "Integrate and conclude"),
    ]
    for col, (num, title, desc) in zip([c1,c2,c3,c4,c5], steps_labels):
        col.markdown(f"""<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;height:130px;">
        <div style="font-size:1.4rem;font-weight:700;color:var(--teal);">{num}</div>
        <div style="font-size:0.82rem;font-weight:600;color:var(--text);margin:4px 0;">{title}</div>
        <div style="font-size:0.72rem;color:var(--muted);">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ── CASE SCREEN ──────────────────────────────────────────────────────────────
else:
    if "feedback_shown" not in st.session_state:
        st.session_state.feedback_shown = False

    case_id = st.session_state.case_choice
    steps = STEPS[case_id]
    step_idx = st.session_state.step - 1  # 0-based index into steps list
    total_steps = len(steps)

    # Bounds check
    if step_idx >= total_steps:
        st.session_state.step = 0
        st.rerun()

    current = steps[step_idx]

    # Case header
    st.markdown(f"""
    <h2 style="margin-top:0;margin-bottom:4px;">{CASE_META[case_id]['label']}</h2>
    <p style="color:var(--muted);font-size:0.85rem;margin-bottom:16px;">{total_steps} diagnostic steps · Step {step_idx+1} of {total_steps}</p>
    """, unsafe_allow_html=True)

    # Progress bar
    step_bar(step_idx + 1, total_steps)

    # Vignette
    show_vignette()

    # Labs
    display_labs()

    # ── COMPLETION ────────────────────────────────────────────────────────
    if current.get("final") and st.session_state.answered and st.session_state.last_correct:
        st.markdown("""<div class="complete-banner">
        <h2>✅ Case Complete!</h2>
        <p style="color:#ECF0F1;font-size:1rem;">You've worked through the full hyponatremia algorithm for this case.</p>
        </div>""", unsafe_allow_html=True)
        st.balloons()

    # ── ALGORITHM IMAGE (shown before question to show where they are) ──
    if "algo_img_pre" in current:
        show_algo_image(current["algo_img_pre"], current.get("algo_caption_pre", ""))

    # ── QUESTION ──────────────────────────────────────────────────────────
    question_card(step_idx + 1, total_steps, current["q"])

    ans = st.radio("Select your answer:", current["options"], key=f"q_{case_id}_{step_idx}", index=None)

    col_submit, col_next = st.columns([1, 1])

    # Submit
    with col_submit:
        submit_disabled = (st.session_state.answered and st.session_state.last_correct) or ans is None
        if st.button("✅ Submit Answer", key=f"submit_{case_id}_{step_idx}", disabled=submit_disabled):
            selected_idx = current["options"].index(ans)
            is_correct = selected_idx == current["correct"]

            # Score only first attempt
            if not st.session_state.feedback_shown:
                st.session_state.total_questions += 1
                if is_correct:
                    st.session_state.correct_answers += 1
                st.session_state.feedback_shown = True

            if is_correct:
                st.session_state.answered = True
                st.session_state.last_correct = True
                st.session_state.feedback_html = ("correct", current["correct_fb"])

                # Unlock labs
                if "unlock_lab" in current:
                    lab = current["unlock_lab"]
                    if lab not in st.session_state.visible_labs:
                        st.session_state.visible_labs.append(lab)
                if "unlock_lab2" in current:
                    lab2 = current["unlock_lab2"]
                    if lab2 not in st.session_state.visible_labs:
                        st.session_state.visible_labs.append(lab2)
            else:
                wrong_fbs = current.get("wrong_fb", {})
                specific_fb = wrong_fbs.get(selected_idx, "Incorrect. Review the algorithm and try again.")
                st.session_state.feedback_html = ("wrong", specific_fb)
                st.session_state.last_correct = False

            st.rerun()

    # Next button
    with col_next:
        if st.session_state.answered and st.session_state.last_correct:
            if not current.get("final"):
                if st.button("Next Step ➡️", key=f"next_{case_id}_{step_idx}"):
                    st.session_state.step += 1
                    st.session_state.answered = False
                    st.session_state.last_correct = False
                    st.session_state.feedback_html = None
                    st.session_state.feedback_shown = False
                    st.rerun()
            else:
                if st.button("🏠 Return to Menu", key=f"menu_{case_id}_{step_idx}"):
                    st.session_state.step = 0
                    st.session_state.answered = False
                    st.session_state.last_correct = False
                    st.session_state.feedback_html = None
                    st.session_state.feedback_shown = False
                    st.rerun()

    # Feedback
    if hasattr(st.session_state, 'feedback_html') and st.session_state.feedback_html:
        kind, html = st.session_state.feedback_html
        if kind == "correct":
            st.markdown(f'<div class="feedback-correct">✅ &nbsp;{html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-wrong">❌ &nbsp;{html}</div>', unsafe_allow_html=True)
        # Render diagram if attached to this question
        if "svg" in current:
            render_diagram(current["svg"])



    st.markdown("---")
    if st.button("↩️ Return to Main Menu", key=f"back_{case_id}_{step_idx}"):
        st.session_state.step = 0
        st.session_state.answered = False
        st.session_state.last_correct = False
        st.session_state.feedback_html = None
        st.session_state.feedback_shown = False
        st.rerun()