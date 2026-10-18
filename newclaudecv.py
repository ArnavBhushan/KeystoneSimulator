import streamlit as st
import math

# ===============================
# SVG DIAGRAM LIBRARY
# ===============================
def svg_wrap(inner, width=800, height=280, title="", subtitle=""):
    header = ""
    if title:
        header += f'<text x="{width//2}" y="24" text-anchor="middle" font-family="Inter,sans-serif" font-size="14" font-weight="600" fill="#ECF0F1">{title}</text>'
    if subtitle:
        header += f'<text x="{width//2}" y="42" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#95A5A6">{subtitle}</text>'
    offset = 50 if (title or subtitle) else 0
    # Generous bottom padding so nothing ever clips
    total_h = height + offset + 80
    # NOTE: no height:100% on the svg -- let it size purely from width:100% + aspect ratio,
    # so preserveAspectRatio actually controls the rendered height instead of being
    # overridden by a forced container height that causes cropping.
    svg = f'''<svg viewBox="0 0 {width} {total_h}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet" style="width:100%;display:block;">
  <rect width="{width}" height="{total_h}" fill="#1A2638" rx="8"/>
  {header}
  <g transform="translate(0,{offset})">{inner}</g>
</svg>'''
    html = f'''<!DOCTYPE html><html><body style="margin:0;padding:0;background:#1A2638;box-sizing:border-box;">
<div style="background:#1A2638;border:1px solid #2C3E50;border-radius:10px;overflow:visible;">{svg}</div>
</body></html>'''
    # iframe height: SVG renders at (column width) x (column width * total_h/width).
    # We don\'t know exact column width, so assume a wide-ish 750px and add a safety margin
    # large enough that even a much narrower column still fits without cropping.
    aspect_h_per_w = total_h / width
    iframe_h = int(750 * aspect_h_per_w) + 60
    return html, iframe_h

