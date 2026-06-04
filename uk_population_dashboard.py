"""
UK Population Dashboard Generator
ONS Mid-Year Population Estimates 2024
Run: python3 uk_population_dashboard.py
Reads: mye24tablesuk.xlsx (same directory)
Output: uk_population_dashboard.html
"""

import pandas as pd
import json
import os
import sys

# Force UTF-8 output so emoji in print() don't crash on Windows (cp1252 terminals)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mye24tablesuk.xlsx")

def load_mye2(sheet):
    df = pd.read_excel(DATA_FILE, sheet_name=sheet, header=None, skiprows=7)
    cols = ["Code","Name","Geography","All_ages"] + [str(i) for i in range(90)] + ["90plus"]
    df.columns = cols
    df = df[df["Geography"] != "Geography"].copy()
    df["All_ages"] = pd.to_numeric(df["All_ages"], errors="coerce")
    for c in [str(i) for i in range(90)] + ["90plus"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_mye3():
    df = pd.read_excel(DATA_FILE, sheet_name="MYE3", header=None, skiprows=7)
    df.columns = ["Code","Name","Geography","Pop2023","Births","Deaths","NatChange",
                  "IntMigIn","IntMigOut","IntMigNet","IntlMigIn","IntlMigOut","IntlMigNet","Other","Pop2024"]
    df = df[df["Geography"] != "Geography"].copy()
    for c in ["Births","Deaths","NatChange","IntMigIn","IntMigOut","IntMigNet","IntlMigIn","IntlMigOut","IntlMigNet"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_mye4():
    df = pd.read_excel(DATA_FILE, sheet_name="MYE4", header=None, skiprows=7)
    years = list(range(2024, 2010, -1))
    df.columns = ["Code","Name","Geography"] + ["Mid"+str(y) for y in years]
    df = df[df["Geography"] != "Geography"].copy()
    for c in ["Mid"+str(y) for y in years]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_mye6():
    df = pd.read_excel(DATA_FILE, sheet_name="MYE6", header=None, skiprows=7)
    years = list(range(2024, 2010, -1))
    df.columns = ["Code","Name","Geography"] + ["Med"+str(y) for y in years]
    df = df[df["Geography"] != "Geography"].copy()
    for c in ["Med"+str(y) for y in years]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_mye1():
    df = pd.read_excel(DATA_FILE, sheet_name="MYE1", header=6)
    df.columns = ["Groups","UK","GB","EW","England","Wales","Scotland","NI"]
    df = df[df["Groups"].notna()]
    return df

print("[*] Loading Excel data...")
mye1  = load_mye1()
mye2p = load_mye2("MYE2 - Persons")
mye2f = load_mye2("MYE2 - Females")
mye2m = load_mye2("MYE2 - Males")
mye3  = load_mye3()
mye4  = load_mye4()
mye6  = load_mye6()

# ── KPIs
total_pop  = int(mye2p.loc[mye2p["Code"]=="K02000001","All_ages"].values[0])
female_pop = int(mye2f.loc[mye2f["Code"]=="K02000001","All_ages"].values[0])
male_pop   = int(mye2m.loc[mye2m["Code"]=="K02000001","All_ages"].values[0])
pop_2023   = int(mye4.loc[mye4["Code"]=="K02000001","Mid2023"].values[0])
pop_2011   = int(mye4.loc[mye4["Code"]=="K02000001","Mid2011"].values[0])
yoy_growth = round((total_pop - pop_2023) / pop_2023 * 100, 2)
median_age = float(mye6.loc[mye6["Code"]=="K02000001","Med2024"].values[0])
uk_births  = int(mye3.loc[mye3["Code"]=="K02000001","Births"].values[0])
uk_deaths  = int(mye3.loc[mye3["Code"]=="K02000001","Deaths"].values[0])
intl_net   = int(mye3.loc[mye3["Code"]=="K02000001","IntlMigNet"].values[0])

# ── Age Pyramid
uk_f_row = mye2f[mye2f["Code"]=="K02000001"].iloc[0]
uk_m_row = mye2m[mye2m["Code"]=="K02000001"].iloc[0]
age_bands = ["0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39",
             "40-44","45-49","50-54","55-59","60-64","65-69","70-74",
             "75-79","80-84","85-89","90+"]
female_pyramid, male_pyramid = [], []
for start in range(0, 90, 5):
    cols_ag = [str(i) for i in range(start, min(start+5,90))]
    female_pyramid.append(int(sum(uk_f_row[c] for c in cols_ag if pd.notna(uk_f_row[c]))))
    male_pyramid.append(int(sum(uk_m_row[c] for c in cols_ag if pd.notna(uk_m_row[c]))))
female_pyramid.append(int(uk_f_row["90plus"]) if pd.notna(uk_f_row["90plus"]) else 0)
male_pyramid.append(int(uk_m_row["90plus"]) if pd.notna(uk_m_row["90plus"]) else 0)

# ── Age groups from MYE1
mye1_age = mye1[mye1["Groups"].str.contains("to|\\+", na=False)][["Groups","UK"]].copy()
mye1_age["UK"] = pd.to_numeric(mye1_age["UK"], errors="coerce")
mye1_age = mye1_age.dropna()
age_labels = mye1_age["Groups"].tolist()
age_values = [int(v) for v in mye1_age["UK"].tolist()]

# ── UK Trend
years_trend = list(range(2011, 2025))
uk_trend_row = mye4[mye4["Code"]=="K02000001"].iloc[0]
pop_trend = [int(uk_trend_row[f"Mid{y}"]) for y in years_trend]

# ── Nations trend
nation_codes = {"England":"E92000001","Wales":"W92000004","Scotland":"S92000003","N. Ireland":"N92000002"}
nations_trend = {}
for name, code in nation_codes.items():
    row = mye4[mye4["Code"]==code].iloc[0]
    nations_trend[name] = [int(row[f"Mid{y}"]) for y in years_trend]

# ── Top 10 LAs
la_types = ["Unitary Authority","Metropolitan District","Non-metropolitan District",
            "London Borough","Council Area","Local Government District"]
la_df = mye2p[mye2p["Geography"].isin(la_types)].copy()
top10 = la_df.nlargest(10,"All_ages")[["Name","Geography","All_ages"]]
top10_names  = top10["Name"].tolist()
top10_values = [int(v) for v in top10["All_ages"].tolist()]

# ── Regions
region_df = mye2p[mye2p["Geography"]=="Region"].copy()
region_df = region_df.sort_values("All_ages", ascending=False)
region_names  = region_df["Name"].str.title().tolist()
region_values = [int(v) for v in region_df["All_ages"].tolist()]

# ── Countries
country_codes = {"England":"E92000001","Wales":"W92000004","Scotland":"S92000003","N. Ireland":"N92000002"}
country_names, country_values = [], []
for name, code in country_codes.items():
    country_names.append(name)
    country_values.append(int(mye2p.loc[mye2p["Code"]==code,"All_ages"].values[0]))

# ── Nations migration
nat_names_mig, nat_births, nat_deaths, nat_intl_net = [], [], [], []
for name, code in country_codes.items():
    row = mye3[mye3["Code"]==code]
    if len(row):
        nat_names_mig.append(name)
        nat_births.append(int(row["Births"].values[0]))
        nat_deaths.append(int(row["Deaths"].values[0]))
        nat_intl_net.append(int(row["IntlMigNet"].values[0]))

# ── Median age
uk_med = mye6[mye6["Code"]=="K02000001"].iloc[0]
med_trend = [float(uk_med[f"Med{y}"]) for y in years_trend]
mye6["Med2024"] = pd.to_numeric(mye6["Med2024"], errors="coerce")
la_med = mye6[mye6["Geography"].isin(la_types)].dropna(subset=["Med2024"])
oldest10   = la_med.nlargest(10,"Med2024")[["Name","Med2024"]]
youngest10 = la_med.nsmallest(10,"Med2024")[["Name","Med2024"]]
oldest_names   = oldest10["Name"].tolist()
oldest_ages    = [float(v) for v in oldest10["Med2024"].tolist()]
youngest_names = youngest10["Name"].tolist()
youngest_ages  = [float(v) for v in youngest10["Med2024"].tolist()]
reg_med = mye6[mye6["Geography"]=="Region"].sort_values("Med2024")
reg_med_names  = reg_med["Name"].str.title().tolist()
reg_med_values = [float(v) for v in reg_med["Med2024"].tolist()]

# ── Bundle
dashboard_data = {
    "kpi": {
        "total_pop":total_pop,"male_pop":male_pop,"female_pop":female_pop,
        "yoy_growth":yoy_growth,"median_age":median_age,
        "births":uk_births,"deaths":uk_deaths,"intl_net_mig":intl_net,
        "pop_2023":pop_2023,"pop_2011":pop_2011,
        "largest_la":"Birmingham",
        "largest_la_pop":int(la_df.loc[la_df["Name"]=="Birmingham","All_ages"].values[0])
    },
    "age_pyramid":{"bands":age_bands,"female":female_pyramid,"male":male_pyramid},
    "age_groups":{"labels":age_labels,"values":age_values},
    "uk_trend":{"years":years_trend,"values":pop_trend},
    "nations_trend":{"years":years_trend,"series":nations_trend},
    "top10_la":{"names":top10_names,"values":top10_values},
    "regions":{"names":region_names,"values":region_values},
    "countries":{"names":country_names,"values":country_values},
    "migration":{"nat_names":nat_names_mig,"births":nat_births,"deaths":nat_deaths,"intl_net":nat_intl_net},
    "median_age_trend":{"years":years_trend,"values":med_trend},
    "oldest_la":{"names":oldest_names,"values":oldest_ages},
    "youngest_la":{"names":youngest_names,"values":youngest_ages},
    "regions_median_age":{"names":reg_med_names,"values":reg_med_values}
}

JSON_DATA = json.dumps(dashboard_data, ensure_ascii=True).replace("</", "<\\/")

# ─────────────── HTML ───────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title> UK Population Dashboard · Mid-2024</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#f0f2f5;
  --surface:#f8f9fa;
  --card:#ffffff;
  --card-border:rgba(0,0,0,0.10);
  --glow-blue:#3b6bff;
  --glow-teal:#00e5c8;
  --glow-violet:#a855f7;
  --accent:#00e5c8;
  --accent2:#3b6bff;
  --accent3:#f472b6;
  --text:#1a1a2e;
  --muted:#6b7280;
  --dim:#9ca3af;
  --r:16px;
  --shadow:0 8px 40px rgba(0,0,0,.08);
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}

body{
  background:var(--bg);
  color:var(--text);
  font-family:'DM Sans',system-ui,sans-serif;
  font-size:14px;
  min-height:100vh;
  overflow-x:hidden;
}

/* ── AURORA BACKGROUND ── */
body::before{
  content:'';
  position:fixed;inset:0;
  background:transparent;
  pointer-events:none;
  z-index:0;
}
body::after{
  content:'';
  position:fixed;inset:0;
  background-image:none;
  pointer-events:none;
  z-index:0;
}

/* ── HEADER ── */
.hdr{
  background:rgba(255,255,255,0.90);
  backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(0,0,0,0.08);
  padding:16px 32px;
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:100;
}
.hdr-left{display:flex;align-items:center;gap:16px}
.flag{
  width:48px;height:30px;border-radius:6px;overflow:hidden;flex-shrink:0;
  background:
    linear-gradient(to right,
      transparent calc(50% - 2px), white calc(50% - 2px),
      white calc(50% + 2px), transparent calc(50% + 2px)),
    linear-gradient(to bottom,
      transparent calc(50% - 2px), white calc(50% - 2px),
      white calc(50% + 2px), transparent calc(50% + 2px)),
    #012169;
  position:relative;
  box-shadow:0 0 12px rgba(59,107,255,0.4);
}
.flag::after{
  content:'';position:absolute;inset:0;
  background:
    linear-gradient(to right,
      transparent calc(50% - 1.3px), #C8102E calc(50% - 1.3px),
      #C8102E calc(50% + 1.3px), transparent calc(50% + 1.3px)),
    linear-gradient(to bottom,
      transparent calc(50% - 1.3px), #C8102E calc(50% - 1.3px),
      #C8102E calc(50% + 1.3px), transparent calc(50% + 1.3px));
}
.hdr h1{
  font-family:'Syne',sans-serif;
  font-size:20px;font-weight:800;
  letter-spacing:-.5px;
  color:#1a1a2e;
}
.hdr p{font-size:11px;color:var(--muted);margin-top:2px}
.hdr-badge{
  background:rgba(59,107,255,0.07);
  border:1px solid rgba(59,107,255,0.25);
  color:var(--accent);
  padding:7px 16px;border-radius:24px;
  font-size:11px;font-weight:700;letter-spacing:.8px;
  white-space:nowrap;
  box-shadow:none;
}

/* ── LAYOUT ── */
.main{padding:24px 32px;max-width:1700px;margin:0 auto;position:relative;z-index:1}

.sec{
  font-family:'Syne',sans-serif;
  font-size:10px;font-weight:700;letter-spacing:2.5px;color:var(--accent);
  text-transform:uppercase;margin:32px 0 16px;
  display:flex;align-items:center;gap:12px;
}
.sec::after{content:'';flex:1;height:1px;background:linear-gradient(to right,rgba(59,107,255,0.2),transparent)}

/* ── FILTER BAR ── */
.filter-bar{
  background:var(--card);
  border:1px solid var(--card-border);
  border-radius:var(--r);
  padding:16px 20px;
  display:flex;flex-wrap:wrap;align-items:center;gap:12px;
  backdrop-filter:blur(12px);
  margin-bottom:20px;
  box-shadow:0 2px 12px rgba(0,0,0,0.06);
}
.filter-label{
  font-size:10px;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;color:var(--muted);
  white-space:nowrap;
}
.filter-chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{
  padding:6px 14px;border-radius:24px;
  font-size:11px;font-weight:600;cursor:pointer;
  border:1px solid rgba(0,0,0,0.10);
  background:#f3f4f6;
  color:var(--dim);
  transition:all .18s ease;
  user-select:none;
}
.chip:hover{border-color:rgba(59,107,255,0.4);color:var(--accent2);background:rgba(59,107,255,0.06)}
.chip.active{
  background:rgba(59,107,255,0.10);
  border-color:rgba(59,107,255,0.4);
  color:var(--accent);
  box-shadow:none;
}
.filter-divider{width:1px;height:28px;background:rgba(0,0,0,0.10);flex-shrink:0}

.filter-select{
  background:#f9fafb;
  border:1px solid rgba(0,0,0,0.10);
  color:var(--text);
  padding:6px 12px;border-radius:10px;
  font-size:12px;font-family:'DM Sans',sans-serif;
  cursor:pointer;
  transition:border-color .18s;
  outline:none;
}
.filter-select:hover{border-color:rgba(59,107,255,0.4)}

/* ── KPI ── */
.kpi-g{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px}
.kpi{
  background:var(--card);
  border:1px solid var(--card-border);
  border-radius:var(--r);
  padding:18px 20px;
  position:relative;overflow:hidden;
  transition:transform .18s,box-shadow .18s;
  cursor:default;
  backdrop-filter:blur(12px);
}
.kpi:hover{transform:translateY(-3px);box-shadow:0 12px 32px rgba(0,0,0,.10),0 0 0 1px rgba(59,107,255,0.15)}
.kpi::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--cc,var(--glow-blue)),transparent);
}
.kpi-glow{
  position:absolute;top:-30px;right:-20px;
  width:80px;height:80px;border-radius:50%;
  background:radial-gradient(circle,var(--cg,rgba(59,107,255,0.12)),transparent 70%);
  pointer-events:none;
}
.kpi-lbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1.2px}
.kpi-val{font-size:26px;font-weight:700;margin:8px 0 4px;line-height:1;color:var(--cv,#60a5fa);font-family:'Syne',sans-serif;}
.kpi-sub{font-size:11px;color:var(--dim)}

/* ── CHARTS ── */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.g3{display:grid;grid-template-columns:2fr 1fr;gap:14px}
.g3b{display:grid;grid-template-columns:1fr 2fr;gap:14px}
.cc{
  background:var(--card);
  border:1px solid var(--card-border);
  border-radius:var(--r);
  padding:20px 22px;
  transition:box-shadow .18s;
  backdrop-filter:blur(12px);
  position:relative;overflow:hidden;
}
.cc::before{
  content:'';position:absolute;inset:0;
  background:none;
  pointer-events:none;
}
.cc:hover{box-shadow:0 0 0 1px rgba(59,107,255,0.15),0 8px 24px rgba(0,0,0,.08)}
.ch{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px}
.ct{font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:var(--text)}
.cs{font-size:11px;color:var(--muted);margin-top:3px}
.ctag{
  font-size:10px;padding:4px 10px;border-radius:8px;
  background:rgba(59,107,255,0.08);
  color:#3b6bff;
  border:1px solid rgba(59,107,255,0.2);
  font-weight:700;letter-spacing:.5px;
  white-space:nowrap;
}

/* ── INSIGHTS ── */
.ins-g{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px}
.ins{
  background:var(--card);
  border:1px solid var(--card-border);
  border-left:2px solid var(--ic,var(--glow-blue));
  border-radius:10px;
  padding:14px 16px;
  backdrop-filter:blur(12px);
}
.ins-t{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1.2px}
.ins-v{font-size:22px;font-weight:700;margin-top:6px;color:var(--ic,var(--accent));font-family:'Syne',sans-serif;}
.ins-d{font-size:11px;color:var(--dim);margin-top:3px}

/* ── TABLE ── */
.tbl{width:100%;border-collapse:collapse;font-size:12px}
.tbl th{
  background:#f9fafb;
  color:var(--muted);text-transform:uppercase;
  font-size:10px;letter-spacing:1px;
  padding:10px 14px;text-align:left;
  border-bottom:1px solid rgba(0,0,0,0.08);
}
.tbl td{padding:10px 14px;border-bottom:1px solid rgba(0,0,0,0.05)}
.tbl tr:last-child td{border-bottom:none}
.tbl tr:hover td{background:rgba(59,107,255,0.04)}
.rb{
  display:inline-flex;align-items:center;justify-content:center;
  width:22px;height:22px;border-radius:50%;
  background:rgba(59,107,255,0.10);color:#3b6bff;font-weight:700;font-size:10px;
}
.rb.g{background:rgba(245,190,11,0.15);color:#f5be0b}
.rb.s{background:rgba(148,163,184,0.12);color:#6b7280}
.rb.b{background:rgba(180,100,9,0.12);color:#b46309}
.pbar-bg{background:rgba(59,107,255,0.10);border-radius:4px;height:4px;margin-top:4px}
.pbar-f{background:linear-gradient(90deg,var(--glow-blue),var(--accent));border-radius:4px;height:4px}

/* ── FOOTER ── */
.ft{
  text-align:center;padding:24px 32px;
  color:var(--muted);font-size:11px;
  border-top:1px solid rgba(0,0,0,0.08);
  margin-top:40px;position:relative;z-index:1;
}
.ft a{color:var(--accent);text-decoration:none}

/* ── FILTER HIDING ── */
.section-block{transition:opacity .25s,transform .25s}
.section-block.hidden{display:none}

@media(max-width:900px){
  .g2,.g3,.g3b{grid-template-columns:1fr}
  .ins-g{grid-template-columns:1fr}
  .kpi-g{grid-template-columns:repeat(2,1fr)}
  .main{padding:14px 16px}
}
@media(max-width:480px){
  .hdr{flex-direction:column;gap:10px;text-align:center}
  .kpi-g{grid-template-columns:1fr}
  .filter-bar{flex-direction:column;align-items:flex-start}
}
</style>
</head>
<body>

<header class="hdr">
  <div class="hdr-left">
    <div class="flag"></div>
    <div>
      <h1>UK Population Dashboard</h1>
      <p>Office for National Statistics · Mid-Year Population Estimates · Published September 2025</p>
    </div>
  </div>
  <div class="hdr-badge"> MID-2024 ESTIMATES</div>
</header>

<div class="main">

<!-- FILTER BAR -->
<div class="filter-bar">
  <span class="filter-label">View</span>
  <div class="filter-chips" id="sectionFilters">
    <span class="chip active" data-section="all">All Sections</span>
    <span class="chip" data-section="kpi">Overview</span>
    <span class="chip" data-section="trends">Trends</span>
    <span class="chip" data-section="age">Age &amp; Gender</span>
    <span class="chip" data-section="geo">Geography</span>
    <span class="chip" data-section="migration">Migration</span>
    <span class="chip" data-section="ageing">Ageing</span>
  </div>
  <div class="filter-divider"></div>
  <span class="filter-label">Trend Year</span>
  <select class="filter-select" id="yearFilter">
    <option value="all">All Years (2011–2024)</option>
    <option value="5">Last 5 Years</option>
    <option value="10">Last 10 Years</option>
  </select>
  <div class="filter-divider"></div>
  <span class="filter-label">Gender</span>
  <div class="filter-chips" id="genderFilters">
    <span class="chip active" data-gender="both">Both</span>
    <span class="chip" data-gender="male">Male</span>
    <span class="chip" data-gender="female">Female</span>
  </div>
</div>

<!-- KPIs -->
<div class="sec section-block" data-sections="all kpi"> Key Population Indicators</div>
<div class="kpi-g section-block" data-sections="all kpi">
  <div class="kpi" style="--cc:var(--glow-blue);--cg:rgba(59,107,255,0.15)">
    <div class="kpi-glow"></div>
    <div class="kpi-lbl">Total UK Population</div>
    <div class="kpi-val" id="v-total" style="--cv:#7eb8ff"></div>
    <div class="kpi-sub">Mid-2024 Estimate</div>
  </div>
  <div class="kpi" style="--cc:var(--glow-teal);--cg:rgba(0,229,200,0.12)" id="kpi-gender-pop">
    <div class="kpi-glow"></div>
    <div class="kpi-lbl" id="lbl-gender-pop">Male Population</div>
    <div class="kpi-val" id="v-gender-pop" style="--cv:#a78bfa"></div>
    <div class="kpi-sub" id="v-gender-p"></div>
  </div>
  <div class="kpi" style="--cc:#a855f7;--cg:rgba(168,85,247,0.12)" id="kpi-gender2" >
    <div class="kpi-glow"></div>
    <div class="kpi-lbl" id="lbl-gender2">Female Population</div>
    <div class="kpi-val" id="v-gender2" style="--cv:#f9a8d4"></div>
    <div class="kpi-sub" id="v-gender2-p"></div>
  </div>
  <div class="kpi" style="--cc:#10b981;--cg:rgba(16,185,129,0.12)">
    <div class="kpi-glow"></div>
    <div class="kpi-lbl">YoY Growth</div>
    <div class="kpi-val" id="v-growth" style="--cv:#34d399"></div>
    <div class="kpi-sub">vs Mid-2023</div>
  </div>
  <div class="kpi" style="--cc:#f59e0b;--cg:rgba(245,158,11,0.12)">
    <div class="kpi-glow"></div>
    <div class="kpi-lbl">Median Age (UK)</div>
    <div class="kpi-val" id="v-med" style="--cv:#fbbf24"></div>
    <div class="kpi-sub">UK average · Mid-2024</div>
  </div>
  <div class="kpi" style="--cc:var(--accent);--cg:rgba(0,229,200,0.12)">
    <div class="kpi-glow"></div>
    <div class="kpi-lbl">Largest Local Authority</div>
    <div class="kpi-val" id="v-la" style="--cv:#22d3ee;font-size:16px;margin-top:12px"></div>
    <div class="kpi-sub" id="v-la-p"></div>
  </div>
  <div class="kpi" style="--cc:#f43f5e;--cg:rgba(244,63,94,0.12)">
    <div class="kpi-glow"></div>
    <div class="kpi-lbl">Annual Births</div>
    <div class="kpi-val" id="v-births" style="--cv:#fb7185"></div>
    <div class="kpi-sub">Mid-2023 → Mid-2024</div>
  </div>
  <div class="kpi" style="--cc:#8b5cf6;--cg:rgba(139,92,246,0.12)">
    <div class="kpi-glow"></div>
    <div class="kpi-lbl">Net Int'l Migration</div>
    <div class="kpi-val" id="v-intl" style="--cv:#c4b5fd"></div>
    <div class="kpi-sub">Long-term net inflows</div>
  </div>
</div>

<div class="ins-g section-block" data-sections="all kpi">
  <div class="ins" style="--ic:#10b981">
    <div class="ins-t">Population Added Since 2011</div>
    <div class="ins-v" id="i-abs"></div>
    <div class="ins-d">13-year absolute growth (2011 → 2024)</div>
  </div>
  <div class="ins" style="--ic:#f59e0b">
    <div class="ins-t">England's Share of UK</div>
    <div class="ins-v" id="i-eng"></div>
    <div class="ins-d">Largest constituent country by population</div>
  </div>
  <div class="ins" style="--ic:#f43f5e">
    <div class="ins-t">Natural Change (Births – Deaths)</div>
    <div class="ins-v" id="i-nat"></div>
    <div class="ins-d">Migration drives most UK population growth</div>
  </div>
</div>

<!-- TREND + DONUT -->
<div class="sec section-block" data-sections="all trends"> Population Trends &amp; Structure</div>
<div class="g3 section-block" data-sections="all trends">
  <div class="cc">
    <div class="ch">
      <div><div class="ct">UK Population Growth · 2011–2024</div>
           <div class="cs">Annual mid-year estimates · ONS</div></div>
      <div class="ctag">TREND</div>
    </div>
    <canvas id="trendChart" height="200"></canvas>
  </div>
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Population by Country</div>
           <div class="cs">Four nations · Mid-2024</div></div>
      <div class="ctag">DONUT</div>
    </div>
    <canvas id="donutChart" height="200"></canvas>
  </div>
</div>

<!-- AGE PYRAMID -->
<div class="sec section-block" data-sections="all age"> Age &amp; Gender Structure</div>
<div class="g3 section-block" data-sections="all age">
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Population Age Pyramid · UK Mid-2024</div>
           <div class="cs" id="pyramid-sub">Males (left) vs Females (right) · 5-year age bands</div></div>
      <div class="ctag">PYRAMID</div>
    </div>
    <canvas id="pyramidChart" height="400"></canvas>
  </div>
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Age Group Distribution</div>
           <div class="cs">Broad 5-year bands · UK total</div></div>
      <div class="ctag">HBAR</div>
    </div>
    <canvas id="ageGroupChart" height="400"></canvas>
  </div>
</div>

<!-- TOP 10 + REGIONS -->
<div class="sec section-block" data-sections="all geo"> Geography &amp; Local Authorities</div>
<div class="g2 section-block" data-sections="all geo">
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Top 10 Most Populated Local Authorities</div>
           <div class="cs">Districts, boroughs &amp; unitary authorities · Mid-2024</div></div>
      <div class="ctag">TABLE</div>
    </div>
    <table class="tbl" id="top10Table"></table>
  </div>
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Population by English Region</div>
           <div class="cs">9 regions of England · Mid-2024</div></div>
      <div class="ctag">HBAR</div>
    </div>
    <canvas id="regionsChart" height="280"></canvas>
  </div>
</div>

<!-- NATIONS + MIGRATION -->
<div class="sec section-block" data-sections="all migration"> Nations &amp; Migration Analysis</div>
<div class="g2 section-block" data-sections="all migration">
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Population Growth by Nation · 2011–2024</div>
           <div class="cs">England, Wales, Scotland &amp; Northern Ireland</div></div>
      <div class="ctag">MULTI-LINE</div>
    </div>
    <canvas id="nationsChart" height="240"></canvas>
  </div>
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Components of Population Change · by Nation</div>
           <div class="cs">Births, Deaths &amp; Net International Migration · 2023–2024</div></div>
      <div class="ctag">GROUPED BAR</div>
    </div>
    <canvas id="migChart" height="240"></canvas>
  </div>
</div>

<!-- AGEING -->
<div class="sec section-block" data-sections="all ageing"> Ageing Population Analysis</div>
<div class="g3b section-block" data-sections="all ageing">
  <div class="cc">
    <div class="ch">
      <div><div class="ct">Oldest &amp; Youngest Local Authorities</div>
           <div class="cs">Median age by local authority · Mid-2024</div></div>
      <div class="ctag">BAR</div>
    </div>
    <canvas id="ageRankChart" height="300"></canvas>
  </div>
  <div class="cc">
    <div class="ch">
      <div><div class="ct">UK Median Age Trend · 2011–2024</div>
           <div class="cs">Steady rise signals population ageing</div></div>
      <div class="ctag">TREND</div>
    </div>
    <canvas id="medAgeChart" height="130"></canvas>
    <div style="margin-top:22px">
      <div class="ch">
        <div><div class="ct" style="font-size:12px">Median Age by English Region · Mid-2024</div></div>
      </div>
      <canvas id="regMedChart" height="130"></canvas>
    </div>
  </div>
</div>

</div><!-- /main -->

<footer class="ft">
  <p> UK Population Dashboard · Data: <a href="https://www.ons.gov.uk">Office for National Statistics</a>
  · Mid-Year Population Estimates, United Kingdom, June 2024 · Published September 2025</p>
  <p style="margin-top:5px">Generated with Python + pandas · Visualised with Chart.js</p>
</footer>

<script>
const D = __JSON_DATA__;

function fmt(n){return n>=1e6?(n/1e6).toFixed(2)+'M':n>=1e3?(n/1e3).toFixed(1)+'K':String(n)}
function fmtF(n){return n.toLocaleString('en-GB')}
function pct(a,b){return(a/b*100).toFixed(1)+'%'}

// ── KPIs
document.getElementById('v-total').textContent    = fmtF(D.kpi.total_pop);
document.getElementById('v-gender-pop').textContent = fmt(D.kpi.male_pop);
document.getElementById('v-gender-p').textContent = pct(D.kpi.male_pop,D.kpi.total_pop)+' of UK';
document.getElementById('v-gender2').textContent  = fmt(D.kpi.female_pop);
document.getElementById('v-gender2-p').textContent= pct(D.kpi.female_pop,D.kpi.total_pop)+' of UK';
document.getElementById('v-growth').innerHTML     = '+'+D.kpi.yoy_growth+'%';
document.getElementById('v-med').textContent      = D.kpi.median_age;
document.getElementById('v-la').textContent       = D.kpi.largest_la;
document.getElementById('v-la-p').textContent     = fmtF(D.kpi.largest_la_pop)+' residents';
document.getElementById('v-births').textContent   = fmt(D.kpi.births);
document.getElementById('v-intl').textContent     = '+'+fmt(D.kpi.intl_net_mig);
document.getElementById('i-abs').textContent      = '+'+fmtF(D.kpi.total_pop-D.kpi.pop_2011);
document.getElementById('i-eng').textContent      = pct(D.nations_trend.series['England'][13],D.kpi.total_pop);
document.getElementById('i-nat').textContent      = fmtF(D.kpi.births-D.kpi.deaths);

// Chart defaults
Chart.defaults.color='#6b7280';
Chart.defaults.borderColor='rgba(0,0,0,0.08)';
Chart.defaults.font.family="'DM Sans',system-ui,sans-serif";
const C={b:'#3b6bff',cy:'#00e5c8',p:'#a855f7',g:'#10b981',a:'#f59e0b',r:'#f43f5e',pk:'#f472b6',i:'#6366f1'};

// ── Charts state
let trendChart, pyramidChart;

function buildTrend(yearFilter){
  const allYears = D.uk_trend.years;
  const allVals  = D.uk_trend.values;
  let years = allYears, vals = allVals;
  if(yearFilter==='5')  { years=allYears.slice(-5); vals=allVals.slice(-5); }
  if(yearFilter==='10') { years=allYears.slice(-10); vals=allVals.slice(-10); }
  if(trendChart) trendChart.destroy();
  trendChart = new Chart('trendChart',{
    type:'line',
    data:{labels:years,datasets:[{
      label:'UK Population',data:vals,
      borderColor:C.cy,backgroundColor:'rgba(0,229,200,0.06)',
      fill:true,tension:.4,pointRadius:4,
      pointBackgroundColor:C.cy,pointBorderColor:'#ffffff',pointBorderWidth:2
    }]},
    options:{responsive:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' '+fmtF(c.parsed.y)}}},
      scales:{x:{grid:{color:'rgba(0,0,0,0.07)'}},y:{grid:{color:'rgba(0,0,0,0.07)'},ticks:{callback:v=>(v/1e6).toFixed(0)+'M'}}}}
  });
}

function buildPyramid(gender){
  const maleData   = gender==='female' ? new Array(D.age_pyramid.male.length).fill(0)
                   : D.age_pyramid.male.map(v=>-v);
  const femaleData = gender==='male'   ? new Array(D.age_pyramid.female.length).fill(0)
                   : D.age_pyramid.female;
  if(pyramidChart) pyramidChart.destroy();
  pyramidChart = new Chart('pyramidChart',{
    type:'bar',
    data:{labels:D.age_pyramid.bands,datasets:[
      {label:'Males',data:maleData,
       backgroundColor:'rgba(59,107,255,0.65)',borderColor:'rgba(59,107,255,0.9)',borderWidth:1},
      {label:'Females',data:femaleData,
       backgroundColor:'rgba(244,114,182,0.65)',borderColor:'rgba(244,114,182,0.9)',borderWidth:1}
    ]},
    options:{indexAxis:'y',responsive:true,
      plugins:{legend:{position:'top'},tooltip:{callbacks:{label:c=>' '+c.dataset.label+': '+fmtF(Math.abs(c.parsed.x))}}},
      scales:{x:{stacked:false,grid:{color:'rgba(0,0,0,0.07)'},ticks:{callback:v=>fmt(Math.abs(v))}},
              y:{stacked:false,grid:{display:false}}}}
  });
}

// ── Initial charts
buildTrend('all');

// Countries Donut
new Chart('donutChart',{
  type:'doughnut',
  data:{labels:D.countries.names,datasets:[{
    data:D.countries.values,
    backgroundColor:[C.b,C.g,C.p,C.a],
    borderColor:'rgba(255,255,255,0.9)',borderWidth:3
  }]},
  options:{responsive:true,cutout:'68%',plugins:{
    legend:{position:'bottom',labels:{padding:16,font:{size:11}}},
    tooltip:{callbacks:{label:c=>' '+c.label+': '+fmtF(c.parsed)+' ('+pct(c.parsed,D.kpi.total_pop)+')'}}
  }}
});

buildPyramid('both');

// Age Groups
new Chart('ageGroupChart',{
  type:'bar',
  data:{labels:D.age_groups.labels,datasets:[{
    label:'Population',data:D.age_groups.values,
    backgroundColor:D.age_groups.labels.map((_,i)=>{
      const t=i/D.age_groups.labels.length;
      const r=Math.round(0+t*244),g=Math.round(229-t*115),b=Math.round(200-t*56);
      return `rgba(${r},${g},${b},0.72)`;
    }),
    borderRadius:4
  }]},
  options:{indexAxis:'y',responsive:true,
    plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' '+fmtF(c.parsed.x)}}},
    scales:{x:{grid:{color:'rgba(0,0,0,0.07)'},ticks:{callback:v=>fmt(v)}},y:{grid:{display:false}}}}
});