def label(x, y, text, color="#95A5A6", size=10, anchor="middle", weight="normal"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Inter,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{text}</text>'

ARROW_DEFS = '<defs><marker id="ah" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#95A5A6"/></marker></defs>'

# ─────────────────────────────────────────────
# FRANK-STARLING CURVES
# ─────────────────────────────────────────────

def svg_frank_starling_hfref():
    W, H = 800, 350
    ox, oy = 100, 260
    ax_w, ax_h = 570, 210
    down_arrow = "&#8595;"
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+ax_w//2}" y="{oy+28}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">Left Ventricular End-Diastolic Pressure (Preload)</text>
  <text x="{ox-62}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-62},{oy-ax_h//2})">Stroke Volume / Cardiac Output</text>
  <path d="M {ox} {oy} Q {ox+180} {oy-185} {ox+440} {oy-200}" stroke="#1ABC9C" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M {ox} {oy} Q {ox+180} {oy-90} {ox+440} {oy-105}" stroke="#E74C3C" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="8,4"/>
  <!-- Dots exactly on curves at same x=ox+340 (same preload) -->
  <circle cx="{ox+340}" cy="{oy-187}" r="7" fill="#1ABC9C"/>
  <circle cx="{ox+340}" cy="{oy-96}" r="7" fill="#E74C3C"/>
  <!-- Vertical dashed line connecting the two dots -->
  <line x1="{ox+340}" y1="{oy-180}" x2="{ox+340}" y2="{oy-103}" stroke="#E67E22" stroke-width="2" stroke-dasharray="5,3"/>
  <text x="{ox+350}" y="{oy-138}" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">{down_arrow} SV at same preload</text>
  <line x1="{ox+460}" y1="{oy-198}" x2="{ox+490}" y2="{oy-198}" stroke="#1ABC9C" stroke-width="3"/>
  <text x="{ox+496}" y="{oy-194}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">Normal</text>
  <line x1="{ox+460}" y1="{oy-176}" x2="{ox+490}" y2="{oy-176}" stroke="#E74C3C" stroke-width="3" stroke-dasharray="8,4"/>
  <text x="{ox+496}" y="{oy-172}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">HFrEF</text>
  <text x="{ox+80}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">Low</text>
  <text x="{ox+280}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">Normal</text>
  <text x="{ox+480}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">High</text>
    '''
    return svg_wrap(inner, W, H, "Frank-Starling Curve: Normal vs. HFrEF", "In HFrEF, the curve is depressed -- same preload yields less cardiac output")

def svg_frank_starling_neurohormonal():
    W, H = 800, 350
    ox, oy = 100, 260
    ax_w, ax_h = 570, 210
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+ax_w//2}" y="{oy+28}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">LVEDP / Preload</text>
  <text x="{ox-62}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-62},{oy-ax_h//2})">Cardiac Output</text>
  <path d="M {ox} {oy} Q {ox+170} {oy-95} {ox+430} {oy-108}" stroke="#E74C3C" stroke-width="3" fill="none" stroke-linecap="round"/>
  <rect x="{ox+330}" y="{oy-ax_h}" width="200" height="{ax_h}" fill="rgba(192,57,43,0.07)" rx="2"/>
  <text x="{ox+380}" y="{oy-ax_h+18}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">Pulmonary</text>
  <text x="{ox+380}" y="{oy-ax_h+34}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">Congestion Zone</text>
  <circle cx="{ox+215}" cy="{oy-88}" r="7" fill="#E67E22"/>
  <text x="{ox+228}" y="{oy-95}" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">Before RAAS</text>
  <path d="M {ox+222} {oy-88} Q {ox+315} {oy-81} {ox+390} {oy-83}" stroke="#E67E22" stroke-width="2" fill="none" stroke-dasharray="5,3" marker-end="url(#ah)"/>
  <circle cx="{ox+390}" cy="{oy-83}" r="7" fill="#C0392B"/>
  <text x="{ox+400}" y="{oy-91}" font-family="Inter,sans-serif" font-size="11" fill="#C0392B">After RAAS</text>
  <path d="M {ox+383} {oy-83} Q {ox+308} {oy-89} {ox+222} {oy-88}" stroke="#1ABC9C" stroke-width="2" fill="none" stroke-dasharray="5,3" marker-end="url(#ah)"/>
  <text x="{ox+290}" y="{oy-104}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">Diuresis</text>
  <line x1="{ox+458}" y1="{oy-200}" x2="{ox+488}" y2="{oy-200}" stroke="#E74C3C" stroke-width="3"/>
  <text x="{ox+494}" y="{oy-196}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">HFrEF curve</text>
  <circle cx="{ox+473}" cy="{oy-178}" r="6" fill="#E67E22"/>
  <text x="{ox+484}" y="{oy-174}" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">Before RAAS</text>
  <circle cx="{ox+473}" cy="{oy-155}" r="6" fill="#C0392B"/>
  <text x="{ox+484}" y="{oy-151}" font-family="Inter,sans-serif" font-size="11" fill="#C0392B">After RAAS</text>
    '''
    return svg_wrap(inner, W, H, "Frank-Starling: Volume Overload from Neurohumoral Activation", "RAAS + SNS push the operating point rightward into the congestion zone")

def svg_frank_starling_four_pillars():
    W, H = 800, 360
    ox, oy = 100, 265
    ax_w, ax_h = 555, 215
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+ax_w//2}" y="{oy+28}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">LVEDP / Preload</text>
  <text x="{ox-62}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-62},{oy-ax_h//2})">Cardiac Output / Stroke Volume</text>
  <path d="M {ox} {oy} Q {ox+170} {oy-82} {ox+420} {oy-95}" stroke="#E74C3C" stroke-width="2.5" fill="none" stroke-dasharray="8,4"/>
  <path d="M {ox} {oy} Q {ox+170} {oy-148} {ox+420} {oy-165}" stroke="#1ABC9C" stroke-width="3" fill="none" stroke-linecap="round"/>
  <line x1="{ox+255}" y1="{oy-95}" x2="{ox+255}" y2="{oy-145}" stroke="#27AE60" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#ah)"/>
  <text x="{ox+264}" y="{oy-118}" font-family="Inter,sans-serif" font-size="11" fill="#27AE60">Reverse remodeling</text>
  <circle cx="{ox+255}" cy="{oy-88}" r="6" fill="#E74C3C"/>
  <circle cx="{ox+225}" cy="{oy-141}" r="6" fill="#1ABC9C"/>
  <rect x="{ox+435}" y="{oy-212}" width="165" height="98" rx="6" fill="rgba(26,188,156,0.08)" stroke="#1ABC9C" stroke-width="1.5"/>
  <text x="{ox+517}" y="{oy-196}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C" font-weight="600">4 Pillars of HFrEF Rx</text>
  <text x="{ox+445}" y="{oy-180}" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">&#9312; ARNI / ACEi / ARB</text>
  <text x="{ox+445}" y="{oy-164}" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">&#9313; Beta-blocker</text>
  <text x="{ox+445}" y="{oy-148}" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">&#9314; MRA (spironolactone)</text>
  <text x="{ox+445}" y="{oy-132}" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">&#9315; SGLT2 inhibitor</text>
  <line x1="{ox+435}" y1="{oy-100}" x2="{ox+465}" y2="{oy-100}" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="8,4"/>
  <text x="{ox+470}" y="{oy-96}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">Untreated HFrEF</text>
  <line x1="{ox+435}" y1="{oy-78}" x2="{ox+465}" y2="{oy-78}" stroke="#1ABC9C" stroke-width="3"/>
  <text x="{ox+470}" y="{oy-74}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">With GDMT</text>
    '''
    return svg_wrap(inner, W, H, "Frank-Starling: Effect of Guideline-Directed Therapy (GDMT)", "Four-pillar therapy shifts the curve upward -- reverse remodeling improves cardiac output")

# ─────────────────────────────────────────────
# PRESSURE-VOLUME LOOPS
# ─────────────────────────────────────────────

def svg_pv_loop_hfpef():
    W, H = 800, 360
    ox, oy = 110, 268
    ax_w, ax_h = 555, 218
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+ax_w//2}" y="{oy+28}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">LV Volume (mL)</text>
  <text x="{ox-66}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-66},{oy-ax_h//2})">LV Pressure (mmHg)</text>
  <text x="{ox+88}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">50</text>
  <text x="{ox+218}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">100</text>
  <text x="{ox+348}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">150</text>
  <text x="{ox+478}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">200</text>
  <path d="M {ox+118} {oy-22} L {ox+118} {oy-155} L {ox+305} {oy-155} L {ox+305} {oy-22} Z" stroke="#1ABC9C" stroke-width="2.5" fill="rgba(26,188,156,0.08)" stroke-linejoin="round"/>
  <path d="M {ox+40} {oy} Q {ox+215} {oy-26} {ox+410} {oy-64}" stroke="#1ABC9C" stroke-width="2" fill="none" stroke-dasharray="6,3" opacity="0.7"/>
  <path d="M {ox+102} {oy-60} L {ox+102} {oy-175} L {ox+255} {oy-175} L {ox+255} {oy-60} Z" stroke="#E74C3C" stroke-width="2.5" fill="rgba(231,76,60,0.08)" stroke-linejoin="round"/>
  <path d="M {ox+40} {oy} Q {ox+126} {oy-70} {ox+278} {oy-175}" stroke="#E74C3C" stroke-width="2" fill="none" stroke-dasharray="6,3" opacity="0.8"/>
  <text x="{ox+320}" y="{oy-165}" font-family="Inter,sans-serif" font-size="11" fill="#ECF0F1">Both have</text>
  <text x="{ox+320}" y="{oy-150}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">preserved EF</text>
  <line x1="{ox+255}" y1="{oy-60}" x2="{ox+435}" y2="{oy-60}" stroke="#E74C3C" stroke-width="1.5" stroke-dasharray="4,2"/>
  <line x1="{ox+118}" y1="{oy-22}" x2="{ox+435}" y2="{oy-22}" stroke="#1ABC9C" stroke-width="1.5" stroke-dasharray="4,2"/>
  <line x1="{ox+435}" y1="{oy-60}" x2="{ox+435}" y2="{oy-24}" stroke="#E67E22" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+443}" y="{oy-38}" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">EDP in HFpEF</text>
  <text x="{ox+160}" y="{oy-193}" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">HFpEF EDPVR (steep -- stiff)</text>
  <text x="{ox+348}" y="{oy-50}" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C" opacity="0.8">Normal EDPVR</text>
  <rect x="{ox+320}" y="{oy-132}" width="12" height="12" rx="2" fill="rgba(26,188,156,0.2)" stroke="#1ABC9C" stroke-width="1.5"/>
  <text x="{ox+337}" y="{oy-122}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">Normal</text>
  <rect x="{ox+320}" y="{oy-106}" width="12" height="12" rx="2" fill="rgba(231,76,60,0.2)" stroke="#E74C3C" stroke-width="1.5"/>
  <text x="{ox+337}" y="{oy-96}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">HFpEF</text>
    '''
    return svg_wrap(inner, W, H, "Pressure-Volume Loop: Normal vs. HFpEF", "Steep EDPVR = stiff ventricle. Same EF, but much higher filling pressures required")

def svg_pv_loop_mr():
    W, H = 800, 360
    ox, oy = 110, 268
    ax_w, ax_h = 555, 218
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox-66}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-66},{oy-ax_h//2})">LV Pressure (mmHg)</text>
  <path d="M {ox+108} {oy-20} L {ox+108} {oy-162} L {ox+275} {oy-162} L {ox+275} {oy-20} Z" stroke="#1ABC9C" stroke-width="2.5" fill="rgba(26,188,156,0.07)" stroke-linejoin="round"/>
  <path d="M {ox+152} {oy-22} L {ox+152} {oy-128} Q {ox+218} {oy-182} {ox+422} {oy-175} L {ox+422} {oy-22} Z" stroke="#E74C3C" stroke-width="2.5" fill="rgba(231,76,60,0.08)" stroke-linejoin="round"/>
  <!-- Orange line at same y as box bottoms (oy-20) to show wider EDV -->
  <line x1="{ox+108}" y1="{oy-20}" x2="{ox+422}" y2="{oy-20}" stroke="#E67E22" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="{ox+282}" y="{oy+16}" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">EDV -- chronic volume overload</text>
  <text x="{ox+ax_w//2}" y="{oy+32}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">LV Volume (mL)</text>
  <text x="{ox+45}" y="{oy-108}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">Regurgitant</text>
  <text x="{ox+45}" y="{oy-94}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">volume</text>
  <line x1="{ox+118}" y1="{oy-102}" x2="{ox+150}" y2="{oy-102}" stroke="#E74C3C" stroke-width="1.5" marker-end="url(#ah)"/>
  <rect x="{ox+285}" y="{oy-198}" width="12" height="12" rx="2" fill="rgba(26,188,156,0.2)" stroke="#1ABC9C" stroke-width="1.5"/>
  <text x="{ox+302}" y="{oy-188}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">Normal</text>
  <rect x="{ox+285}" y="{oy-170}" width="12" height="12" rx="2" fill="rgba(231,76,60,0.2)" stroke="#E74C3C" stroke-width="1.5"/>
  <text x="{ox+302}" y="{oy-160}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">Mitral Regurgitation</text>
    '''
    return svg_wrap(inner, W, H, "Pressure-Volume Loop: Mitral Regurgitation", "MR loop is wider and shifted right -- chronic LV volume overload drives eccentric dilation")

def svg_pv_loop_ar():
    W, H = 800, 370
    ox, oy = 110, 272
    ax_w, ax_h = 548, 224
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+ax_w//2}" y="{oy+50}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">LV Volume (mL)</text>
  <text x="{ox-66}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-66},{oy-ax_h//2})">LV Pressure (mmHg)</text>
  <path d="M {ox+78} {oy-18} L {ox+78} {oy-155} L {ox+240} {oy-155} L {ox+240} {oy-18} Z" stroke="#1ABC9C" stroke-width="2.5" fill="rgba(26,188,156,0.07)" stroke-linejoin="round"/>
  <path d="M {ox+118} {oy-14} L {ox+118} {oy-198} L {ox+408} {oy-198} L {ox+408} {oy-14} Z" stroke="#E74C3C" stroke-width="2.5" fill="rgba(231,76,60,0.08)" stroke-linejoin="round"/>
  <line x1="{ox+422}" y1="{oy-198}" x2="{ox+422}" y2="{oy-14}" stroke="#E67E22" stroke-width="2"/>
  <line x1="{ox+415}" y1="{oy-198}" x2="{ox+429}" y2="{oy-198}" stroke="#E67E22" stroke-width="1.5"/>
  <line x1="{ox+415}" y1="{oy-14}" x2="{ox+429}" y2="{oy-14}" stroke="#E67E22" stroke-width="1.5"/>
  <text x="{ox+435}" y="{oy-118}" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">Wide pulse</text>
  <text x="{ox+435}" y="{oy-104}" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">pressure</text>
  <line x1="{ox+78}" y1="{oy+12}" x2="{ox+408}" y2="{oy+12}" stroke="#E67E22" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="{ox+244}" y="{oy+26}" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#E67E22">Massive EDV (regurgitant vol + venous return)</text>
  <rect x="{ox+152}" y="{oy-215}" width="12" height="12" rx="2" fill="rgba(26,188,156,0.2)" stroke="#1ABC9C" stroke-width="1.5"/>
  <text x="{ox+169}" y="{oy-205}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">Normal</text>
  <rect x="{ox+255}" y="{oy-215}" width="12" height="12" rx="2" fill="rgba(231,76,60,0.2)" stroke="#E74C3C" stroke-width="1.5"/>
  <text x="{ox+272}" y="{oy-205}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">Aortic Regurgitation</text>
    '''
    return svg_wrap(inner, W, H, "Pressure-Volume Loop: Aortic Regurgitation", "AR loop is massively widened -- huge EDV from regurgitant volume, wide pulse pressure")

def svg_pv_loop_as():
    W, H = 800, 360
    ox, oy = 110, 268
    ax_w, ax_h = 548, 218
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+ax_w//2}" y="{oy+28}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">LV Volume (mL)</text>
  <text x="{ox-66}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-66},{oy-ax_h//2})">LV Pressure (mmHg)</text>
  <path d="M {ox+175} {oy-20} L {ox+175} {oy-148} L {ox+333} {oy-148} L {ox+333} {oy-20} Z" stroke="#1ABC9C" stroke-width="2.5" fill="rgba(26,188,156,0.07)" stroke-linejoin="round"/>
  <path d="M {ox+163} {oy-18} L {ox+163} {oy-208} L {ox+321} {oy-208} L {ox+321} {oy-18} Z" stroke="#E74C3C" stroke-width="2.5" fill="rgba(231,76,60,0.08)" stroke-linejoin="round"/>
  <line x1="{ox+338}" y1="{oy-208}" x2="{ox+338}" y2="{oy-148}" stroke="#E67E22" stroke-width="2"/>
  <line x1="{ox+331}" y1="{oy-208}" x2="{ox+345}" y2="{oy-208}" stroke="#E67E22" stroke-width="1.5"/>
  <line x1="{ox+331}" y1="{oy-148}" x2="{ox+345}" y2="{oy-148}" stroke="#E67E22" stroke-width="1.5"/>
  <text x="{ox+350}" y="{oy-188}" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">Trans-valvular</text>
  <text x="{ox+350}" y="{oy-174}" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">pressure gradient</text>
  <text x="{ox+350}" y="{oy-160}" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">&gt;= 40 mmHg = severe</text>
  <text x="{ox+46}" y="{oy-198}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">LV systolic pressure</text>
  <text x="{ox+46}" y="{oy-184}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">concentric hypertrophy</text>
  <rect x="{ox+350}" y="{oy-134}" width="12" height="12" rx="2" fill="rgba(26,188,156,0.2)" stroke="#1ABC9C" stroke-width="1.5"/>
  <text x="{ox+367}" y="{oy-124}" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">Normal</text>
  <rect x="{ox+350}" y="{oy-108}" width="12" height="12" rx="2" fill="rgba(231,76,60,0.2)" stroke="#E74C3C" stroke-width="1.5"/>
  <text x="{ox+367}" y="{oy-98}" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">Aortic Stenosis</text>
    '''
    return svg_wrap(inner, W, H, "Pressure-Volume Loop: Aortic Stenosis", "Tall narrow loop = pressure overload. LV generates supranormal pressure to overcome obstruction")

# ─────────────────────────────────────────────
# ECG TRACINGS
# ─────────────────────────────────────────────

def _ecg_baseline(ox, oy, total_w, grid_h=160):
    lines = ""
    for i in range(0, total_w, 20):
        lines += f'<line x1="{ox+i}" y1="{oy-grid_h}" x2="{ox+i}" y2="{oy}" stroke="#1E3A2F" stroke-width="0.5"/>'
    for j in range(0, grid_h+1, 20):
        lines += f'<line x1="{ox}" y1="{oy-j}" x2="{ox+total_w}" y2="{oy-j}" stroke="#1E3A2F" stroke-width="0.5"/>'
    for i in range(0, total_w+1, 100):
        lines += f'<line x1="{ox+i}" y1="{oy-grid_h}" x2="{ox+i}" y2="{oy}" stroke="#1E4A38" stroke-width="1"/>'
    for j in range(0, grid_h+1, 40):
        lines += f'<line x1="{ox}" y1="{oy-j}" x2="{ox+total_w}" y2="{oy-j}" stroke="#1E4A38" stroke-width="1"/>'
    lines += f'<rect x="{ox}" y="{oy-grid_h}" width="{total_w}" height="{grid_h}" fill="none" stroke="#2C4A38" stroke-width="1.5" rx="2"/>'
    return lines

def svg_ecg_normal_sinus():
    W, H = 800, 315
    ox, oy = 28, 222
    grid_w = 745
    grid = _ecg_baseline(ox, oy, grid_w, 172)
    baseline = oy - 50

    def beat(start):
        s = start
        return f'''
      <path d="M{s},{baseline} Q{s+14},{baseline-18} {s+28},{baseline}" stroke="#00FF88" stroke-width="2" fill="none"/>
      <line x1="{s+28}" y1="{baseline}" x2="{s+44}" y2="{baseline}" stroke="#00FF88" stroke-width="2"/>
      <polyline points="{s+44},{baseline} {s+50},{baseline+9} {s+57},{baseline-62} {s+63},{baseline+11} {s+70},{baseline}" stroke="#00FF88" stroke-width="2.5" fill="none"/>
      <line x1="{s+70}" y1="{baseline}" x2="{s+86}" y2="{baseline}" stroke="#00FF88" stroke-width="2"/>
      <path d="M{s+86},{baseline} Q{s+102},{baseline-26} {s+118},{baseline}" stroke="#00FF88" stroke-width="2" fill="none"/>
    '''

    beats = "".join(beat(ox + 10 + i * 172) for i in range(4))
    inner = f'''{grid}{beats}
  <text x="{ox+14}" y="{oy-164}" font-family="Inter,sans-serif" font-size="11" fill="#95A5A6">Lead II  25mm/s</text>
  <text x="{ox+55}" y="{oy-116}" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">P</text>
  <text x="{ox+72}" y="{oy+14}" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">Q</text>
  <text x="{ox+80}" y="{oy-114}" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">R</text>
  <text x="{ox+90}" y="{oy+18}" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">S</text>
  <text x="{ox+114}" y="{oy-66}" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">T</text>
  <text x="{ox+500}" y="{oy+14}" font-family="Inter,sans-serif" font-size="10" fill="#00FF88" font-weight="600">Normal Sinus Rhythm -- Regular, ~75 bpm</text>
    '''
    return svg_wrap(inner, W, H, "ECG: Normal Sinus Rhythm (Lead II)", "Regular P waves before each QRS  PR interval 120-200 ms  Rate 60-100 bpm")

def svg_ecg_afib():
    import math as _math
    W, H = 800, 315
    ox, oy = 28, 222
    grid_w = 745
    grid = _ecg_baseline(ox, oy, grid_w, 172)
    baseline = oy - 50

    fib = f'<path d="M{ox+10},{baseline}'
    x = ox + 10
    while x < ox + grid_w - 10:
        amp = 5 if (int(x) % 7 < 3) else 2
        y = baseline - amp * _math.sin((x - ox) * 0.65 + 0.3)
        fib += f' L{x:.0f},{y:.1f}'
        x += 2
    fib += '" stroke="#00FF88" stroke-width="1.2" fill="none" opacity="0.7"/>'

    qrs_positions = [ox+55, ox+185, ox+290, ox+415, ox+500, ox+605, ox+685]
    qrs = ""
    for s in qrs_positions:
        qrs += f'<polyline points="{s},{baseline} {s+6},{baseline+12} {s+12},{baseline-60} {s+18},{baseline+14} {s+24},{baseline}" stroke="#00FF88" stroke-width="2.5" fill="none"/>'
        qrs += f'<path d="M{s+24},{baseline} Q{s+38},{baseline-18} {s+52},{baseline}" stroke="#00FF88" stroke-width="1.8" fill="none"/>'

    rr_ann = ""
    for x1, x2, txt in [(ox+55,ox+185,"RR=0.43s"),(ox+185,ox+290,"RR=0.31s"),(ox+415,ox+500,"RR=0.26s"),(ox+605,ox+685,"RR=0.24s")]:
        mid = (x1+x2+24)//2
        rr_ann += f'<line x1="{x1+24}" y1="{oy-8}" x2="{x2}" y2="{oy-8}" stroke="#E67E22" stroke-width="1" stroke-dasharray="3,2"/>'
        rr_ann += f'<text x="{mid}" y="{oy+6}" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E67E22">{txt}</text>'

    inner = f'''{grid}{fib}{qrs}{rr_ann}
  <text x="{ox+14}" y="{oy-164}" font-family="Inter,sans-serif" font-size="11" fill="#95A5A6">Lead II</text>
  <text x="{ox+310}" y="{oy-132}" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">No discrete P waves</text>
  <text x="{ox+310}" y="{oy-118}" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">Irregularly irregular RR intervals</text>
  <text x="{ox+310}" y="{oy-104}" font-family="Inter,sans-serif" font-size="10" fill="#00FF88">Narrow QRS (AV node intact)</text>
    '''
    return svg_wrap(inner, W, H, "ECG: Atrial Fibrillation (Lead II)", "Absent P waves  Fibrillatory baseline  Irregularly irregular ventricular response")

def svg_ecg_stemi():
    W, H = 800, 318
    ox, oy = 28, 224
    grid_w = 745
    grid = _ecg_baseline(ox, oy, grid_w, 174)
    baseline = oy - 52

    def stemi_beat(start, label, st_elev=30):
        s = start
        st_y = baseline - st_elev
        st_y2 = st_y - 22
        return f'''
      <path d="M{s},{baseline} Q{s+11},{baseline-14} {s+22},{baseline}" stroke="#00FF88" stroke-width="1.8" fill="none"/>
      <line x1="{s+22}" y1="{baseline}" x2="{s+35}" y2="{baseline}" stroke="#00FF88" stroke-width="1.8"/>
      <polyline points="{s+35},{baseline} {s+40},{baseline+9} {s+45},{baseline-58} {s+50},{baseline+7} {s+55},{baseline}" stroke="#00FF88" stroke-width="2.5" fill="none"/>
      <path d="M{s+55},{baseline} L{s+70},{st_y} L{s+84},{st_y}" stroke="#E74C3C" stroke-width="2.2" fill="none"/>
      <path d="M{s+84},{st_y} Q{s+99},{st_y2} {s+116},{baseline}" stroke="#E74C3C" stroke-width="2" fill="none"/>
      <text x="{s+6}" y="{oy-166}" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">{label}</text>
    '''

    def normal_beat(start, label):
        s = start
        return f'''
      <path d="M{s},{baseline} Q{s+11},{baseline-13} {s+22},{baseline}" stroke="#00FF88" stroke-width="1.8" fill="none"/>
      <line x1="{s+22}" y1="{baseline}" x2="{s+35}" y2="{baseline}" stroke="#00FF88" stroke-width="1.8"/>
      <polyline points="{s+35},{baseline} {s+40},{baseline+9} {s+45},{baseline-58} {s+50},{baseline+7} {s+55},{baseline}" stroke="#00FF88" stroke-width="2.5" fill="none"/>
      <line x1="{s+55}" y1="{baseline}" x2="{s+70}" y2="{baseline}" stroke="#00FF88" stroke-width="1.8"/>
      <path d="M{s+70},{baseline} Q{s+84},{baseline-18} {s+98},{baseline}" stroke="#00FF88" stroke-width="1.8" fill="none"/>
      <text x="{s+6}" y="{oy-166}" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">{label}</text>
    '''

    beats  = normal_beat(ox+8,   "V1")
    beats += stemi_beat(ox+158,  "V2", st_elev=30)
    beats += stemi_beat(ox+308,  "V3", st_elev=36)
    beats += stemi_beat(ox+458,  "V4", st_elev=33)
    beats += stemi_beat(ox+608,  "V5", st_elev=24)

    ann = f'''
  <line x1="{ox+228}" y1="{baseline-30}" x2="{ox+228}" y2="{baseline-2}" stroke="#E74C3C" stroke-width="1.5" stroke-dasharray="3,2"/>
  <text x="{ox+234}" y="{baseline-14}" font-family="Inter,sans-serif" font-size="9" fill="#E74C3C">ST up ~3mm</text>
  <text x="{ox+390}" y="{oy+14}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C" font-weight="600">ST elevation V2-V5 -- Anterior STEMI (LAD territory)</text>
    '''
    inner = f'''{grid}{beats}{ann}'''
    return svg_wrap(inner, W, H, "ECG: Anterior STEMI -- ST Elevation V2-V5", "Convex ST elevation in V2-V5  LAD occlusion  Tombstoning pattern in severe cases")

def svg_ecg_pericarditis():
    W, H = 800, 318
    ox, oy = 28, 224
    grid_w = 745
    grid = _ecg_baseline(ox, oy, grid_w, 174)
    baseline = oy - 52

    def peri_beat(start, label, pr_depr=9, st_elev=20):
        s = start
        pr_y = baseline + pr_depr
        st_y = baseline - st_elev
        st_mid = st_y + 8
        return f'''
      <path d="M{s},{baseline} Q{s+11},{baseline-13} {s+22},{baseline}" stroke="#00FF88" stroke-width="1.8" fill="none"/>
      <line x1="{s+22}" y1="{baseline}" x2="{s+28}" y2="{baseline}" stroke="#00FF88" stroke-width="1.8"/>
      <line x1="{s+28}" y1="{baseline}" x2="{s+37}" y2="{pr_y}" stroke="#00FF88" stroke-width="1.8"/>
      <line x1="{s+37}" y1="{pr_y}" x2="{s+42}" y2="{pr_y}" stroke="#00FF88" stroke-width="1.8"/>
      <polyline points="{s+42},{pr_y} {s+47},{pr_y+8} {s+52},{pr_y-54} {s+57},{pr_y+6} {s+62},{pr_y}" stroke="#00FF88" stroke-width="2.5" fill="none"/>
      <line x1="{s+62}" y1="{pr_y}" x2="{s+68}" y2="{pr_y}" stroke="#00FF88" stroke-width="1.5"/>
      <path d="M{s+68},{pr_y} Q{s+84},{st_mid} {s+100},{st_y}" stroke="#E67E22" stroke-width="2.2" fill="none"/>
      <path d="M{s+100},{st_y} Q{s+114},{st_y+4} {s+128},{baseline}" stroke="#E67E22" stroke-width="1.8" fill="none"/>
      <text x="{s+6}" y="{oy-166}" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">{label}</text>
    '''

    beats = "".join(peri_beat(ox+8+i*148, lbl) for i, lbl in enumerate(["I","II","aVF","V4","V5"]))
    ann = f'''
  <text x="{ox+175}" y="{baseline-54}" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">Concave (saddle-shaped) ST elevation</text>
  <text x="{ox+40}" y="{oy+8}" font-family="Inter,sans-serif" font-size="9" fill="#9B59B6">PR depression</text>
  <text x="{ox+380}" y="{oy+14}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E67E22" font-weight="600">Diffuse across all leads -- not limited to one territory</text>
    '''
    inner = f'''{grid}{beats}{ann}'''
    return svg_wrap(inner, W, H, "ECG: Acute Pericarditis -- Diffuse Saddle-Shaped ST Elevation", "Concave ST elevation in all leads  PR depression (atrial inflammation)  No reciprocal changes")

def svg_ecg_stemi_vs_peri():
    W, H = 800, 310
    inner = f'''
  <rect x="20" y="10" width="370" height="230" rx="8" fill="rgba(192,57,43,0.08)" stroke="#E74C3C" stroke-width="1.5"/>
  <text x="205" y="32" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#E74C3C" font-weight="600">STEMI -- Convex ST Elevation</text>
  <line x1="40" y1="150" x2="370" y2="150" stroke="#2C4A38" stroke-width="1"/>
  <polyline points="55,150 62,164 70,88 78,166 86,150" stroke="#00FF88" stroke-width="2.5" fill="none"/>
  <path d="M86,150 Q114,78 144,82 L164,150" stroke="#E74C3C" stroke-width="3" fill="rgba(192,57,43,0.1)"/>
  <text x="118" y="72" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">Convex (tombstone)</text>
  <text x="205" y="196" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">Focal  One territory  Reciprocal STD</text>
  <text x="205" y="214" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C" font-weight="600">STEMI until proven otherwise</text>

  <rect x="410" y="10" width="370" height="230" rx="8" fill="rgba(230,126,34,0.08)" stroke="#E67E22" stroke-width="1.5"/>
  <text x="595" y="32" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#E67E22" font-weight="600">Pericarditis -- Concave ST Elevation</text>
  <line x1="430" y1="150" x2="760" y2="150" stroke="#2C4A38" stroke-width="1"/>
  <polyline points="445,150 452,163 460,90 468,165 476,150" stroke="#00FF88" stroke-width="2.5" fill="none"/>
  <line x1="432" y1="150" x2="445" y2="158" stroke="#9B59B6" stroke-width="2"/>
  <text x="426" y="174" font-family="Inter,sans-serif" font-size="9" fill="#9B59B6">PR depression</text>
  <path d="M476,150 Q494,128 514,112 Q534,98 554,112 L568,150" stroke="#E67E22" stroke-width="3" fill="rgba(230,126,34,0.1)"/>
  <text x="522" y="88" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">Concave (saddle)</text>
  <text x="595" y="196" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">Diffuse  All leads  PR depression</text>
  <text x="595" y="214" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E67E22" font-weight="600">No reciprocal ST depression</text>
    '''
    return svg_wrap(inner, W, H, "ECG Morphology: STEMI vs. Pericarditis", "The shape and distribution of ST changes are the key differentiating features")

# ─────────────────────────────────────────────
# ABI DIAGRAM
# ─────────────────────────────────────────────

def svg_abi_diagram():
    W, H = 800, 330
    inner = f'''
  <rect x="20" y="10" width="330" height="255" rx="8" fill="rgba(26,188,156,0.05)" stroke="#2C3E50" stroke-width="1.5"/>
  <text x="185" y="32" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1" font-weight="600">How ABI is Measured</text>
  <rect x="60" y="50" width="90" height="26" rx="4" fill="#1ABC9C" opacity="0.5"/>
  <text x="105" y="66" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">Brachial SBP</text>
  <text x="105" y="90" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C">e.g. 130 mmHg</text>
  <rect x="60" y="192" width="90" height="26" rx="4" fill="#E74C3C" opacity="0.5"/>
  <text x="105" y="208" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">Ankle SBP (DP/PT)</text>
  <text x="105" y="232" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C">e.g. 84 mmHg</text>
  <text x="220" y="128" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1">Ankle SBP</text>
  <line x1="165" y1="140" x2="275" y2="140" stroke="#95A5A6" stroke-width="2"/>
  <text x="220" y="162" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1">Brachial SBP</text>
  <text x="305" y="148" text-anchor="middle" font-family="Inter,sans-serif" font-size="22" fill="#E67E22" font-weight="700">= ABI</text>
  <text x="305" y="166" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#E67E22">0.65</text>
  <rect x="365" y="10" width="415" height="255" rx="8" fill="rgba(26,188,156,0.05)" stroke="#2C3E50" stroke-width="1.5"/>
  <text x="572" y="32" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1" font-weight="600">ABI Interpretation Scale</text>
  <rect x="382" y="48" width="72" height="26" rx="3" fill="#C0392B"/>
  <text x="418" y="64" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#fff">&lt; 0.4</text>
  <text x="418" y="86" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#C0392B">Critical ischemia</text>
  <rect x="460" y="48" width="72" height="26" rx="3" fill="#E74C3C"/>
  <text x="496" y="64" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#fff">0.4-0.69</text>
  <text x="496" y="86" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E74C3C">Mod-Severe PAD</text>
  <rect x="538" y="48" width="72" height="26" rx="3" fill="#E67E22"/>
  <text x="574" y="64" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#fff">0.7-0.89</text>
  <text x="574" y="86" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E67E22">Mild-Mod PAD</text>
  <rect x="616" y="48" width="72" height="26" rx="3" fill="#27AE60"/>
  <text x="652" y="64" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#fff">0.9-1.4</text>
  <text x="652" y="86" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#27AE60">Normal</text>
  <rect x="694" y="48" width="68" height="26" rx="3" fill="#2C3E50" stroke="#95A5A6" stroke-width="1"/>
  <text x="728" y="64" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">&gt; 1.4</text>
  <text x="728" y="86" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">Non-compressible</text>
  <defs><marker id="ah2" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#ECF0F1"/></marker></defs>
  <line x1="496" y1="100" x2="496" y2="118" stroke="#ECF0F1" stroke-width="2" marker-end="url(#ah2)"/>
  <text x="496" y="136" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1" font-weight="600">Patient ABI = 0.65</text>
  <text x="496" y="152" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">Moderate-Severe PAD confirmed</text>
  <text x="375" y="178" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">- First-line, non-invasive, bedside test</text>
  <text x="375" y="196" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">- Use the higher of dorsalis pedis and posterior tibial</text>
  <text x="375" y="214" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">- ABI &gt;1.4 = calcified vessels (DM/CKD): order TBI</text>
  <text x="375" y="232" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">- ABI &lt;0.9 = PAD confirmed; refer for vascular evaluation</text>
    '''
    return svg_wrap(inner, W, H, "Ankle-Brachial Index (ABI): Measurement and Interpretation", "")

# ─────────────────────────────────────────────
# TROPONIN RISE CURVE
# ─────────────────────────────────────────────

def svg_troponin_curve():
    W, H = 800, 350
    ox, oy = 100, 258
    ax_w, ax_h = 575, 210
    inner = f'''
  {ARROW_DEFS}
  <line x1="{ox}" y1="{oy-ax_h}" x2="{ox}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="#2C3E50" stroke-width="2" marker-end="url(#ah)"/>
  <text x="{ox+ax_w//2}" y="{oy+28}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6">Hours after symptom onset</text>
  <text x="{ox-62}" y="{oy-ax_h//2}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#95A5A6" transform="rotate(-90,{ox-62},{oy-ax_h//2})">Serum Troponin Level</text>
  <text x="{ox}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">0h</text>
  <text x="{ox+96}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">3h</text>
  <text x="{ox+192}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">6h</text>
  <text x="{ox+288}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">12h</text>
  <text x="{ox+384}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">24h</text>
  <text x="{ox+480}" y="{oy+18}" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#555">48h</text>
  <line x1="{ox}" y1="{oy-22}" x2="{ox+ax_w-12}" y2="{oy-22}" stroke="#E67E22" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="{ox+ax_w+2}" y="{oy-18}" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">ULN</text>
  <path d="M {ox} {oy-14} L {ox+ax_w-32} {oy-14}" stroke="#1ABC9C" stroke-width="2.5" fill="none" stroke-dasharray="8,4"/>
  <text x="{ox+516}" y="{oy-30}" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">Unstable Angina</text>
  <text x="{ox+516}" y="{oy-16}" font-family="Inter,sans-serif" font-size="9" fill="#1ABC9C">(troponin negative)</text>
  <path d="M {ox} {oy-14} L {ox+96} {oy-14} Q {ox+154} {oy-28} {ox+192} {oy-74} Q {ox+258} {oy-185} {ox+328} {oy-192} Q {ox+402} {oy-185} {ox+480} {oy-106} L {ox+555} {oy-48}" stroke="#E74C3C" stroke-width="3" fill="none" stroke-linecap="round"/>
  <text x="{ox+330}" y="{oy-200}" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C" font-weight="600">STEMI / NSTEMI</text>
  <text x="{ox+330}" y="{oy-186}" font-family="Inter,sans-serif" font-size="9" fill="#E74C3C">(troponin rises, peaks, then falls)</text>
  <line x1="{ox+96}" y1="{oy-22}" x2="{ox+96}" y2="{oy-70}" stroke="#95A5A6" stroke-width="1" stroke-dasharray="3,2"/>
  <text x="{ox+100}" y="{oy-52}" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">First rise ~3-6h</text>
  <line x1="{ox+328}" y1="{oy}" x2="{ox+328}" y2="{oy-192}" stroke="#95A5A6" stroke-width="1" stroke-dasharray="3,2"/>
  <text x="{ox+332}" y="{oy-172}" font-family="Inter,sans-serif" font-size="9" fill="#95A5A6">Peak ~12-24h</text>
    '''
    return svg_wrap(inner, W, H, "Troponin Kinetics: MI vs. Unstable Angina", "Troponin rises ONLY with myocardial necrosis -- this is what separates MI from UA")

# ─────────────────────────────────────────────
# MURMUR COMPARISON
# ─────────────────────────────────────────────

def svg_murmur_timing():
    W, H = 800, 325
    inner = f'''
  <text x="400" y="24" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#ECF0F1" font-weight="600">Murmur Timing in the Cardiac Cycle</text>
  <rect x="30" y="44" width="16" height="58" rx="3" fill="#ECF0F1" opacity="0.7"/>
  <text x="38" y="114" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#ECF0F1">S1</text>
  <rect x="30" y="120" width="16" height="58" rx="3" fill="#ECF0F1" opacity="0.35"/>
  <text x="38" y="190" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#ECF0F1">S1</text>
  <rect x="46" y="34" width="220" height="78" rx="3" fill="rgba(231,76,60,0.07)"/>
  <text x="156" y="48" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">SYSTOLE</text>
  <rect x="266" y="34" width="246" height="78" rx="3" fill="rgba(26,188,156,0.06)"/>
  <text x="389" y="48" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">DIASTOLE</text>
  <rect x="46" y="110" width="220" height="78" rx="3" fill="rgba(231,76,60,0.07)"/>
  <rect x="266" y="110" width="246" height="78" rx="3" fill="rgba(26,188,156,0.06)"/>
  <rect x="266" y="34" width="16" height="58" rx="3" fill="#ECF0F1" opacity="0.7"/>
  <text x="274" y="104" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#ECF0F1">S2</text>
  <rect x="266" y="110" width="16" height="58" rx="3" fill="#ECF0F1" opacity="0.7"/>
  <text x="274" y="180" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#ECF0F1">S2</text>
  <path d="M 46,102 Q 156,52 266,102" stroke="#E74C3C" stroke-width="3" fill="rgba(231,76,60,0.12)"/>
  <text x="524" y="78" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C" font-weight="600">Aortic Stenosis</text>
  <text x="524" y="94" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">Crescendo-decrescendo systolic</text>
  <text x="524" y="108" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">Radiates to carotids  RUSB</text>
  <line x1="266" y1="77" x2="520" y2="86" stroke="#E74C3C" stroke-width="0.8" stroke-dasharray="3,2" opacity="0.5"/>
  <rect x="46" y="132" width="220" height="32" rx="3" fill="rgba(231,76,60,0.18)" stroke="#E67E22" stroke-width="2"/>
  <text x="156" y="152" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E67E22">Holosystolic (pansystolic)</text>
  <text x="524" y="148" font-family="Inter,sans-serif" font-size="11" fill="#E67E22" font-weight="600">Mitral Regurgitation</text>
  <text x="524" y="164" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">Holosystolic  Apex to axilla</text>
  <line x1="266" y1="148" x2="520" y2="156" stroke="#E67E22" stroke-width="0.8" stroke-dasharray="3,2" opacity="0.5"/>
  <path d="M 282,222 Q 326,207 382,237" stroke="#9B59B6" stroke-width="3" fill="none"/>
  <text x="524" y="212" font-family="Inter,sans-serif" font-size="11" fill="#9B59B6" font-weight="600">Aortic Regurgitation</text>
  <text x="524" y="228" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">Early diastolic decrescendo</text>
  <text x="524" y="244" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">Left sternal border</text>
  <line x1="382" y1="222" x2="520" y2="220" stroke="#9B59B6" stroke-width="0.8" stroke-dasharray="3,2" opacity="0.5"/>
    '''
    return svg_wrap(inner, W, H, "", "")



# ===============================
# PAGE CONFIG & CUSTOM CSS
# ===============================
st.set_page_config(
    page_title="Cardiovascular Physiology Simulator",
    layout="wide",
    page_icon="🫀",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, .stApp {
        background-color: #1A2638 !important;
        font-family: 'Inter', sans-serif;
        color: #ECF0F1;
    }

    [data-testid="stSidebar"] {
        background: #243447 !important;
        border-right: 1px solid #2C3E50;
    }
    [data-testid="stSidebar"] * { color: #ECF0F1 !important; }

    p, li, label, div, span { color: #ECF0F1; }
    h1, h2, h3, h4, h5 { color: #ECF0F1 !important; font-weight: 600; }

    .app-header {
        background: linear-gradient(135deg, #C0392B 0%, #243447 60%);
        padding: 28px 32px 20px;
        border-radius: 12px;
        margin-bottom: 28px;
        border: 1px solid #C0392B;
        position: relative;
        overflow: hidden;
    }
    .app-header::before {
        content: "🫀";
        position: absolute;
        right: 24px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 72px;
        opacity: 0.15;
    }
    .app-header h1 { font-size: 2.1rem !important; font-weight: 700 !important; margin: 0 0 6px !important; }
    .app-header p { color: rgba(236,240,241,0.75) !important; font-size: 0.95rem; margin: 0; }

    .case-card {
        background: #1E2E42;
        border: 1px solid #2C3E50;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }
    .case-card h4 { margin: 0 0 6px; font-size: 0.95rem; }

    .vignette-box {
        background: #1E2E42;
        border: 1px solid #2C3E50;
        border-left: 4px solid #C0392B;
        border-radius: 10px;
        padding: 22px 26px;
        font-size: 0.95rem;
        line-height: 1.75;
        margin-bottom: 20px;
    }

    .labs-strip {
        background: #243447;
        border: 1px solid #2C3E50;
        border-radius: 8px;
        padding: 12px 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        margin-bottom: 20px;
    }
    .labs-strip .lab-row { display: flex; flex-wrap: wrap; gap: 24px; align-items: center; margin-top: 8px; }
    .labs-strip .lab-item { display: flex; flex-direction: column; }
    .labs-strip .lab-label { color: #95A5A6 !important; font-size: 0.72rem; display: block; margin-bottom: 2px; }
    .labs-strip .lab-value { color: #1ABC9C !important; font-weight: 500; }

    .step-bar { display: flex; gap: 6px; margin-bottom: 20px; }
    .step-pip { height: 6px; flex: 1; border-radius: 3px; background: #2C3E50; }
    .step-pip.done { background: #27AE60; }
    .step-pip.active { background: #E74C3C; }

    .question-card {
        background: #1E2E42;
        border: 1px solid #2C3E50;
        border-radius: 10px;
        padding: 22px 26px;
        margin-bottom: 16px;
    }
    .question-number { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #E74C3C !important; margin-bottom: 8px; }
    .question-text { font-size: 1.05rem; font-weight: 500; line-height: 1.5; }

    .stRadio > label { display: none; }
    div[data-testid="stRadio"] > div { gap: 8px !important; }
    div[data-testid="stRadio"] label {
        background: #1E2E42 !important;
        border: 1px solid #2C3E50 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        width: 100% !important;
        color: #ECF0F1 !important;
    }
    div[data-testid="stRadio"] label:hover { border-color: #E74C3C !important; }

    div.stButton > button {
        background: #C0392B !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        width: 100% !important;
    }
    div.stButton > button:hover { background: #E74C3C !important; }

    .feedback-correct {
        background: rgba(39,174,96,0.12);
        border: 1px solid #27AE60;
        border-left: 4px solid #27AE60;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 14px;
        font-size: 0.93rem;
        line-height: 1.7;
        color: #ECF0F1 !important;
    }
    .feedback-wrong {
        background: rgba(192,57,43,0.12);
        border: 1px solid #C0392B;
        border-left: 4px solid #C0392B;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 14px;
        font-size: 0.93rem;
        line-height: 1.7;
        color: #ECF0F1 !important;
    }
    .feedback-correct strong { color: #2ECC71 !important; }
    .feedback-wrong strong { color: #E74C3C !important; }

    .score-box {
        background: #1E2E42;
        border: 1px solid #2C3E50;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 16px;
    }
    .score-number { font-size: 2.8rem; font-weight: 700; color: #1ABC9C !important; }
    .score-label { color: #95A5A6 !important; font-size: 0.85rem; }

    .complete-banner {
        background: linear-gradient(135deg, rgba(39,174,96,0.18), rgba(26,188,156,0.1));
        border: 1px solid #1ABC9C;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-bottom: 24px;
    }
    .complete-banner h2 { color: #1ABC9C !important; font-size: 1.5rem !important; }

    .stat-pill {
        background: #1E2E42;
        border: 1px solid #2C3E50;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stat-pill .s-label { font-size: 0.8rem; color: #95A5A6 !important; }
    .stat-pill .s-value { font-size: 0.95rem; font-weight: 600; color: #1ABC9C !important; }

    .lab-unlocked {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(26,188,156,0.15);
        border: 1px solid #1ABC9C;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 500;
        color: #1ABC9C !important;
        margin-top: 10px;
    }

    .topic-badge {
        display: inline-block;
        background: rgba(192,57,43,0.18);
        border: 1px solid rgba(192,57,43,0.4);
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #E74C3C !important;
        margin-bottom: 10px;
    }

    hr { border-color: #2C3E50 !important; }
    [data-testid="stMarkdownContainer"] { color: #ECF0F1; }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #1A2638; }
    ::-webkit-scrollbar-thumb { background: #2C3E50; border-radius: 3px; }

    /* selectbox, expander dark theme */
    .stSelectbox div[data-baseweb="select"] { background-color: #1E2E42 !important; border-color: #2C3E50 !important; }
    .stSelectbox div[data-baseweb="select"] * { color: #ECF0F1 !important; }
    .streamlit-expanderHeader { background-color: #1E2E42 !important; color: #ECF0F1 !important; border-color: #2C3E50 !important; }
    .streamlit-expanderContent { background-color: #1E2E42 !important; border-color: #2C3E50 !important; }
</style>
""", unsafe_allow_html=True)

# ===============================
# CENTRALIZED DATA ENGINE
# ===============================
# This dictionary contains all clinical vignettes, dynamic lab reveals, questions, and explanations.
# Each case consists of exactly 3 rigorous, M2-level steps: Pathophysiology, Diagnostic/Hemodynamic, and Diagnosis.


# ===============================
# CENTRALIZED DATA ENGINE
# ===============================
CASES_DATA = {
"case1": {
        "button_label": "Case 1",
        "difficulty": "Intermediate",
        "title": "Case 1: Pathophysiology and Management of Heart Failure",
        "vignette": "A 62-year-old man presents to the cardiology clinic for a follow-up after a recent hospital admission for heart failure. Six months ago, he suffered a massive anterior ST-elevation myocardial infarction (STEMI) due to a 100% occlusion of his proximal left anterior descending (LAD) artery. He now complains of worsening fatigue, the inability to sleep without using three pillows (orthopnea), and shortness of breath when walking from his kitchen to his living room.\n\nPhysical examination reveals a point of maximal impulse (PMI) displaced to the anterior axillary line, a faint S3 gallop at the apex, and bibasilar pulmonary crackles. There is 2+ pitting edema in his lower extremities. A recent echocardiogram demonstrates a left ventricular ejection fraction (LVEF) of 28% with severe eccentric dilation of the left ventricle and global hypokinesis of the anterior wall.",
        "initial_labs": {"BP": "112/74 mmHg", "HR": "88 bpm", "BNP": "1250 pg/mL"},
        "steps": [
            {
                "question": "What is the primary pathophysiological mechanism underlying this patient's condition?",
                "options": [
                    "Isolated diastolic dysfunction leading to impaired ventricular filling",
                    "Chronic impairment of myocardial systolic function leading to reduced cardiac output",
                    "High-output state driven by thyrotoxicosis",
                    "Primary pericardial constriction limiting diastolic expansion"
                ],
                "correct_idx": 1,
                "svg": "frank_starling_hfref",
                "explanations": [
                    "**Incorrect:** This is wrong because diastolic heart failure, or heart failure with preserved ejection fraction (HFpEF), occurs when the heart is stiff and unable to fill properly, not when it is weak. This patient's echocardiogram specifically shows a severely reduced ejection fraction of 28% and global hypokinesis, which are the hallmarks of systolic dysfunction rather than the preserved systolic function seen in isolated diastolic heart failure.",
                    "**Correct!** The patient is suffering from heart failure with reduced ejection fraction (HFrEF). In this condition, the myocardium has been damaged—in this case, by a massive anterior myocardial infarction—causing it to become weak. This weakness leads to a reduction in the heart's ability to eject blood effectively, which lowers overall cardiac output and triggers a compensatory but maladaptive neurohumoral response.",
                    "**Incorrect:** This is incorrect because high-output heart failure occurs when the heart is functioning normally but cannot keep up with an abnormally high metabolic demand, such as that seen in thyrotoxicosis, anemia, or arteriovenous fistulas. Our patient has a clearly documented history of ischemic cardiomyopathy following a massive infarction, which is a classic low-output state where the heart muscle itself is physically impaired and failing.",
                    "**Incorrect:** This is wrong because constrictive pericarditis involves a rigid, scarred pericardium that physically restricts the heart from expanding during diastole. While this can cause symptoms of heart failure and systemic venous congestion, it is characterized by preserved systolic function and normal ventricular volumes, which contradicts the eccentric dilation and significantly reduced ejection fraction observed in this patient's diagnostic imaging."
                ]
            },
            {
                "question": "Why is this patient volume overloaded?",
                "options": [
                    "Primary hyperaldosteronism causing autonomous sodium retention",
                    "Compensatory neurohumoral activation (RAAS and Vasopressin) due to low cardiac output",
                    "Excessive dietary sodium intake as the sole cause of fluid retention",
                    "Increased secretion of BNP and ANP causing fluid accumulation"
                ],
                "correct_idx": 1,
                "svg": "frank_starling_neurohormonal",
                "explanations": [
                    "**Incorrect:** This is wrong because primary hyperaldosteronism is a specific endocrine disorder where the adrenal glands autonomously produce too much aldosterone. In this patient, the body's sodium retention is a secondary compensatory reaction to the heart's inability to pump, rather than a primary adrenal pathology causing the syndrome independently of the heart's function.",
                    "**Correct!** In the setting of HFrEF, the heart cannot maintain adequate cardiac output. The body interprets this low output as under-perfusion, triggering the sympathetic nervous system, the Renin-Angiotensin-Aldosterone System (RAAS), and the release of vasopressin. These systems work together to aggressively reabsorb sodium and water at the kidneys to increase intravascular volume and preload, which is a maladaptive response that ultimately leads to systemic and pulmonary congestion.",
                    "**Incorrect:** This is incorrect because, while dietary sodium can certainly exacerbate the symptoms of heart failure, it is not the primary physiological driver of the condition. The fluid retention in this patient is fundamentally caused by the heart's failure to pump, which triggers profound, systemic neurohumoral shifts that mandate the kidneys retain fluid regardless of how much salt the patient consumes.",
                    "**Incorrect:** This is wrong because the exact opposite is true regarding the function of natriuretic peptides. When the heart is stretched, it releases Brain Natriuretic Peptide (BNP) and Atrial Natriuretic Peptide (ANP) specifically to promote natriuresis, which is the excretion of sodium and water in the urine to decrease blood volume and reduce the workload on the heart; they are protective markers and compensatory mechanisms, not the cause of fluid retention."
                ]
            },
            {
                "question": "Which medication regimen is indicated as foundational, mortality-reducing 'four pillar' therapy for this patient's HFrEF?",
                "options": [
                    "ACE inhibitor/ARB/ARNI, Beta-blocker, MRA, and SGLT2 inhibitor",
                    "Loop diuretic, Digoxin, Hydralazine, and Ivabradine",
                    "High-dose intravenous fluids and positive inotropes",
                    "Diltiazem, NSAIDs, and Thiazolidinediones"
                ],
                "correct_idx": 0,
                "svg": "frank_starling_four_pillars",
                "explanations": [
                    "**Correct!** The 'four pillars' of guideline-directed medical therapy for HFrEF consist of an ARNI (or ACE inhibitor or ARB), a beta-blocker, a mineralocorticoid receptor antagonist (MRA), and an SGLT2 inhibitor. These four classes of medication are proven to target the maladaptive neurohumoral pathways, reverse remodeling, and significantly improve long-term survival in patients with reduced ejection fraction.",
                    "**Incorrect:** This option is wrong because these medications are primarily used for symptomatic management rather than mortality reduction. While loop diuretics are essential for clearing excess fluid and Hydralazine or Digoxin may have specific roles in certain patient profiles, they do not constitute the foundational, life-prolonging neurohumoral blockade that is established by the four pillars of HFrEF therapy.",
                    "**Incorrect:** This is incorrect because administering intravenous fluids to a patient with heart failure who is already volume overloaded and suffering from pulmonary congestion would be dangerous and counterproductive, as it would further increase filling pressures. Additionally, chronic use of positive inotropes is known to increase all-cause mortality and is generally avoided outside of acute settings or end-stage bridge-to-transplant scenarios.",
                    "**Incorrect:** This is wrong because all three of these medication classes are actually contraindicated in patients with HFrEF. NSAIDs cause sodium retention and worsen renal function, thiazolidinediones also promote fluid retention, and non-dihydropyridine calcium channel blockers like diltiazem act as negative inotropes, which directly weaken the heart further and can precipitate worsening heart failure or death."
                ]
            },
            {
                "question": "Which of the following medications is strictly contraindicated in this patient because it may worsen cardiac function?",
                "options": [
                    "Furosemide",
                    "Non-dihydropyridine calcium channel blockers (e.g., Verapamil)",
                    "Carvedilol",
                    "Dapagliflozin"
                ],
                "correct_idx": 1,
                "svg": "frank_starling_four_pillars",
                "explanations": [
                    "**Incorrect:** This is wrong because Furosemide is a loop diuretic that is absolutely necessary for the management of this patient's current symptoms. It works by decreasing the patient's preload, which relieves the pulmonary congestion and peripheral edema caused by the failing heart's inability to handle current fluid volumes, making it a life-saving intervention for acute stabilization.",
                    "**Correct!** Non-dihydropyridine calcium channel blockers, such as verapamil and diltiazem, are negative inotropes that directly suppress the contractility of the myocardium. In a patient whose heart is already failing and has a severely reduced ejection fraction, these drugs further depress the heart's pumping ability, which can lead to a dangerous decline in cardiac output and potentially cause cardiogenic shock.",
                    "**Incorrect:** This is incorrect because Carvedilol is a beta-blocker, which is one of the four essential pillars of HFrEF treatment. Beta-blockers are vital for blocking the harmful, chronic sympathetic nervous system overdrive that contributes to the 'downward spiral' of heart failure; they are proven to improve long-term outcomes and survival, provided they are initiated when the patient is stable.",
                    "**Incorrect:** This is wrong because Dapagliflozin is an SGLT2 inhibitor, which is a foundational medication for the treatment of HFrEF. These drugs provide significant mortality benefits by helping to mitigate the maladaptive neurohumoral changes and offering protective effects on both the heart and the kidneys, making them a standard part of the care for patients with this condition."
                ]
            }
        ]
    },
"case2": {
        "button_label": "Case 2",
        "difficulty": "Advanced",
        "title": "Case 2",
        "vignette": "A 68-year-old man presents with six months of progressive dyspnea on exertion, limiting his ability to perform daily activities. His medical history is significant for hypertension, type 2 diabetes with peripheral neuropathy, hyperlipidemia, and gout. He reports worsening fatigue, orthopnea, and a chronic dry cough. On physical exam, he exhibits jugular venous distension with a positive hepatojugular reflex and 2+ pitting edema in the lower extremities.\n\nHis echocardiogram reveals a left ventricular ejection fraction (LVEF) of 55% with evidence of left atrial enlargement and left ventricular hypertrophy. Despite the preserved ejection fraction, he exhibits classic clinical signs of systemic venous congestion and elevated filling pressures. A resting NT-proBNP is significantly elevated.",
        "initial_labs": {"BP": "158/92 mmHg", "HR": "78 bpm", "HbA1c": "8.2%", "NT-proBNP": "850 pg/mL"},
        "steps": [
            {
                "question": "Which of the following describes the fundamental hemodynamic derangement in this patient that differentiates his condition from systolic heart failure?",
                "options": [
                    "A shift of the left ventricular end-diastolic pressure-volume relationship (EDPVR) upward and to the left",
                    "Decreased myocardial contractility leading to a reduction in stroke volume",
                    "Increased end-systolic ventricular volumes leading to eccentric hypertrophy",
                    "A primary elevation in systemic vascular resistance that cannot be overcome by increased inotropy"
                ],
                "correct_idx": 0,
                "svg": "pv_loop_hfpef",
                "explanations": [
                    "**Correct!** The condition presented is characterized by diastolic dysfunction, where the ventricle is stiff and non-compliant. This stiffness is represented on the pressure-volume loop as a shift of the end-diastolic pressure-volume relationship (EDPVR) upward and to the left, meaning the ventricle requires significantly higher filling pressures to achieve the same end-diastolic volume as a normal heart.",
                    "**Incorrect:** This option describes the hallmark of systolic heart failure (HFrEF), where the weakened myocardium suffers from reduced contractility. In HFrEF, the ventricle is unable to eject blood effectively, resulting in a low ejection fraction, whereas this patient maintains a preserved ejection fraction, indicating his systolic function is relatively intact.",
                    "**Incorrect:** This is wrong because eccentric hypertrophy and increased end-systolic volumes are associated with the dilated cardiomyopathy seen in HFrEF. In the condition presented, the heart typically undergoes concentric remodeling in response to chronic stressors like hypertension, resulting in smaller ventricular volumes rather than the dilation associated with systolic failure.",
                    "**Incorrect:** This is wrong because, while systemic hypertension often contributes to the development of this condition, a primary elevation in systemic vascular resistance alone does not constitute the pathophysiological diagnosis. The key diagnostic feature is the impairment of diastolic filling caused by structural myocardial stiffness, rather than just the presence of high afterload."
                ]
            },
            {
                "question": "Given the patient's metabolic profile, which cellular mechanism is most centrally involved in the pathogenesis of his diastolic dysfunction?",
                "options": [
                    "Myocyte loss via apoptosis leading to wall thinning and chamber dilation",
                    "Chronic systemic inflammation leading to cardiomyocyte stiffness and increased interstitial fibrosis",
                    "Inhibition of the natriuretic peptide pathway resulting in blunted natriuresis",
                    "Primary genetic mutation in the beta-myosin heavy chain gene"
                ],
                "correct_idx": 1,
                "explanations": [
                    "**Incorrect:** This option describes the pathogenesis of HFrEF, where cell death and adverse remodeling lead to the thinning and dilation of the ventricular wall. This process results in the weak, 'baggy' heart muscle characteristic of systolic failure, which is the opposite of the stiff, hypertrophied ventricle seen in this patient.",
                    "**Correct!** The condition is increasingly recognized as a metabolic and inflammatory syndrome, particularly in patients with comorbidities like diabetes and hypertension. These chronic systemic conditions promote a pro-inflammatory state that induces cardiomyocyte hypertrophy, increases interstitial collagen deposition (fibrosis), and reduces myocardial compliance, ultimately creating the stiff ventricle that characterizes diastolic dysfunction.",
                    "**Incorrect:** This is wrong because the natriuretic peptide pathway is actually activated in heart failure as a compensatory, protective response. BNP and ANP are secreted in response to atrial and ventricular stretch to help reduce fluid overload through natriuresis; while patients may eventually have elevated levels, the failure to clear fluid is not due to an inhibition of this pathway.",
                    "**Incorrect:** This is wrong because, while genetic factors can contribute to cardiomyopathies, the most common cause of diastolic dysfunction in a patient with this constellation of metabolic risk factors is acquired, not congenital. The stiffness here is a secondary manifestation of long-standing hypertension and metabolic disease, which causes myocardial remodeling rather than a primary sarcomeric mutation."
                ]
            },
            {
                "question": "Which of the following therapeutic interventions is supported by clinical data as providing a definitive mortality benefit in patients with this specific physiological classification?",
                "options": [
                    "Initiation of a beta-blocker to improve diastolic filling time",
                    "Aggressive titration of ACE inhibitors to reverse myocardial fibrosis",
                    "Treatment with an SGLT2 inhibitor",
                    "Administration of a non-dihydropyridine calcium channel blocker for rate control"
                ],
                "correct_idx": 2,
                "explanations": [
                    "**Incorrect:** This is wrong because, while beta-blockers are a foundational pillar of therapy for HFrEF, they have not been shown to provide a definitive mortality or symptom benefit in patients with this condition. Their use in this setting is primarily to manage comorbid conditions like atrial fibrillation or rate control, but they do not alter the disease progression in the same way they do in systolic failure.",
                    "**Incorrect:** This is incorrect because, although RAAS modulation (ACE inhibitors or ARBs) is often used to manage hypertension and comorbidities, they have not demonstrated a clear, definitive mortality benefit in this specific physiological classification. While they may help with symptomatic control or managing underlying hypertension, they do not carry the same strong evidence for survival improvement seen in HFrEF.",
                    "**Correct!** SGLT2 inhibitors are the only class of medications that have been definitively shown to reduce mortality and hospitalizations in patients with this condition. These agents are crucial in managing the metabolic components of the disease and are now considered the most impactful therapeutic intervention for this patient population.",
                    "**Incorrect:** This is wrong because non-dihydropyridine calcium channel blockers like diltiazem act as negative inotropes and can suppress myocardial contractility, potentially worsening symptoms in heart failure. They are not indicated for disease-modifying therapy and are generally avoided due to their potential to negatively impact cardiac performance."
                ]
            },
            {
                "question": "A 75-year-old woman presents with exertional dyspnea. Echocardiography reveals EF 60%, left atrial enlargement, and concentric left ventricular hypertrophy. Which physical examination finding is most consistent with her diagnosis?",
                "options": [
                    "S3 gallop",
                    "Holosystolic murmur radiating to the axilla",
                    "S4 gallop",
                    "Fixed split S2"
                ],
                "correct_idx": 2,
                "svg": "pv_loop_hfpef",
                "explanations": [
                    "**Incorrect:** An S3 gallop is a low-frequency sound occurring during the rapid passive filling phase of diastole, which is strongly associated with severe volume overload and systolic dysfunction (HFrEF). In HFrEF, the dilated, highly compliant ventricle creates this sound when blood fills the chamber; therefore, it is not the typical finding in a patient with the stiff, non-compliant ventricle characteristic of this condition.",
                    "**Incorrect:** A holosystolic murmur radiating to the axilla is the classic presentation of mitral regurgitation. While mitral regurgitation can coexist with or even cause heart failure symptoms, it is not a direct diagnostic physical exam finding of diastolic dysfunction itself; the finding in this patient must reflect the mechanical properties of a stiff, poorly compliant ventricle.",
                    "**Correct!** An S4 gallop is a low-pitched sound that occurs late in diastole, caused by the atrial kick forcing blood into a stiff, non-compliant, hypertrophied ventricle. This is the classic auscultatory finding in patients with this condition, as the ventricle lacks the necessary compliance to accommodate blood flow during the atrial contraction phase of the cardiac cycle.",
                    "**Incorrect:** A fixed split S2 is a classic finding of an atrial septal defect (ASD), where the volume overload of the right heart causes delayed closure of the pulmonic valve regardless of respiratory phase. This finding is related to a structural congenital shunt and is not reflective of the diastolic stiffening and impaired ventricular filling dynamics that define the pathophysiology of heart failure with preserved ejection fraction."
                ]
            }
        ]
    },
"case3": {
       "button_label": "Case 3",
        "difficulty": "Intermediate",
        "difficulty": "Intermediate",
       "title": "Case 3",
       "vignette": "An 84-year-old woman presents to the clinic complaining of progressive shortness of breath that has significantly limited her daily activities, such as walking around the store. Her medical history is significant for diabetes, hypertension, and a 30-year history of smoking. She denies any history of chest pain or myocardial infarction. On physical examination, her blood pressure is normal, but her peripheral pulses are 1+.\n\nAuscultation reveals a systolic murmur. Echocardiography is performed to further evaluate the patient, revealing a restricted aortic valve opening with a calculated valve area of less than 1.0 cm². The mean transvalvular pressure gradient is measured at 45 mmHg, and the peak velocity across the valve is 4.2 m/s.",
        "steps": [
            {
                "question": "Which of the following is the most likely underlying mechanism for this patient's condition?",
                "options": [
                    "Rheumatic heart disease resulting from prior infection",
                    "Senile calcific degeneration of the aortic valve",
                    "Acute bacterial endocarditis affecting the valve leaflets",
                    "Primary congenital bicuspid valve deformity"
                ],
                "correct_idx": 1,
                "svg": "pv_loop_as",
                "explanations": [
                    "**Incorrect:** While rheumatic heart disease is a potential cause of aortic stenosis, it typically develops several decades after a history of rheumatic fever. Given the patient's age of 84, senile calcific aortic stenosis is the most common and statistically likely etiology.",
                    "**Correct!** Senile calcific aortic stenosis is the most common cause of the condition in patients over the age of 65. It is an age-related process where the valve leaflets become calcified and stiff, preventing the valve from opening completely and creating a barrier to blood flow.",
                    "**Incorrect:** Acute bacterial endocarditis typically causes rapid destruction of the valve leaflets leading to acute aortic regurgitation, not the chronic, progressive stenosis described in this patient's case.",
                    "**Incorrect:** Although congenital bicuspid valves are a known cause of aortic stenosis, they typically degenerate and manifest as clinically significant stenosis in patients younger than 45 years. In an 84-year-old patient, calcification is the far more common driver."
                ]
            },
            {
                "question": "Which of the following physical examination findings would be most expected given this patient's diagnosis?",
                "options": [
                    "A diastolic decrescendo murmur heard best at the left sternal border",
                    "Brisk, bounding peripheral pulses (water hammer pulses)",
                    "A weak and delayed carotid upstroke (pulsus parvus et tardus)",
                    "A holosystolic murmur that does not radiate"
                ],
                "correct_idx": 2,
                "svg": "pv_loop_as",
                "explanations": [
                    "**Incorrect:** This murmur is characteristic of aortic regurgitation, where blood flows backward into the ventricle during diastole. This patient has been diagnosed with aortic stenosis, which presents with a systolic ejection murmur.",
                    "**Incorrect:** Brisk or water hammer pulses are a classic physical exam finding for aortic regurgitation, caused by wide pulse pressure and rapid runoff of blood. This patient has 1+ peripheral pulses, which is more consistent with the diminished pulses of aortic stenosis.",
                    "**Correct!** In aortic stenosis, the physical exam often reveals a weak and delayed carotid upstroke, known as pulsus parvus et tardus, because the stenotic valve obstructs the ejection of blood from the left ventricle into the arterial system.",
                    "**Incorrect:** A holosystolic murmur that does not radiate is more suggestive of mitral regurgitation. Aortic stenosis typically presents with a crescendo-decrescendo systolic ejection murmur that radiates to the carotid or subclavian arteries."
                ]
            },
            {
                "question": "How does the left ventricle physiologically adapt to the chronic pressure overload caused by this stenosis?",
                "options": [
                    "The ventricle undergoes eccentric hypertrophy and progressive chamber dilation",
                    "The ventricle develops concentric left ventricular hypertrophy to maintain wall stress",
                    "The ventricle decreases muscle mass to reduce myocardial oxygen consumption",
                    "The ventricle shifts to a high-output state to compensate for the valve resistance"
                ],
                "correct_idx": 1,
                "explanations": [
                    "**Incorrect:** Eccentric hypertrophy and chamber dilation are the typical responses to volume overload, such as that seen in aortic regurgitation or mitral regurgitation. In response to the chronic pressure overload of aortic stenosis, the heart undergoes a different remodeling process.",
                    "**Correct!** To manage the chronic pressure overload and increased wall stress, the left ventricle undergoes concentric hypertrophy. This hypertrophy increases the muscle mass of the ventricle but can eventually impair diastolic function, resulting in elevated filling pressures.",
                    "**Incorrect:** The ventricle actually increases its muscle mass in response to the high pressures required to force blood through the stenotic valve, which actually increases, rather than decreases, the total myocardial oxygen demand.",
                    "**Incorrect:** The body attempts to keep cardiac output relatively constant, not increase it to a 'high-output' state, by increasing the pressure gradient across the valve. A high-output state is a pathological condition, not a standard compensatory mechanism for aortic stenosis."
                ]
            },
            {
                "question": "The patient's echocardiogram shows severe, symptomatic aortic stenosis. What is the most appropriate next step in her management?",
                "options": [
                    "Repeat the TTE in six months to monitor for further progression",
                    "Initiate aggressive medical management with beta-blockers and ACE inhibitors",
                    "Referral for surgical or transcatheter aortic valve replacement",
                    "Perform a diagnostic cardiac catheterization to confirm the valve area"
                ],
                "correct_idx": 2,
                "explanations": [
                    "**Incorrect:** Simply repeating the echo would delay definitive treatment for a patient who is already symptomatic with severe disease; delaying intervention once symptoms occur significantly worsens her prognosis.",
                    "**Incorrect:** Medical therapy does not fix the physical obstruction caused by a severely stenotic valve. While managing comorbidities is important, it does not replace the need for definitive treatment in a symptomatic patient.",
                    "**Correct!** Valve replacement—whether surgical or via a transcatheter approach—is the indicated treatment for patients with severe, symptomatic aortic stenosis. This relieves the outflow obstruction and addresses the primary driver of her symptoms and poor prognosis.",
                    "**Incorrect:** While catheterization can be used to measure pressures, the diagnosis of severe aortic stenosis has already been confirmed by the echocardiography findings. Diagnostic cath is not the management step—definitive valve intervention is."
                ]
            }
        ]
    },
"case4": {
        "button_label": "Case 4",
        "difficulty": "Advanced",
        "title": "Case 4",
        "vignette": "A 55-year-old man presents to the clinic with complaints of progressive exertional fatigue and dyspnea. He reports that he has been feeling 'pounding' sensations in his chest when lying down at night. He has no significant past medical history but mentions a recent diagnosis of an aortic root dilation. He denies any chest pain or history of rheumatic fever.\n\nOn physical examination, his blood pressure is 145/45 mmHg. Auscultation reveals a decrescendo diastolic murmur heard best at the left sternal border. His peripheral pulses are noted to be brisk and bounding. An echocardiogram shows significant backward flow of blood from the aorta into the left ventricle during diastole, and the left ventricle appears dilated.",
        "steps": [
            {
                "question": "Which of the following best describes the underlying pathophysiology of this patient's condition?",
                "options": [
                    "Calcification of the aortic valve leaflets preventing proper opening",
                    "A chronic pressure-overload state leading to concentric hypertrophy",
                    "Failure of the aortic valve to close completely, leading to a volume-overloaded left ventricle",
                    "Primary narrowing of the left ventricular outflow tract causing turbulent flow"
                ],
                "correct_idx": 2,
                "svg": "pv_loop_ar",
                "explanations": [
                    "**Incorrect:** This option describes the pathophysiology of aortic stenosis, a condition where the valve becomes stiff and fails to open effectively during systole. In this patient's case, the physical exam and echocardiogram specifically highlight issues with the valve preventing backflow during diastole, not the resistance to forward flow seen in stenosis.\n\nFurthermore, aortic stenosis is characterized by an obstruction to blood flow as it exits the left ventricle. Because this patient’s primary clinical problem is the leakage of blood backward into the ventricle, the mechanical failure here is one of valve closure, not valve opening.",
                    "**Incorrect:** This description accurately defines the physiological response to aortic stenosis, which creates a chronic pressure-overload state. In response to the significant resistance to outflow, the ventricle remodels by adding sarcomeres in parallel, resulting in concentric left ventricular hypertrophy.\n\nIn contrast, the condition this patient presents with is a volume-overloaded state. Because the heart must accommodate both the normal venous return and the regurgitant volume returning from the aorta, the ventricle undergoes a different type of remodeling called eccentric hypertrophy and progressive dilation.",
                    "**Correct!** Aortic regurgitation is defined by the failure of the aortic valve leaflets to seal correctly at the end of systole. This incompetence allows blood that has already been ejected into the aorta to flow backward into the left ventricle during the diastolic filling phase, which essentially creates a volume-overloaded state.\n\nThis increased volume significantly impacts the left ventricle, leading to compensatory eccentric hypertrophy and eventual dilation. By forcing the ventricle to handle this extra blood, the heart eventually reaches a point where its ability to manage these increased preloads is overwhelmed, leading to the symptoms of heart failure the patient is experiencing.",
                    "**Incorrect:** This description refers to conditions like hypertrophic cardiomyopathy or subvalvular obstructions, which physically constrict the outflow tract and create turbulence as blood tries to exit. While these can lead to murmurs, they do not result in the backward diastolic flow into the ventricle that characterizes aortic regurgitation.\n\nTurbulent flow from an outflow tract obstruction is a systolic phenomenon, whereas this patient’s condition is defined by the mechanical failure of the aortic valve to maintain a pressure gradient between the aorta and the ventricle during diastole."
                ]
            },
            {
                "question": "The patient's blood pressure is 145/45 mmHg. What is the cause of this wide pulse pressure?",
                "options": [
                    "Increased systemic vascular resistance due to left ventricular failure",
                    "Rapid runoff of blood from the aorta back into the left ventricle and peripheral vasodilation",
                    "Elevated pulmonary capillary wedge pressure due to left atrial congestion",
                    "Compensatory sympathetic nervous system stimulation increasing cardiac contractility"
                ],
                "correct_idx": 1,
                "explanations": [
                    "**Incorrect:** In the setting of chronic aortic regurgitation, systemic vascular resistance is typically reduced, not increased. The peripheral vasculature often undergoes vasodilation in response to the changes in cardiac output and pressure dynamics, which helps to facilitate the runoff of blood.\n\nLeft ventricular failure, while a potential consequence of long-standing valve disease, is not the mechanism that produces a wide pulse pressure. Instead, the widened pressure range is a direct mechanical consequence of the regurgitant jet and the associated changes in arterial tone.",
                    "**Correct!** The wide pulse pressure observed in this patient is largely caused by the rapid runoff of blood out of the aorta and back into the left ventricle during diastole. Because the blood is leaking backward, the diastolic blood pressure drops to a very low level.\n\nSimultaneously, the body experiences peripheral vasodilation, which further promotes this rapid runoff. This combination of a high systolic pressure—generated by the increased stroke volume—and a very low diastolic pressure creates the classic, wide pulse pressure of 145/45 mmHg that is hallmark of this condition.",
                    "**Incorrect:** While pulmonary capillary wedge pressure elevation is a sign of late-stage cardiac decompensation and left atrial congestion, it is not the mechanism responsible for a wide pulse pressure. Wedge pressure relates specifically to the filling pressures of the left atrium and pulmonary circulation rather than the systemic arterial blood pressure.\n\nThe pulse pressure is a measure of the difference between systolic and diastolic arterial pressures, which is governed by the dynamics of blood within the aorta and systemic vasculature, not by venous pressures in the pulmonary system.",
                    "**Incorrect:** Although the sympathetic nervous system is undoubtedly active in heart failure, it does not act as the primary driver for a wide pulse pressure. Sympathetic activation usually increases both heart rate and contractility, which might help maintain cardiac output, but these actions do not directly cause the dramatic separation between systolic and diastolic pressures.\n\nThe wide pressure range is a mechanical phenomenon directly linked to the volume of blood regurgitating back into the heart and the vasodilation of the arterial tree, which creates the massive drop in diastolic pressure."
                ]
            },
            {
                "question": "Which of the following physical examination findings is most consistent with the diagnosis of severe aortic regurgitation?",
                "options": [
                    "Weak and delayed carotid upstroke (pulsus parvus et tardus)",
                    "A fixed split S2 heart sound",
                    "Austin Flint murmur",
                    "Crescendo-decrescendo systolic murmur at the right upper sternal border"
                ],
                "correct_idx": 2,
                "svg": "murmur_timing",
                "explanations": [
                    "**Incorrect:** A weak and delayed carotid upstroke, also known as pulsus parvus et tardus, is the classic finding in aortic stenosis. It occurs because the stenotic valve creates a significant barrier to the ejection of blood, resulting in a slowed and diminished wave traveling to the carotid arteries.\n\nBecause this patient has been diagnosed with aortic regurgitation, his pulses are actually the opposite—they are characteristically brisk and bounding. Therefore, this finding would be entirely inconsistent with the diagnosis.",
                    "**Incorrect:** A fixed split S2 is a characteristic physical finding of an atrial septal defect (ASD). In an ASD, the chronic volume overload of the right heart results in a delayed closure of the pulmonic valve, and this delay does not change with the patient's respiratory cycle.\n\nThis finding has no physiological relationship to aortic valve disease. Aortic regurgitation primarily affects the left side of the heart, whereas a fixed split S2 is an indicator of right-sided hemodynamic shunting.",
                    "**Correct!** The Austin Flint murmur is a specific low-pitched, mid-diastolic rumble heard at the apex. It occurs in cases of severe aortic regurgitation when the jet of blood leaking backward from the aorta strikes the anterior mitral valve leaflet.\n\nThis physical impact causes the mitral valve leaflet to partially close, effectively creating a functional mitral stenosis that limits blood inflow into the ventricle. It is an important diagnostic clue that clinicians look for when evaluating the severity of regurgitation.",
                    "**Incorrect:** A crescendo-decrescendo systolic murmur heard best at the right upper sternal border is the classic presentation for aortic stenosis. This murmur is caused by turbulent blood flow as it is ejected through the narrowed, calcified valve opening.\n\nWhile patients with aortic regurgitation may have flow murmurs due to the increased stroke volume, the diastolic murmur described in this patient's vignette is the definitive sound associated with the valve's failure to close, not the systolic murmur of an obstructed opening."
                ]
            },
            {
                "question": "What is the most appropriate management approach for a patient with symptomatic severe aortic regurgitation?",
                "options": [
                    "Strict salt restriction and follow-up in one year",
                    "Initiation of a beta-blocker as the primary curative treatment for regurgitation",
                    "Surgical or transcatheter repair of the mitral valve to reduce backflow",
                    "Aortic valve replacement for symptomatic patients or those with LV dysfunction"
                ],
                "correct_idx": 3,
                "explanations": [
                    "**Incorrect:** Simply managing the patient's diet and monitoring with echocardiograms (TTE) is insufficient for someone who is already symptomatic. Once a patient begins showing symptoms, their prognosis is significantly impacted, and watchful waiting risks allowing the left ventricle to progress toward irreversible dysfunction.\n\nDefinitive treatment is required once the valve disease reaches the symptomatic threshold. Therefore, deferring intervention is not an appropriate strategy for a patient who is struggling with exertional fatigue and dyspnea.",
                    "**Incorrect:** Beta-blockers are a useful tool for managing blood pressure and heart rate in various heart conditions, but they do not serve as a curative treatment for structural valve failure. Aortic regurgitation is a mechanical problem where the valve fails to close; no medication can correct this structural flaw.\n\nWhile these medications might be used to support the heart, they do not resolve the volume overload caused by the regurgitant jet, and thus they cannot be considered a primary treatment approach for severe, symptomatic disease.",
                    "**Incorrect:** This is not a viable strategy because the underlying pathology is located at the aortic valve, not the mitral valve. Performing a procedure on the mitral valve would do nothing to stop the blood from flowing backward from the aorta into the left ventricle.\n\nInterventions must be targeted at the site of the mechanical defect. Since the incompetence is occurring at the aortic root, the solution must involve an intervention that replaces or addresses the aortic valve apparatus itself.",
                    "**Correct!** Aortic valve replacement is the definitive treatment indicated for patients who have severe aortic regurgitation combined with symptoms or evidence of left ventricular dysfunction. This surgical or transcatheter procedure removes the incompetent valve and replaces it with a prosthesis to stop the regurgitant volume.\n\nBy addressing the valve itself, clinicians can relieve the volume overload on the left ventricle, which helps to stop the progressive dilation and improves the patient's clinical outcome and survival prospects."
                ]
            }
        ]
    },
"case5": {
        "button_label": "Case 5",
        "difficulty": "Intermediate",
        "title": "Case 5",
        "vignette": "A 68-year-old woman presents to the cardiology clinic with a three-month history of progressive exercise intolerance and exertional dyspnea. She denies any chest pain, orthopnea, or paroxysmal nocturnal dyspnea, but reports feeling 'palpitations' at rest. Her medical history is significant for a myocardial infarction five years ago and long-standing hypertension.\n\nOn physical examination, her blood pressure is 138/82 mmHg. A cardiac exam reveals a holosystolic murmur heard best at the cardiac apex that radiates to the left axilla. An echocardiogram demonstrates an enlarged left atrium, a dilated left ventricle, and significant retrograde flow of blood from the left ventricle into the left atrium during systole.",
        "steps": [
            {
                "question": "Which of the following is the most likely etiology for this patient's condition?",
                "options": [
                    "Calcific degeneration of the mitral annulus",
                    "Chronic rheumatic valvulitis leading to leaflet fusion",
                    "Myxomatous degeneration of the mitral valve apparatus",
                    "Papillary muscle dysfunction or chordal rupture secondary to prior infarction"
                ],
                "correct_idx": 3,
                "svg": "pv_loop_mr",
                "explanations": [
                    "**Incorrect:** While mitral annular calcification can lead to some degree of mitral regurgitation in older adults, it is rarely the cause of significant, symptomatic regurgitation in the context of a prior myocardial infarction. This patient's history of a prior MI points toward a more specific ischemic mechanism.",
                    "**Incorrect:** Chronic rheumatic heart disease typically results in mitral stenosis, or a combination of stenosis and regurgitation, rather than pure, significant regurgitation. Furthermore, rheumatic disease usually presents with characteristic 'fish-mouth' orifice narrowing, which is not described here.",
                    "**Incorrect:** Myxomatous degeneration is the most common cause of mitral valve prolapse. While it can cause significant regurgitation, this patient's clinical history of a myocardial infarction is a much more direct and statistically probable cause for her presentation.",
                    "**Correct!** The patient's history of a myocardial infarction is a classic setup for papillary muscle dysfunction or secondary mitral regurgitation. Ischemia can cause the papillary muscles to become dysfunctional or lead to remodeling of the left ventricle, which tethers the mitral leaflets and prevents them from coapting properly during systole."
                ]
            },
            {
                "question": "What is the primary hemodynamic consequence of significant mitral regurgitation?",
                "options": [
                    "Chronic pressure overload on the left ventricle resulting in concentric hypertrophy",
                    "Volume overload of the left atrium and left ventricle",
                    "Decreased preload to the left ventricle, leading to hypotension",
                    "Increased forward stroke volume due to decreased resistance in the left atrium"
                ],
                "correct_idx": 1,
                "svg": "pv_loop_mr",
                "explanations": [
                    "**Incorrect:** Pressure overload is the hallmark of aortic stenosis. Mitral regurgitation is a volume-overload state, not a pressure-overload state, as the blood is ejected into the lower-pressure environment of the left atrium.",
                    "**Correct!** Significant mitral regurgitation creates a volume-overload state. Because a portion of the left ventricular stroke volume is ejected backward into the left atrium during systole, both the left ventricle and the left atrium must handle an increased volume of blood, leading to chamber dilation.",
                    "**Incorrect:** Mitral regurgitation actually increases the diastolic filling volume (preload) of the left ventricle because of the blood that returns from the left atrium. This volume overload is what drives the characteristic ventricular dilation.",
                    "**Incorrect:** Forward stroke volume typically decreases in significant mitral regurgitation because a substantial portion of the blood is diverted into the left atrium instead of being pumped into the systemic circulation through the aorta."
                ]
            },
            {
                "question": "Which physical examination finding is highly specific to the murmur of mitral regurgitation?",
                "options": [
                    "A crescendo-decrescendo murmur that radiates to the carotid arteries",
                    "A holosystolic murmur heard best at the apex with radiation to the axilla",
                    "A mid-diastolic rumble at the apex following an opening snap",
                    "A diastolic decrescendo murmur at the left sternal border"
                ],
                "correct_idx": 1,
                "svg": "murmur_timing",
                "explanations": [
                    "**Incorrect:** This is the characteristic description of aortic stenosis, where blood is ejected through a narrow valve into the aorta, producing a systolic murmur that radiates upward to the carotid vessels.",
                    "**Correct!** The hallmark of mitral regurgitation is a holosystolic (pansystolic) murmur, which occurs because the pressure in the left ventricle exceeds the pressure in the left atrium throughout the entire period of ventricular systole. The sound is characteristically directed by the regurgitant jet, often radiating to the left axilla.",
                    "**Incorrect:** An opening snap followed by a mid-diastolic rumble is the classic presentation of mitral stenosis. The opening snap occurs when the stenotic valve leaflets reach their limit of opening at the start of diastole.",
                    "**Incorrect:** A diastolic decrescendo murmur at the left sternal border is the classic finding for aortic regurgitation, caused by the backward flow of blood from the aorta into the left ventricle during diastole."
                ]
            },
            {
                "question": "Given the patient's symptomatic state and echocardiographic findings, what is the most appropriate next step in her management?",
                "options": [
                    "Strict salt restriction and follow-up in one year",
                    "Immediate referral for mitral valve surgery or transcatheter intervention",
                    "Initiation of long-term anticoagulation with warfarin regardless of rhythm",
                    "Cardiopulmonary exercise testing to confirm the need for intervention"
                ],
                "correct_idx": 1,
                "explanations": [
                    "**Incorrect:** While lifestyle management is helpful, the patient is already symptomatic (exertional dyspnea). Simply waiting for a follow-up visit does not address the underlying mechanical valve failure that is driving her heart failure symptoms.",
                    "**Correct!** In a patient with symptomatic, severe mitral regurgitation, surgical or interventional repair (or replacement) is the gold standard for treatment. Delaying intervention in symptomatic patients with structural valve disease can lead to permanent, irreversible myocardial damage.",
                    "**Incorrect:** Anticoagulation is generally indicated if the patient has atrial fibrillation to prevent stroke, but it does not address the mechanical regurgitation caused by the mitral valve dysfunction itself.",
                    "**Incorrect:** While exercise testing can sometimes be used to evaluate exercise capacity, it is not the next step for a patient who is already symptomatic with clear echocardiographic evidence of severe regurgitation; she already meets the criteria for intervention."
                ]
            }
        ]
    },
"case6": {
        "button_label": "Case 6",
        "difficulty": "Intermediate",
        "title": "Case 6",
        "vignette": "A 62-year-old man is brought to the emergency department by ambulance after experiencing 45 minutes of crushing substernal chest pain that began while he was mowing his lawn. He describes the pain as a heavy pressure radiating to his left jaw and shoulder, associated with diaphoresis and nausea. His past medical history is significant for hyperlipidemia, hypertension, and a 20-pack-year smoking history.\n\nAn electrocardiogram (ECG) performed upon arrival reveals 3-mm ST-segment elevation in leads V2 through V5. Physical examination shows he is tachypneic and pale, with a blood pressure of 105/65 mmHg and a heart rate of 102 bpm. Lung auscultation reveals mild crackles at the bases bilaterally.",
        "steps": [
            {
                "question": "Which of the following is the most appropriate initial management step for this patient?",
                "options": [
                    "Administer intravenous fluids to improve preload",
                    "Immediate reperfusion therapy, such as primary percutaneous coronary intervention (PCI)",
                    "Obtain a computed tomography (CT) scan of the chest to rule out aortic dissection",
                    "Initiate thrombolytic therapy as a bridge to surgical evaluation"
                ],
                "correct_idx": 1,
                "svg": "ecg_stemi",
                "explanations": [
                    "**Incorrect:** While this patient is slightly hypotensive, his lung crackles suggest he may have early pulmonary congestion. Over-aggressive fluid resuscitation could worsen his symptoms of heart failure and is not the priority for his STEMI, as the main goal in acute coronary syndrome is to treat the underlying thrombotic occlusion.\n\nClinical management must prioritize the restoration of blood flow to the ischemic myocardium. Hemodynamic support is secondary to addressing the culprit lesion causing the ST-elevation, and unnecessary fluids may further complicate his pulmonary status.",
                    "**Correct!** The primary goal in the management of ST-elevation myocardial infarction (STEMI) is immediate reperfusion to minimize myocardial necrosis, as a STEMI is an emergency resulting from the complete occlusion of a coronary artery. Primary percutaneous coronary intervention (PCI) is the gold standard and should be performed as quickly as possible if available.\n\nTime is muscle in the setting of acute coronary syndromes. Every minute saved in achieving reperfusion correlates with improved patient survival and reduced long-term complications like heart failure or arrhythmias.",
                    "**Incorrect:** While aortic dissection is an important differential for chest pain, this patient has classic ECG findings of a STEMI with ST-segment elevation. Delaying reperfusion to perform imaging for an unlikely diagnosis is contraindicated when clinical suspicion for STEMI is high.\n\nRedirecting resources toward imaging would unnecessarily delay time-sensitive revascularization, which is the most critical intervention for this patient's survival. The clinical presentation and ECG findings are diagnostic for an acute STEMI requiring emergent action.",
                    "**Incorrect:** Thrombolytics are generally reserved for situations where primary PCI cannot be performed within the recommended time windows and are not a standard bridge to surgical evaluation for a patient who is eligible for primary PCI.\n\nThrombolytic therapy carries a significant risk of bleeding, particularly in an older patient with multiple cardiovascular risk factors. It is a secondary option when PCI capabilities are not available within the required timeframe of 90 minutes."
                ]
            },
            {
                "question": "What laboratory finding explicitly differentiates this patient's presentation from Unstable Angina (UA)?",
                "options": [
                    "Elevated B-type Natriuretic Peptide (BNP)",
                    "Presence of ST-segment depressions on the ECG",
                    "Elevated serum cardiac troponins",
                    "Elevated D-dimer levels"
                ],
                "correct_idx": 2,
                "svg": "troponin_curve",
                "explanations": [
                    "**Incorrect:** BNP is a marker of cardiac stretch and is often elevated in heart failure, but it is not specific to the diagnosis of an acute myocardial infarction and does not differentiate between UA and STEMI/NSTEMI.\n\nElevations in BNP may occur secondary to ventricular strain, but they are not the primary biomarker used to establish the presence of myocardial necrosis in the context of an acute coronary syndrome.",
                    "**Incorrect:** ST-segment depressions are typically associated with NSTEMI or ischemia, not STEMI. Furthermore, cardiac troponin levels—which are highly sensitive and specific markers for myocardial cell death—are characteristically negative in UA.\n\nWhile ECG changes are vital for classification, they do not constitute a laboratory finding. The presence of biomarkers is what specifically defines an infarction rather than just angina.",
                    "**Correct!** The presence of elevated serum cardiac troponins is the hallmark of myocardial necrosis, which is the defining feature of myocardial infarction as opposed to unstable angina where troponins remain negative.",
                    "**Incorrect:** D-dimer is a marker of fibrinolysis and is used primarily in the workup of venous thromboembolism (DVT/PE) or aortic dissection, not for the evaluation of acute myocardial infarction.\n\nElevated D-dimer levels are non-specific and would not help a clinician differentiate between the various forms of acute coronary syndrome."
                ]
            },
            {
                "question": "How do troponins become elevated in the setting of a STEMI?",
                "options": [
                    "Increased production by healthy cardiomyocytes under stress",
                    "Release from damaged or necrotic myocardial cells following infarction",
                    "Activation of inactive precursors in the bloodstream",
                    "Increased synthesis in the liver in response to systemic inflammation"
                ],
                "correct_idx": 1,
                "svg": "troponin_curve",
                "explanations": [
                    "**Incorrect:** Troponins are not produced in increased amounts by healthy cells in response to stress; rather, they are structural proteins within the contractile apparatus of the cardiomyocyte.\n\nElevation occurs because of cellular destruction, not an upregulation of protein synthesis by functional cardiac tissue.",
                    "**Correct!** As myocardial cells experience prolonged ischemia and subsequently die (infarction), their cell membranes become compromised, allowing intracellular contents to leak into the bloodstream.\n\nTroponin is a protein found within these myocardial cells and is considered the most specific marker of cardiac injury, as its detection in the blood directly correlates with cell death.",
                    "**Incorrect:** Troponins are structural components of the sarcomere (actin-tropomyosin complex) and are not stored as inactive precursors in the blood waiting to be activated.\n\nTheir appearance in the circulation is exclusively due to the leakage of intracellular proteins from damaged myocardium, not an activation cascade in the plasma.",
                    "**Incorrect:** Troponins are specific to cardiac muscle and are not synthesized by the liver, even in the presence of systemic inflammation or stress.\n\nWhile systemic inflammation can affect various serum markers, troponin elevation is a specific diagnostic indicator of myocardial injury and is not a byproduct of hepatic metabolism."
                ]
            },
            {
                "question": "Which of the following medications is indicated for this patient to reduce myocardial oxygen demand and mortality?",
                "options": [
                    "A high-dose calcium channel blocker",
                    "A non-selective beta-blocker",
                    "Aspirin and a P2Y12 inhibitor",
                    "A long-acting nitrate"
                ],
                "correct_idx": 2,
                "svg": "ecg_stemi",
                "explanations": [
                    "**Incorrect:** Calcium channel blockers are not first-line therapy for STEMI management and can even be harmful in patients with heart failure or reduced systolic function, which may be developing in this patient given his lung crackles.\n\nIn the setting of an acute infarction, the primary pharmacological focus is on antiplatelet therapy and stabilization of the plaque, rather than calcium channel blockade, which does not have the same mortality benefit in the acute STEMI setting.",
                    "**Incorrect:** Beta-blockers are used in the management of myocardial infarction to minimize negative effects from sympathetic nervous system activation, but they should be used with caution in this patient who shows signs of early congestion and borderline blood pressure.\n\nBeta-blockers can decrease contractility, which might exacerbate heart failure in a patient with acute left ventricular dysfunction. They are not the absolute priority over antiplatelet therapy in the first minutes of care and should only be initiated within 24 hours if the patient is hemodynamically stable.",
                    "**Correct!** Dual antiplatelet therapy, consisting of aspirin and a P2Y12 inhibitor (such as clopidogrel, ticagrelor, or prasugrel), is foundational in the management of acute coronary syndrome (ACS) to prevent further thrombus propagation and stabilize the culprit lesion.\n\nThese agents work through different mechanisms to inhibit platelet aggregation, which is critical since the mechanism of the infarct involves plaque rupture and blood clot formation. This therapy significantly reduces the risk of recurrent ischemic events and mortality following the index STEMI.",
                    "**Incorrect:** Nitrates are used to relieve ischemic pain by promoting vasodilation and reducing preload; however, they have not been shown to reduce mortality in the setting of acute STEMI.\n\nIn a patient with borderline blood pressure and evidence of potential low output, nitrates must be used with caution as they can trigger profound hypotension, which may complicate the patient's hemodynamic status."
                ]
            }
        ]
    },
   "case7": {
        "button_label": "Case 7",
        "difficulty": "Intermediate",
        "title": "Clinical Case 7",
        "vignette": "A 32-year-old man presents to the emergency department complaining of sharp, stabbing chest pain that began abruptly yesterday morning. He rates the pain as 9/10 and states it is excruciating when he takes a deep breath or lies flat on the stretcher. However, the pain is significantly relieved when he sits up and leans forward. He mentions having a bad flu-like illness two weeks ago.\n\nAuscultation at the left lower sternal border reveals a high-pitched, scratchy, leathery sound with three distinct components, which persists even when the patient holds his breath. His lungs are clear to auscultation, and there is no evidence of wheezing or crackles indicating an alternative pulmonary pathology.",
        "initial_labs": {"BP": "120/80 mmHg", "HR": "95 bpm", "Temp": "38.1°C"},
        "steps": [
            {
                "question": "Integrating the postural nature of the chest pain and the pathognomonic physical exam finding, what is the diagnosis?",
                "options": ["Acute STEMI", "Unstable Angina", "Acute Viral Pericarditis", "Infective Endocarditis"],
                "correct_idx": 2,
                "svg": "ecg_stemi_vs_peri",
                "explanations": [
                    "**Incorrect:** STEMI pain is characteristically described as a crushing or heavy substernal pressure that radiates to the jaw or arms, and it is notably unaffected by changes in body position or respiratory cycles.",
                    "**Incorrect:** Unstable angina represents a form of acute coronary syndrome defined by myocardial ischemia at rest, but it does not produce the positional relief seen in this patient nor does it cause a friction rub.",
                    "**Correct!** The diagnosis is Acute Viral Pericarditis, supported by the classic triad of pleuritic chest pain relieved by leaning forward, a history of a recent viral illness, and the pathognomonic pericardial friction rub.",
                    "**Incorrect:** Infective endocarditis typically presents with persistent fever, systemic embolization, and the development of new heart murmurs, rather than the sharp, positional chest pain and three-component friction rub found here."
                ]
            },
            {
                "question": "An ECG is obtained. What specific finding differentiates this condition from an acute ST-elevation myocardial infarction (STEMI)?",
                "options": ["Focal ST elevations in leads II, III, and aVF with reciprocal ST depressions in lead aVL", "Diffuse, concave-upward ST elevations across all precordial leads with concurrent PR segment depressions", "Deep, pathological Q waves appearing in the anterior leads", "A progressively lengthening PR interval until a QRS complex is dropped"],
                "correct_idx": 1,
                "svg": "ecg_pericarditis",
                "explanations": [
                    "**Incorrect:** Focal ST segment elevations accompanied by reciprocal depressions in opposite leads are the definitive electrocardiographic markers of an acute, focal ischemic event such as a STEMI, which occurs within a specific coronary arterial distribution rather than affecting the entire heart surface.",
                    "**Correct!** The presence of diffuse, concave-upward ST elevations and PR segment depressions is the hallmark of pericarditis, reflecting generalized epicardial and atrial inflammation. Unlike a STEMI, these changes are not limited to a single coronary territory and lack the reciprocal ST depressions that characterize focal ischemia, providing a vital diagnostic distinction.",
                    "**Incorrect:** Deep and wide pathological Q waves are classic indicators of established, transmural myocardial scar tissue resulting from a completed infarction, which does not align with the acute, inflammatory nature of the pericardial pathology seen in this patient’s presentation.",
                    "**Incorrect:** The finding of a progressively lengthening PR interval leading to a dropped QRS complex describes a Mobitz Type I or second-degree AV block. This is a specific electrical conduction system anomaly and does not serve as a diagnostic marker for the inflammatory surface processes found in pericarditis."
                ],
                "unlock_labs": {"ECG": "Diffuse ST elevation, PR depression in lead II, PR elevation in aVR"}
            },
            {
                "question": "If this patient's condition rapidly deteriorated, producing severe hypotension, muffled heart sounds, and jugular venous distention, what physiological equalization would be occurring?",
                "options": ["Equalization of left and right ventricular systolic pressures", "Equalization of diastolic pressures across all four cardiac chambers", "Equalization of systemic and pulmonary arterial pressures", "Equalization of aortic and left ventricular systolic pressures"],
                "correct_idx": 1,
                "svg": "becks_triad",
                "explanations": [
                    "**Incorrect:** Ventricular systolic pressures remain significantly different because the left ventricle is highly muscular and capable of generating high pressures to overcome systemic vascular resistance, even in the presence of external compression from a pericardial effusion.",
                    "**Correct!** The clinical triad of hypotension, muffled heart sounds, and JVD defines Beck's Triad, indicating cardiac tamponade. In this state, rapidly rising intrapericardial pressure restricts diastolic filling, forcing the diastolic pressures of all four cardiac chambers to equalize at a pathologically elevated level, which severely limits venous return and reduces overall stroke volume.",
                    "**Incorrect:** The systemic and pulmonary circulatory circuits maintain fundamentally different baseline resistances, which prevents the equalization of their respective arterial pressures, even during states of obstructive shock caused by tamponade or other forms of hemodynamic instability.",
                    "**Incorrect:** Equalization of aortic and left ventricular pressures is a standard feature of normal cardiac physiology during the ejection phase when the aortic valve is wide open, and this does not represent the pathological state of restrictive filling found in cardiac tamponade."
                ],
                "unlock_labs": {"Echo": "Small pericardial effusion, NO right ventricular diastolic collapse"}
            },
            {
                "question": "Which of the following is the most appropriate first-line pharmacologic treatment for this patient?",
                "options": ["Intravenous corticosteroids", "High-dose aspirin or NSAIDs with colchicine", "Urgent pericardial window surgery", "High-dose opioids"],
                "correct_idx": 1,
                "explanations": [
                    "**Incorrect:** Intravenous corticosteroids are not indicated as first-line therapy because they have been consistently associated with an increased risk of symptom recurrence in viral pericarditis and are generally reserved for cases that fail to respond to standard anti-inflammatory regimens.",
                    "**Correct!** High-dose aspirin or NSAIDs are the cornerstones of initial management for viral pericarditis to decrease pain and inflammation, while the addition of colchicine is now considered standard care to reduce the probability of future recurrence for patients presenting with this inflammatory condition.",
                    "**Incorrect:** Urgent surgical interventions such as a pericardial window or pericardiocentesis are reserved exclusively for patients who demonstrate clear clinical signs of hemodynamic compromise or cardiac tamponade, which is not the case for this patient given his current stable vital signs.",
                    "**Incorrect:** High-dose opioids may provide temporary pain relief in the emergency setting, but they do not address the underlying inflammatory process that causes pericarditis and therefore serve no role as a primary therapeutic approach in the management of this condition."
                ]
            },
            {
                "question": "If this patient had a concomitant acute kidney injury (AKI), which pharmacologic adjustment would be most appropriate?",
                "options": ["Continue NSAIDs at standard doses, but add a proton pump inhibitor", "Avoid NSAIDs and utilize colchicine as monotherapy or consider corticosteroids if necessary", "Switch to high-dose acetaminophen for pain control", "Increase the dose of colchicine to comepensate for reduced renal clearance"],
                "correct_idx": 1,
                "explanations": [
                    "**Incorrect:** Continuing NSAID therapy in a patient with acute kidney injury is inappropriate because these medications can further impair renal perfusion by inhibiting the prostaglandins that maintain afferent arteriolar vasodilation, potentially leading to irreversible renal damage.",
                    "**Correct!** In the presence of an acute kidney injury, NSAIDs must be avoided to prevent further renal harm. The most appropriate strategy is to use colchicine monotherapy for inflammation or to carefully evaluate the use of corticosteroids if the condition remains refractory to treatment, provided renal function is monitored.",
                    "**Incorrect:** While acetaminophen is a useful analgesic for general pain management, it lacks the necessary anti-inflammatory properties required to suppress the active pericardial inflammation and will not effectively treat the underlying pathology of the patient's condition.",
                    "**Incorrect:** Increasing the dose of colchicine is dangerous because the drug is primarily eliminated through renal pathways, and any reduction in glomerular filtration rate necessitates a cautious dose reduction rather than an increase to prevent the development of severe drug toxicity."
                ]
            }
        ]
    },
"case8": {
        "button_label": "Case 8",
        "difficulty": "Foundational",
        "title": "Clinical Case 8",
        "vignette": "A 74-year-old woman presents to the clinic reporting two weeks of intermittent palpitations and decreased exercise tolerance. She describes the sensation as her heart 'fluttering' in her chest, often occurring when she is performing light household activities. She denies any chest pain, syncope, or shortness of breath while at rest.\n\nPhysical examination reveals an irregularly irregular heart rhythm with a ventricular rate of 115 bpm. Her blood pressure is 128/78 mmHg, and her lungs are clear to auscultation. There are no signs of peripheral edema or jugular venous distention, and the remainder of the cardiovascular examination is unremarkable.",
        "steps": [
            {
                "question": "Given the patient's physical examination findings, which of the following is the most likely diagnosis?",
                "options": [
                    "Sinus tachycardia",
                    "Atrial fibrillation",
                    "Second-degree AV block",
                    "Ventricular tachycardia"
                ],
                "correct_idx": 1,
                "svg": "ecg_afib",
                "explanations": [
                    "**Incorrect:** Sinus tachycardia typically presents with a regular rhythm driven by the sinus node, unlike the irregular rhythm observed in this patient.",
                    "**Correct!** Atrial fibrillation is characterized by a rapid, chaotic rhythm of the cardiac atria, which typically results in an irregularly irregular ventricular rhythm, matching this patient's clinical presentation.",
                    "**Incorrect:** A second-degree AV block would generally present with a dropped QRS complex and would not account for the rapid, irregular palpitations described.",
                    "**Incorrect:** Ventricular tachycardia is a life-threatening, usually regular and wide-complex rhythm that presents very differently from this stable clinical picture."
                ]
            },
            {
                "question": "What is the underlying pathophysiology of atrial fibrillation?",
                "options": [
                    "Complete blockage of the AV node",
                    "Rapid, chaotic electrical activity in the atria leading to mechanical inefficiency",
                    "Increased automaticity of the ventricles",
                    "Excessive parasympathetic tone slowing the sinus node"
                ],
                "correct_idx": 1,
                "svg": "ecg_afib",
                "explanations": [
                    "**Incorrect:** Complete blockage of the AV node would result in bradycardia, not the rapid, chaotic atrial activity seen in this condition.",
                    "**Correct!** The pathophysiology involves rapid, chaotic electrical pathways in the atria, causing mechanical inefficiency where the atria do not contract effectively, leading to an irregular ventricular response.",
                    "**Incorrect:** Atrial fibrillation is defined by atrial, not ventricular, electrical abnormalities.",
                    "**Incorrect:** While autonomic tone can influence heart rate, it is not the primary cause of the chaotic electrical pathways characterizing atrial fibrillation."
                ]
            },
            {
                "question": "Which of the following best describes the relationship between this patient's diagnosis and stroke risk?",
                "options": [
                    "Atrial fibrillation is an independent risk factor that increases stroke risk approximately 3-5 fold",
                    "Atrial fibrillation reduces stroke risk by increasing blood flow velocity in the left atrium",
                    "Stroke risk is solely determined by age, regardless of the presence of atrial fibrillation",
                    "Stroke risk only exists when the patient is actively symptomatic with palpitations"
                ],
                "correct_idx": 0,
                "explanations": [
                    "**Correct!** Atrial fibrillation is an independent risk factor imparting an approximately 3-5 fold increased risk of cerebrovascular accident.",
                    "**Incorrect:** Atrial fibrillation causes blood stasis in the atrium, particularly the left atrial appendage, rather than increasing blood flow velocity.",
                    "**Incorrect:** While age is a risk factor, atrial fibrillation independently and significantly increases the risk of stroke regardless of age.",
                    "**Incorrect:** Stroke risk persists in patients with atrial fibrillation, and events can occur whether or not the patient is actively in an arrhythmia episode."
                ]
            },
            {
                "question": "Which of the following medication pairs correctly matches the therapeutic strategy to the class of drug?",
                "options": [
                    "Rate control: Diltiazem; Rhythm control: Amiodarone",
                    "Rate control: Flecainide; Rhythm control: Beta blockers",
                    "Rate control: Dofetilide; Rhythm control: Digoxin",
                    "Rate control: Sotalol; Rhythm control: Verapamil"
                ],
                "correct_idx": 0,
                "explanations": [
                    "**Correct!** Diltiazem is a non-dihydropyridine calcium channel blocker used for ventricular rate control, while amiodarone is an antiarrhythmic drug used for rhythm control strategies.",
                    "**Incorrect:** Flecainide is an antiarrhythmic used for rhythm control, whereas beta blockers are typically used for rate control.",
                    "**Incorrect:** Dofetilide is an antiarrhythmic used for rhythm control, while digoxin is primarily used for rate control in atrial fibrillation.",
                    "**Incorrect:** Sotalol is an antiarrhythmic used for rhythm control, and verapamil is a calcium channel blocker used for rate control."
                ]
            },
            {
                "question": "If this patient were to present with severe hypotension and altered mental status, what would be the most appropriate management?",
                "options": [
                    "Immediate synchronized electrical cardioversion",
                    "Observation and repeat vitals in one hour",
                    "Initiation of oral beta-blocker therapy",
                    "Cardiac catheterization without delay"
                ],
                "correct_idx": 0,
                "explanations": [
                    "**Correct!** Immediate synchronized electrical cardioversion is indicated for patients who are hemodynamically unstable, such as those presenting with hypotension or altered mental status, to restore sinus rhythm.",
                    "**Incorrect:** Observation is inappropriate for a patient presenting with hemodynamic instability and signs of organ hypoperfusion.",
                    "**Incorrect:** Oral medications are not sufficient for a patient who is hemodynamically unstable and requires immediate rhythm restoration.",
                    "**Incorrect:** While catheterization may be required for specific cardiac emergencies, immediate cardioversion is the priority for arrhythmia-related hemodynamic collapse."
                ]
            }
        ]
    },
"case9": {
        "button_label": "Case 9",
        "difficulty": "Foundational",
        "title": "Clinical Case 9",
        "vignette": "A 62-year-old man presents complaining of a severe, cramping ache in his bilateral calves that occurs every time he walks to the mailbox (about 1 block). The pain is debilitating, forcing him to stop walking. It completely and predictably resolves after 2 minutes of standing still. He has a 40 pack-year smoking history.\n\nHis cardiovascular exam is normal. Inspection of his lower extremities reveals thin, shiny skin with an obvious loss of hair below the knees. Palpation reveals that both the dorsalis pedis and posterior tibial pulses are extremely faint and barely palpable bilaterally. There is no edema.",
        "steps": [
            {
                "question": "What diagnostic test is the absolute best FIRST step to confirm the suspected vascular pathology in the clinic?",
                "options": [
                    "Lower extremity venous Doppler ultrasound",
                    "Measurement of the Ankle-Brachial Index (ABI)",
                    "CT Angiography of the lower extremities",
                    "Measurement of serum D-dimer"
                ],
                "correct_idx": 1,
                "svg": "abi_diagram",
                "explanations": [
                    "**Incorrect:** Venous ultrasounds map the deep veins to rule out DVT, which presents with acute unilateral swelling and pain, not predictable exertional claudication. This diagnostic tool is fundamentally targeted at venous, rather than arterial, pathology. Using this test for an arterial issue would fail to capture the occlusive disease located in the systemic arteries. Therefore, it is the wrong modality for the initial evaluation of this patient.",
                    "**Correct!** The Ankle-Brachial Index (ABI) is the gold-standard, first-line diagnostic test for Peripheral Artery Disease. It is a simple, non-invasive bedside test that compares the systolic blood pressure at the ankle to the systolic blood pressure in the arm using a Doppler probe. A normal ratio is 1.0 to 1.4, while an ABI of <0.9 confirms significant peripheral arterial occlusive disease by demonstrating a massive pressure drop across the obstruction. An ABI <0.4 indicates severe disease with a high risk for resting ischemia or tissue loss.",
                    "**Incorrect:** CT Angiography is highly specific but exposes the patient to radiation and intravenous contrast, which may not be necessary for an initial diagnosis. It is reserved for anatomical mapping precisely before surgical revascularization, rather than being used for initial screening of stable symptoms. By opting for this invasive imaging too early, the clinician exposes the patient to unnecessary risks and costs. Therefore, it is not the most appropriate first-line diagnostic test to confirm the presence of arterial disease.",
                    "**Incorrect:** D-dimer is used to rule out active thrombosis, such as DVT or pulmonary embolism, rather than identifying chronic atherosclerotic flow limitations. This laboratory test is not designed to assess for the fixed plaque stenoses that cause predictable exertional limb pain. Ordering this test would not provide any information regarding the patency or pressure gradients of the lower extremity arteries. Consequently, it remains an ineffective diagnostic strategy for a patient presenting with classic intermittent claudication."
                ],
                "unlock_labs": {
                    "ABI": "0.65 Right, 0.68 Left"
                }
            },
            {
                "question": "What is the primary biochemical driver of the severe muscular pain he experiences while walking?",
                "options": [
                    "Rupture of a localized atherosclerotic plaque causing acute thromboembolic showers to the calf",
                    "Accumulation of anaerobic metabolic byproducts due to flow-limiting stenoses failing to meet exertional oxygen demand",
                    "Diabetic microvascular demyelination of the peripheral sensory nerves",
                    "Venous valvular incompetence causing massive blood pooling and tissue stretch"
                ],
                "correct_idx": 1,
                "svg": "abi_diagram",
                "explanations": [
                    "**Incorrect:** Acute plaque rupture in the leg causes Acute Limb Ischemia, which is a surgical emergency characterized by the '6 P's': Pain, Pallor, Pulselessness, Paresthesia, Paralysis, and Poikilothermia. Unlike stable claudication, this condition presents with severe pain at rest and requires immediate intervention to save the limb. Because this patient’s pain is predictable and resolves with rest, it is not due to an acute embolic event. Therefore, this answer choice incorrectly identifies the underlying temporal nature of the patient's pathology.",
                    "**Correct!** Intermittent claudication is effectively 'stable angina of the legs,' caused by fixed atherosclerotic stenoses in the peripheral arteries failing to meet the muscle's increased demand during exertion. During walking, the skeletal muscles demand massive increases in oxygen, but the plaque-blocked arteries cannot provide adequate hyperemic flow, forcing tissues into anaerobic metabolism. The resulting buildup of acidic metabolic byproducts—specifically lactic acid and adenosine—directly stimulates local nociceptors, causing severe cramping pain. When the patient rests, the oxygen demand drops, the byproducts are washed away, and the pain resolves.",
                    "**Incorrect:** Diabetic neuropathy causes a continuous, burning, stocking-glove paresthesia present even at rest, which is entirely unlinked to physical exertion. While diabetes is a risk factor for PAD, the specific pain pattern of intermittent claudication is ischemic in origin rather than neuropathic. The pain of claudication is deep and cramping, whereas neuropathic pain is characteristically burning or shooting. Consequently, this choice fails to explain why the patient's pain predictably occurs only during walking and disappears during standing rest.",
                    "**Incorrect:** Venous insufficiency causes leg heaviness, massive swelling, and hyperpigmentation known as stasis dermatitis that often improves with leg elevation, completely unlike this patient's ischemic presentation. Chronic venous disease involves valvular incompetence leading to blood pooling, which is a structural issue very different from the arterial blockage found in PAD. The patient shows no signs of edema or skin color changes consistent with venous pooling. Thus, this mechanism does not align with the patient’s clinical symptoms or the absence of lower extremity edema."
                ],
                "unlock_labs": {
                    "Lipid Panel": "Total Cholesterol 240, LDL 185"
                }
            },
            {
                "question": "Based on the exertional pain, tissue changes, and abnormal ABI, what is the definitive diagnosis?",
                "options": [
                    "Deep Vein Thrombosis (DVT)",
                    "Peripheral Artery Disease (PAD)",
                    "Lumbar Spinal Stenosis",
                    "Chronic Venous Insufficiency"
                ],
                "correct_idx": 1,
                "explanations": [
                    "**Incorrect:** DVT causes acute, unilateral, warm, and swollen leg pain that is typically present at rest rather than brought on by exertion. This condition is related to venous thrombosis, not the chronic atherosclerotic narrowing of systemic arteries that causes the symptoms seen in this patient. Since the patient exhibits bilateral symptoms and shows no signs of acute inflammation or swelling, DVT is an inappropriate diagnosis. Therefore, this choice ignores the classic, predictable, and long-term nature of the patient's intermittent claudication.",
                    "**Correct!** The patient has Peripheral Artery Disease (PAD), and his presentation of intermittent claudication is classic for this atherosclerotic condition. Physical exam findings of thin, shiny skin, hair loss, and diminished pulses represent chronic, long-term tissue ischemia failing to support normal dermal structures. The ABI of ~0.65 definitively proves a severe atherosclerotic flow limitation, which is the hallmark of the disease. Because the core pathophysiology is identical to coronary artery disease, this patient is at an exceptionally high risk for concurrent myocardial infarction and requires aggressive risk factor modification.",
                    "**Incorrect:** Lumbar spinal stenosis causes 'pseudoclaudication,' a neurogenic condition characterized by pain that often radiates down the back of the legs. This pain is typically relieved by leaning forward in the 'shopping cart sign' position rather than by simply standing still. While it can mimic claudication, the patient’s physical exam reveals diminished pulses and thin skin, which are specific signs of arterial insufficiency, not neurological entrapment. Thus, a neurological diagnosis fails to account for the clear, systemic evidence of peripheral arterial disease.",
                    "**Incorrect:** Chronic venous insufficiency features pitting edema, varicosities, and medial malleolus ulcers, none of which are present in this specific patient. The pathology here is dominated by arterial, rather than venous, dysfunction, as evidenced by the abnormal ABI and the lack of fluid accumulation in the lower limbs. Venous disease typically involves problems with returning blood to the heart, whereas this patient is struggling with the supply of oxygenated blood. Consequently, the findings and clinical symptoms do not support a diagnosis of venous insufficiency."
                ]
            }
        ]
    }
}


def svg_becks_triad():
    W, H = 800, 360
    inner = f'''
  <text x="400" y="20" text-anchor="middle" font-family="Inter,sans-serif" font-size="13" fill="#E74C3C" font-weight="600">Cardiac Tamponade: Diastolic Pressure Equalization</text>
  <ellipse cx="310" cy="185" rx="210" ry="145" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="8,4"/>
  <text x="310" y="348" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">Pericardial effusion compressing all chambers</text>
  <rect x="190" y="80" width="100" height="75" rx="8" fill="rgba(231,76,60,0.15)" stroke="#E74C3C" stroke-width="2"/>
  <text x="240" y="110" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1" font-weight="600">RA</text>
  <text x="240" y="128" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">EDP = 18 mmHg</text>
  <text x="240" y="143" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E67E22">&#8593; elevated</text>
  <rect x="190" y="185" width="100" height="75" rx="8" fill="rgba(231,76,60,0.15)" stroke="#E74C3C" stroke-width="2"/>
  <text x="240" y="215" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1" font-weight="600">RV</text>
  <text x="240" y="233" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">EDP = 18 mmHg</text>
  <text x="240" y="248" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E67E22">&#8593; elevated</text>
  <rect x="320" y="80" width="100" height="75" rx="8" fill="rgba(231,76,60,0.15)" stroke="#E74C3C" stroke-width="2"/>
  <text x="370" y="110" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1" font-weight="600">LA</text>
  <text x="370" y="128" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">EDP = 18 mmHg</text>
  <text x="370" y="143" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E67E22">&#8593; elevated</text>
  <rect x="320" y="185" width="100" height="75" rx="8" fill="rgba(231,76,60,0.15)" stroke="#E74C3C" stroke-width="2"/>
  <text x="370" y="215" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" fill="#ECF0F1" font-weight="600">LV</text>
  <text x="370" y="233" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">EDP = 18 mmHg</text>
  <text x="370" y="248" text-anchor="middle" font-family="Inter,sans-serif" font-size="9" fill="#E67E22">&#8593; elevated</text>
  <text x="307" y="125" text-anchor="middle" font-family="Inter,sans-serif" font-size="18" fill="#E67E22" font-weight="700">=</text>
  <text x="307" y="232" text-anchor="middle" font-family="Inter,sans-serif" font-size="18" fill="#E67E22" font-weight="700">=</text>
  <text x="240" y="175" text-anchor="middle" font-family="Inter,sans-serif" font-size="18" fill="#E67E22" font-weight="700">=</text>
  <text x="370" y="175" text-anchor="middle" font-family="Inter,sans-serif" font-size="18" fill="#E67E22" font-weight="700">=</text>
  <rect x="540" y="60" width="225" height="235" rx="8" fill="rgba(26,188,156,0.06)" stroke="#2C3E50" stroke-width="1.5"/>
  <text x="652" y="82" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#1ABC9C" font-weight="600">Normal vs. Tamponade</text>
  <text x="556" y="104" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">Chamber</text>
  <text x="680" y="104" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#95A5A6">Normal</text>
  <text x="750" y="104" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">Tamponade</text>
  <line x1="556" y1="110" x2="755" y2="110" stroke="#2C3E50" stroke-width="1"/>
  <text x="556" y="126" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">RA EDP</text>
  <text x="680" y="126" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">0-8</text>
  <text x="750" y="126" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">~18</text>
  <text x="556" y="146" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">RV EDP</text>
  <text x="680" y="146" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">0-8</text>
  <text x="750" y="146" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">~18</text>
  <text x="556" y="166" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">LA EDP (PCWP)</text>
  <text x="680" y="166" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">6-12</text>
  <text x="750" y="166" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">~18</text>
  <text x="556" y="186" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">LV EDP</text>
  <text x="680" y="186" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#1ABC9C">5-12</text>
  <text x="750" y="186" text-anchor="middle" font-family="Inter,sans-serif" font-size="10" fill="#E74C3C">~18</text>
  <line x1="556" y1="196" x2="755" y2="196" stroke="#2C3E50" stroke-width="1"/>
  <text x="556" y="214" font-family="Inter,sans-serif" font-size="9.5" fill="#E67E22">All pressures equalize &#8594;</text>
  <text x="556" y="230" font-family="Inter,sans-serif" font-size="9.5" fill="#E67E22">venous return collapses</text>
  <text x="556" y="246" font-family="Inter,sans-serif" font-size="9.5" fill="#E67E22">stroke volume falls</text>
  <text x="556" y="262" font-family="Inter,sans-serif" font-size="9.5" fill="#E67E22">&#8594; obstructive shock</text>
  <rect x="30" y="60" width="148" height="110" rx="6" fill="rgba(192,57,43,0.12)" stroke="#C0392B" stroke-width="1.5"/>
  <text x="104" y="80" text-anchor="middle" font-family="Inter,sans-serif" font-size="11" fill="#E74C3C" font-weight="600">Beck's Triad</text>
  <text x="44" y="100" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">1. Hypotension</text>
  <text x="44" y="118" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">2. Muffled heart sounds</text>
  <text x="44" y="136" font-family="Inter,sans-serif" font-size="10" fill="#ECF0F1">3. JVD</text>
  <line x1="44" y1="144" x2="165" y2="144" stroke="#2C3E50" stroke-width="1"/>
  <text x="44" y="160" font-family="Inter,sans-serif" font-size="9.5" fill="#E67E22">Tx: Pericardiocentesis</text>
    '''
    return svg_wrap(inner, W, H, "", "")


# SVG DIAGRAM REGISTRY
# Maps string keys used in step data to generator functions
# ===============================
SVG_DIAGRAMS = {
    "frank_starling_hfref":       svg_frank_starling_hfref,
    "frank_starling_neurohormonal": svg_frank_starling_neurohormonal,
    "frank_starling_four_pillars": svg_frank_starling_four_pillars,
    "pv_loop_hfpef":              svg_pv_loop_hfpef,
    "pv_loop_mr":                 svg_pv_loop_mr,
    "pv_loop_ar":                 svg_pv_loop_ar,
    "pv_loop_as":                 svg_pv_loop_as,
    "ecg_normal_sinus":           svg_ecg_normal_sinus,
    "ecg_afib":                   svg_ecg_afib,
    "ecg_stemi":                  svg_ecg_stemi,
    "ecg_pericarditis":           svg_ecg_pericarditis,
    "ecg_stemi_vs_peri":          svg_ecg_stemi_vs_peri,
    "abi_diagram":                svg_abi_diagram,
    "troponin_curve":             svg_troponin_curve,
    "murmur_timing":              svg_murmur_timing,
    "becks_triad":                svg_becks_triad,
}

# ===============================
# HELPER FUNCTIONS
# ===============================
def get_score_for_case(case_id):
    return st.session_state.scores.get(case_id, {"correct": 0, "total": 0})

def total_score():
    c = sum(v["correct"] for v in st.session_state.scores.values())
    t = sum(v["total"] for v in st.session_state.scores.values())
    return c, t

def md_to_html(text):
    import re
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = text.replace('\n\n', '<br><br>').replace('\n', ' ')
    return text

# ===============================
# SESSION STATE INITIALIZATION
# ===============================
defaults = {
    "step": 0,
    "case_choice": None,
    "answered": False,
    "current_labs": {},
    "scores": {},
    "feedback_html": None,
    "selected_option": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("## 🫀 CV Simulator")
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
        <div class="stat-pill"><span class="s-label">Progress</span><span class="s-value">Step {st.session_state.step + 1} / {total_steps}</span></div>
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
            st.session_state.feedback_html = None
            st.rerun()

    st.markdown("---")
    if st.button("🏠 Main Menu", key="sidebar_home"):
        st.session_state.case_choice = None
        st.session_state.step = 0
        st.session_state.answered = False
        st.session_state.feedback_html = None
        st.rerun()

# ===============================
# MAIN CONTENT
# ===============================
st.markdown("""
<div class="app-header">
<h1>Cardiovascular Physiology Simulator</h1>
<p>M2-Level Clinical Case Engine · Pathophysiology · Hemodynamics · Diagnosis · Management</p>
</div>
""", unsafe_allow_html=True)

# ---- HOME SCREEN ----
if st.session_state.case_choice is None:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Select a Clinical Case")
        st.markdown("Each case presents a clinical vignette followed by rigorous pathophysiology and management questions. Complete all steps to earn a full score.")
    with c2:
        c, t = total_score()
        if t > 0:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-number">{c}/{t}</div>
                <div class="score-label">Questions Correct · {int(c/t*100)}% accuracy</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Difficulty filter
    diff_filter = st.selectbox("Filter by difficulty:", ["All", "Foundational", "Intermediate", "Advanced"], index=0)

    keys = list(CASES_DATA.keys())
    if diff_filter != "All":
        keys = [k for k in keys if CASES_DATA[k]["difficulty"] == diff_filter]

    cols = st.columns(3)
    for i, case_id in enumerate(keys):
        case = CASES_DATA[case_id]
        sc = get_score_for_case(case_id)
        n_steps = len(case["steps"])
        done = sc["total"] >= n_steps
        in_progress = 0 < sc["total"] < n_steps
        status = "✅ Complete" if done else ("🔵 In Progress" if in_progress else "⚪ Not Started")
        diff_color = {"Foundational": "#27AE60", "Intermediate": "#E67E22", "Advanced": "#C0392B"}.get(case["difficulty"], "#fff")

        with cols[i % 3]:
            st.markdown(f"""
            <div class="case-card">
                <h4>{case['button_label']}</h4>
                <p style="margin-top:8px;font-size:0.75rem;">
                    <span style="color:{diff_color};font-weight:600;">{case['difficulty']}</span>
                    &nbsp;·&nbsp; {n_steps} questions &nbsp;·&nbsp; {status}
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"▶ Start {case['button_label']}", key=f"home_btn_{case_id}"):
                st.session_state.case_choice = case_id
                st.session_state.current_labs = CASES_DATA[case_id].get("initial_labs", {}).copy()
                st.session_state.step = 0
                st.session_state.answered = False
                st.session_state.feedback_html = None
                st.rerun()

# ---- CASE SCREEN ----
else:
    active_case = CASES_DATA[st.session_state.case_choice]
    step_idx = st.session_state.step
    total_steps = len(active_case["steps"])
    sc = get_score_for_case(st.session_state.case_choice)

    # Case header
    st.markdown(f"""
    <h2 style="margin-top:4px;margin-bottom:4px;">{active_case['button_label']}</h2>
    <p style="color:#95A5A6;font-size:0.85rem;margin-bottom:16px;">
        Difficulty: {active_case['difficulty']} &nbsp;·&nbsp; {total_steps} questions &nbsp;·&nbsp; Score: {sc['correct']}/{sc['total']}
    </p>
    """, unsafe_allow_html=True)

    # Step progress bar
    pip_html = '<div class="step-bar">'
    for i in range(total_steps):
        cls = "done" if i < step_idx else ("active" if i == step_idx else "")
        pip_html += f'<div class="step-pip {cls}"></div>'
    pip_html += '</div>'
    st.markdown(pip_html, unsafe_allow_html=True)

    # Vignette
    with st.expander("📄 Clinical Vignette", expanded=(step_idx == 0)):
        st.markdown(f'<div class="vignette-box">{active_case["vignette"]}</div>', unsafe_allow_html=True)

    # Vitals & Labs strip
    lab_items = "".join([
        f'<div class="lab-item"><span class="lab-label">{k}</span><span class="lab-value">{v}</span></div>'
        for k, v in st.session_state.current_labs.items()
    ])
    st.markdown(f'<div class="labs-strip"><strong style="color:#95A5A6;font-size:0.78rem;">🧪 VITALS &amp; LABS</strong><div class="lab-row">{lab_items}</div></div>', unsafe_allow_html=True)

    # Completion check
    if step_idx >= total_steps:
        cs = get_score_for_case(st.session_state.case_choice)
        pct_case = int(cs["correct"] / cs["total"] * 100) if cs["total"] else 0
        grade = "🏆 Excellent" if pct_case >= 80 else ("👍 Good" if pct_case >= 60 else "📚 Review Recommended")
        st.markdown(f"""
        <div class="complete-banner">
            <h2>✅ Case Complete!</h2>
            <p style="font-size:1.1rem;color:#ECF0F1;">You scored <strong style="color:#1ABC9C;">{cs['correct']} / {cs['total']}</strong> ({pct_case}%) — {grade}</p>
            <p style="color:#95A5A6;font-size:0.85rem;">Review the vignette above and select another case to continue.</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

    else:
        current_step = active_case["steps"][step_idx]

        # Question card
        st.markdown(f"""
        <div class="question-card">
            <div class="question-number">Question {step_idx + 1} of {total_steps}</div>
            <div class="question-text">{current_step['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        ans = st.radio(
            "Select your answer:",
            current_step["options"],
            key=f"radio_{step_idx}",
            index=None
        )

        col_submit, col_next = st.columns([1, 1])

        with col_submit:
            if st.button("✅ Submit Answer", key=f"submit_{step_idx}", disabled=(st.session_state.answered and st.session_state.get("last_correct", False)) or ans is None):
                selected_idx = current_step["options"].index(ans)
                is_correct = (selected_idx == current_step["correct_idx"])

                # Score tracking — only count first attempt per question
                case_id = st.session_state.case_choice
                if case_id not in st.session_state.scores:
                    st.session_state.scores[case_id] = {"correct": 0, "total": 0}
                first_attempt = not st.session_state.get("feedback_html")
                if first_attempt:
                    st.session_state.scores[case_id]["total"] += 1
                    if is_correct:
                        st.session_state.scores[case_id]["correct"] += 1
                st.session_state["last_correct"] = is_correct

                exp_html = md_to_html(current_step["explanations"][selected_idx])
                if is_correct:
                    st.session_state.feedback_html = ("correct", exp_html, current_step.get("svg"))
                    if "unlock_labs" in current_step:
                        st.session_state.current_labs.update(current_step["unlock_labs"])
                else:
                    st.session_state.feedback_html = ("wrong", exp_html, current_step.get("svg"))

                # Only lock submission if correct; wrong allows retry
                if is_correct:
                    st.session_state.answered = True
                st.rerun()

        with col_next:
            if st.session_state.answered and step_idx < total_steps - 1:
                if st.button("Next Question ➡️", key=f"next_{step_idx}"):
                    st.session_state.step += 1
                    st.session_state.answered = False
                    st.session_state["last_correct"] = False
                    st.session_state.feedback_html = None
                    st.rerun()
            elif st.session_state.answered and step_idx == total_steps - 1:
                if st.button("Finish Case 🏁", key=f"finish_{step_idx}"):
                    st.session_state.step += 1
                    st.session_state.answered = False
                    st.session_state.feedback_html = None
                    st.rerun()

        # Feedback
        if st.session_state.feedback_html:
            feedback_data = st.session_state.feedback_html
            kind, html = feedback_data[0], feedback_data[1]
            svg_key = feedback_data[2] if len(feedback_data) > 2 else None
            if kind == "correct":
                st.markdown(f'<div class="feedback-correct">✅ &nbsp;{html}</div>', unsafe_allow_html=True)
                if "unlock_labs" in current_step:
                    unlocked = ", ".join([f"{k}: {v}" for k, v in current_step["unlock_labs"].items()])
                    st.markdown(f'<div class="lab-unlocked">🔓 New lab result unlocked: {unlocked}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="feedback-wrong">❌ &nbsp;{html}</div>', unsafe_allow_html=True)
                st.markdown('<p style="color:#E67E22;font-size:0.85rem;margin-top:8px;">Review the explanation above and try again.</p>', unsafe_allow_html=True)
            # Render SVG diagram if attached to this question
            if svg_key:
                svg_fn = SVG_DIAGRAMS.get(svg_key)
                if svg_fn:
                    html_content, svg_h = svg_fn()
                    import streamlit.components.v1 as components
                    components.html(html_content, height=svg_h, scrolling=True)

    st.markdown("---")
    if st.button("↩️ Return to Main Menu"):
        st.session_state.case_choice = None
        st.session_state.step = 0
        st.session_state.answered = False
        st.session_state.feedback_html = None
        st.session_state.current_labs = {}
        st.rerun()