// Top 10 Table
const tbl=document.getElementById('top10Table');
const mx=D.top10_la.values[0];
const medal=i=>i===0?'g':i===1?'s':i===2?'b':'';
tbl.innerHTML='<thead><tr><th>#</th><th>Local Authority</th><th style="text-align:right">Population</th></tr></thead>';
const tb=document.createElement('tbody');
D.top10_la.names.forEach((n,i)=>{
  tb.innerHTML+=`<tr>
    <td><span class="rb ${medal(i)}">${i+1}</span></td>
    <td><strong>${n}</strong><div class="pbar-bg"><div class="pbar-f" style="width:${Math.round(D.top10_la.values[i]/mx*100)}%"></div></div></td>
    <td style="text-align:right;color:#3b6bff;font-weight:700">${fmtF(D.top10_la.values[i])}</td>
  </tr>`;
});
tbl.appendChild(tb);

// Regions
new Chart('regionsChart',{
  type:'bar',
  data:{labels:D.regions.names,datasets:[{
    label:'Population',data:D.regions.values,
    backgroundColor:['rgba(59,107,255,0.7)','rgba(0,229,200,0.7)','rgba(168,85,247,0.7)',
      'rgba(16,185,129,0.7)','rgba(245,158,11,0.7)','rgba(244,63,94,0.7)',
      'rgba(99,102,241,0.7)','rgba(20,184,166,0.7)','rgba(249,115,22,0.7)'],
    borderRadius:4
  }]},
  options:{indexAxis:'y',responsive:true,
    plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' '+fmtF(c.parsed.x)}}},
    scales:{x:{grid:{color:'rgba(0,0,0,0.07)'},ticks:{callback:v=>fmt(v)}},y:{grid:{display:false},ticks:{font:{size:11}}}}}
});

// Nations multi-line
const nc={England:C.b,Wales:C.g,Scotland:C.p,'N. Ireland':C.a};
const nationsChartInst = new Chart('nationsChart',{
  type:'line',
  data:{labels:D.nations_trend.years,
    datasets:Object.entries(D.nations_trend.series).map(([name,vals])=>({
      label:name,data:vals,borderColor:nc[name]||C.cy,
      backgroundColor:'transparent',tension:.4,pointRadius:3,borderWidth:2
    }))},
  options:{responsive:true,
    plugins:{legend:{position:'top'},tooltip:{callbacks:{label:c=>' '+c.dataset.label+': '+fmtF(c.parsed.y)}}},
    scales:{x:{grid:{color:'rgba(0,0,0,0.07)'}},y:{grid:{color:'rgba(0,0,0,0.07)'},ticks:{callback:v=>fmt(v)}}}}
});

// Migration grouped bar
new Chart('migChart',{
  type:'bar',
  data:{labels:D.migration.nat_names,datasets:[
    {label:'Births',data:D.migration.births,backgroundColor:'rgba(16,185,129,0.72)',borderRadius:4},
    {label:'Deaths',data:D.migration.deaths,backgroundColor:'rgba(244,63,94,0.72)',borderRadius:4},
    {label:"Net Int'l Migration",data:D.migration.intl_net,backgroundColor:'rgba(0,229,200,0.72)',borderRadius:4}
  ]},
  options:{responsive:true,
    plugins:{legend:{position:'top'},tooltip:{callbacks:{label:c=>' '+c.dataset.label+': '+fmtF(c.parsed.y)}}},
    scales:{x:{grid:{color:'rgba(0,0,0,0.07)'}},y:{grid:{color:'rgba(0,0,0,0.07)'},ticks:{callback:v=>fmtF(v)}}}}
});

// Age rank
new Chart('ageRankChart',{
  type:'bar',
  data:{labels:[...D.oldest_la.names,...D.youngest_la.names],datasets:[
    {label:'Oldest LAs',data:[...D.oldest_la.values,...new Array(10).fill(null)],
     backgroundColor:'rgba(245,158,11,0.72)',borderRadius:3},
    {label:'Youngest LAs',data:[...new Array(10).fill(null),...D.youngest_la.values],
     backgroundColor:'rgba(99,102,241,0.72)',borderRadius:3}
  ]},
  options:{indexAxis:'y',responsive:true,
    plugins:{legend:{position:'top'}},
    scales:{x:{min:25,grid:{color:'rgba(0,0,0,0.07)'}},y:{grid:{display:false},ticks:{font:{size:10}}}}}
});

// Median age trend
new Chart('medAgeChart',{
  type:'line',
  data:{labels:D.median_age_trend.years,datasets:[{
    label:'UK Median Age',data:D.median_age_trend.values,
    borderColor:C.a,backgroundColor:'rgba(245,158,11,0.06)',
    fill:true,tension:.4,pointRadius:4,
    pointBackgroundColor:C.a,pointBorderColor:'#ffffff',pointBorderWidth:2
  }]},
  options:{responsive:true,
    plugins:{legend:{position:'top'}},
    scales:{x:{grid:{color:'rgba(0,0,0,0.07)'}},y:{min:39,max:42,grid:{color:'rgba(0,0,0,0.07)'}}}}
});

// Regions median age
new Chart('regMedChart',{
  type:'bar',
  data:{labels:D.regions_median_age.names,datasets:[{
    label:'Median Age',data:D.regions_median_age.values,
    backgroundColor:D.regions_median_age.values.map(v=>
      v<38?'rgba(99,102,241,0.72)':v<42?'rgba(0,229,200,0.72)':'rgba(245,158,11,0.72)'),
    borderRadius:3
  }]},
  options:{indexAxis:'y',responsive:true,
    plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>' Median age: '+c.parsed.x}}},
    scales:{x:{min:34,grid:{color:'rgba(0,0,0,0.07)'}},y:{grid:{display:false},ticks:{font:{size:10}}}}}
});

// ── FILTER LOGIC ──
let activeSection = 'all';
let activeGender  = 'both';
let activeYear    = 'all';

function applySectionFilter(section){
  activeSection = section;
  document.querySelectorAll('.section-block').forEach(el=>{
    const secs = el.dataset.sections ? el.dataset.sections.split(' ') : ['all'];
    el.classList.toggle('hidden', !secs.includes(section));
  });
}

document.querySelectorAll('#sectionFilters .chip').forEach(chip=>{
  chip.addEventListener('click',()=>{
    document.querySelectorAll('#sectionFilters .chip').forEach(c=>c.classList.remove('active'));
    chip.classList.add('active');
    applySectionFilter(chip.dataset.section);
  });
});

document.getElementById('yearFilter').addEventListener('change', e=>{
  activeYear = e.target.value;
  buildTrend(activeYear);

  // Also update nations chart year range
  const allYears = D.nations_trend.years;
  let yrs = allYears;
  if(activeYear==='5')  yrs=allYears.slice(-5);
  if(activeYear==='10') yrs=allYears.slice(-10);
  nationsChartInst.data.labels = yrs;
  Object.entries(D.nations_trend.series).forEach(([name,vals],i)=>{
    let sliced = vals;
    if(activeYear==='5')  sliced=vals.slice(-5);
    if(activeYear==='10') sliced=vals.slice(-10);
    nationsChartInst.data.datasets[i].data = sliced;
  });
  nationsChartInst.update();
});

document.querySelectorAll('#genderFilters .chip').forEach(chip=>{
  chip.addEventListener('click',()=>{
    document.querySelectorAll('#genderFilters .chip').forEach(c=>c.classList.remove('active'));
    chip.classList.add('active');
    activeGender = chip.dataset.gender;
    buildPyramid(activeGender);

    // Update KPI cards
    if(activeGender==='male'){
      document.getElementById('lbl-gender-pop').textContent='Male Population';
      document.getElementById('v-gender-pop').textContent=fmt(D.kpi.male_pop);
      document.getElementById('v-gender-p').textContent=pct(D.kpi.male_pop,D.kpi.total_pop)+' of UK';
      document.getElementById('kpi-gender2').style.opacity='0.35';
      document.getElementById('pyramid-sub').textContent='Showing males only';
    } else if(activeGender==='female'){
      document.getElementById('lbl-gender-pop').textContent='Female Population';
      document.getElementById('v-gender-pop').textContent=fmt(D.kpi.female_pop);
      document.getElementById('v-gender-p').textContent=pct(D.kpi.female_pop,D.kpi.total_pop)+' of UK';
      document.getElementById('kpi-gender2').style.opacity='0.35';
      document.getElementById('pyramid-sub').textContent='Showing females only';
    } else {
      document.getElementById('lbl-gender-pop').textContent='Male Population';
      document.getElementById('v-gender-pop').textContent=fmt(D.kpi.male_pop);
      document.getElementById('v-gender-p').textContent=pct(D.kpi.male_pop,D.kpi.total_pop)+' of UK';
      document.getElementById('kpi-gender2').style.opacity='1';
      document.getElementById('pyramid-sub').textContent='Males (left) vs Females (right) · 5-year age bands';
    }
  });
});
</script>
</body>
</html>"""

HTML = HTML.replace('__JSON_DATA__', JSON_DATA)

output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uk_population_dashboard.html")
with open(output, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = os.path.getsize(output)/1024
print(f"\n[OK] Dashboard saved -> {output}")
print(f"   File size: {size_kb:.1f} KB")
print(f"\n[DATA] KEY FINDINGS:")
print(f"   Total UK Population (Mid-2024) : {total_pop:>14,}")
print(f"   Males                          : {male_pop:>14,}  ({male_pop/total_pop*100:.1f}%)")
print(f"   Females                        : {female_pop:>14,}  ({female_pop/total_pop*100:.1f}%)")
print(f"   YoY Growth                     : +{yoy_growth:>13}%  (+{total_pop-pop_2023:,})")
print(f"   Growth since 2011              : +{total_pop-pop_2011:>14,}")
print(f"   UK Median Age                  : {median_age:>14}")
print(f"   Annual Births                  : {uk_births:>14,}")
print(f"   Annual Deaths                  : {uk_deaths:>14,}")
print(f"   Net Int'l Migration            : +{intl_net:>13,}")
print(f"\n[MAP] NATIONS (Mid-2024):")
for name, code in nation_codes.items():
    v = int(mye2p.loc[mye2p['Code']==code,'All_ages'].values[0])
    print(f"   {name:<15}: {v:>12,}  ({v/total_pop*100:.1f}%)")
