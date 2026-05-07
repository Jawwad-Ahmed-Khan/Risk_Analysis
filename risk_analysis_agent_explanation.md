# Risk Analysis Agent — Final Complete Design

## SECTION 1: COMPLETE CONTEXT UNDERSTANDING

Before designing the agent, let me map exactly what data exists and what gaps must be filled by web search:

```
┌──────────────────────────────────────────────────────────────────┐
│              DATA AVAILABILITY MATRIX                            │
├─────────────────────────────┬────────────────┬───────────────────┤
│  DATA NEEDED                │  IN DATABASE   │  SOURCE           │
├─────────────────────────────┼────────────────┼───────────────────┤
│  Population count           │  ✅ YES        │  pakistan_locations│
│  Population density         │  ✅ YES        │  pakistan_locations│
│  Flood risk zone            │  ✅ YES        │  pakistan_locations│
│  Seismic zone               │  ✅ YES        │  pakistan_locations│
│  Heat risk zone             │  ✅ YES        │  pakistan_locations│
│  Infrastructure quality     │  ✅ YES        │  pakistan_locations│
│  Drainage quality           │  ✅ YES        │  pakistan_locations│
│  Building stock type        │  ✅ YES        │  pakistan_locations│
│  Elevation                  │  ✅ YES        │  pakistan_locations│
│  Hospitals count            │  ✅ YES        │  pakistan_infra    │
│  Schools count              │  ✅ YES        │  pakistan_infra    │
│  Bridges count              │  ✅ YES        │  pakistan_infra    │
│  Dams and barrages          │  ✅ YES        │  pakistan_infra    │
│  Evacuation centers         │  ✅ YES        │  pakistan_infra    │
│  Current weather            │  ✅ YES        │  weather_hourly    │
│  5-day forecast             │  ✅ YES        │  weather_daily     │
│  Earthquake data            │  ✅ YES        │  seismic_events    │
│  River gauge current        │  ✅ YES        │  flood_gauge_curr  │
│  River gauge forecast       │  ✅ YES        │  flood_gauge_fore  │
├─────────────────────────────┼────────────────┼───────────────────┤
│  TERRAIN TYPE               │  ❌ NO         │  Web Search Needed │
│  (mountain/plain/desert/    │                │                   │
│   urban/coastal/riverine)   │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  ROAD NETWORK QUALITY       │  ❌ NO         │  Web Search Needed │
│  (paved/unpaved/single      │                │                   │
│   track/seasonal)           │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  POVERTY LEVEL              │  ❌ NO         │  Web Search Needed │
│  (affects recovery speed    │                │                   │
│   and self-resilience)      │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  HISTORICAL DISASTER        │  ❌ NO         │  Web Search Needed │
│  FREQUENCY IN THIS AREA     │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  CURRENT NGO PRESENCE       │  ❌ NO         │  Web Search Needed │
│  ON GROUND                  │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  SEASONAL CONTEXT           │  ❌ NO         │  Web Search Needed │
│  (harvest season, Ramadan,  │                │                   │
│   school exam period)       │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  CURRENT MEDIA REPORTS      │  ❌ NO         │  Web Search Needed │
│  FROM GROUND                │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  SOIL TYPE AND              │  ❌ NO         │  Web Search Needed │
│  SATURATION LEVEL           │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  UPSTREAM DAM STATUS        │  ❌ NO         │  Web Search Needed │
│  (is Tarbela releasing?)    │                │                   │
├─────────────────────────────┼────────────────┼───────────────────┤
│  LANDSLIDE HISTORY          │  ❌ NO         │  Web Search Needed │
│  IN MOUNTAIN AREAS          │                │                   │
└─────────────────────────────┴────────────────┴───────────────────┘
```

---

## SECTION 2: TERRAIN CLASSIFICATION SYSTEM

The database stores elevation but not terrain type. The agent must determine terrain intelligently:

```
┌──────────────────────────────────────────────────────────────────┐
│              TERRAIN DETERMINATION LOGIC                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FROM DATABASE (elevation_m + province + flood_risk_zone):       │
│                                                                  │
│  elevation_m > 2000m + KPK/GB/AJK → MOUNTAIN                   │
│  elevation_m 500-2000m + KPK/Balochistan → HIGHLAND             │
│  elevation_m < 500m + Punjab/Sindh + flood_zone_4/5 → RIVERINE  │
│  elevation_m < 100m + Sindh + coastal → COASTAL_FLOODPLAIN      │
│  elevation_m < 500m + Balochistan interior → DESERT             │
│  population_density > 5000/km² + any → URBAN                    │
│  population_density 1000-5000 + flat → AGRICULTURAL_PLAIN       │
│                                                                  │
│  IF TERRAIN CANNOT BE DETERMINED FROM DB:                        │
│  → web_search: "[location_name] Pakistan terrain geography type" │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Why Terrain Changes Everything:

```
MOUNTAIN TERRAIN + FLOOD:
  → Landslide risk activated
  → Road closures likely (single track mountain roads)
  → Helicopter may be only access
  → Flash floods move faster and carry boulders
  → Bridges extremely vulnerable
  → Risk multiplier: ×1.8

RIVERINE PLAIN + FLOOD (Sindh/Punjab):
  → Slow onset but massive area inundated
  → Days to weeks of standing water
  → Crop destruction guaranteed
  → Displacement prolonged (weeks not days)
  → Risk multiplier: ×1.4

URBAN + ANY DISASTER:
  → Higher infrastructure concentration
  → Better hospitals but overwhelmed quickly
  → Media visibility increases response
  → Dense population = mass casualty risk
  → Risk multiplier: ×1.5

DESERT + HEATWAVE (Balochistan interior):
  → Pre-existing heat stress on population
  → Water scarcity compounds heat risk
  → Sparse population = under-reporting
  → Risk multiplier: ×1.6

COASTAL + CYCLONE:
  → Storm surge adds to wind damage
  → Saline water damages agriculture for years
  → Evacuation routes limited
  → Risk multiplier: ×1.7
```

---

## SECTION 3: COMPLETE FACTOR FRAMEWORK

Every factor the agent must assess:

```
┌──────────────────────────────────────────────────────────────────┐
│              COMPLETE RISK FACTOR FRAMEWORK                      │
├────────────────────────────────────────────────────────────────  │
│                                                                  │
│  CATEGORY A: PHYSICAL HAZARD FACTORS                             │
│  ─────────────────────────────────────                           │
│  A1. Disaster magnitude/intensity                                │
│  A2. Disaster area of impact (radius/extent)                     │
│  A3. Duration (is it ongoing? forecast duration?)                │
│  A4. Onset speed (sudden vs slow onset)                          │
│  A5. Secondary hazard potential                                  │
│      Earthquake → landslide, fire, dam failure                   │
│      Flood → disease outbreak, crop failure, displacement        │
│      Heatwave → electricity grid failure, water shortage         │
│                                                                  │
│  CATEGORY B: POPULATION FACTORS                                  │
│  ─────────────────────────────────                               │
│  B1. Total population in impact zone                             │
│  B2. Population density distribution                             │
│  B3. Vulnerable population groups:                               │
│      • Children under 5 (require special evacuation)            │
│      • Elderly (slower evacuation, medical needs)               │
│      • Women (especially pregnant — in Pakistan context)        │
│      • Persons with disability                                   │
│      • Livestock-dependent communities (asset loss)             │
│  B4. Poverty level (affects self-recovery capacity)              │
│  B5. Literacy level (affects alert message comprehension)        │
│  B6. Seasonal population variation                               │
│      (harvest workers, pilgrims, seasonal migrants)              │
│                                                                  │
│  CATEGORY C: SETTLEMENT AND HOUSING FACTORS                      │
│  ─────────────────────────────────────────────                   │
│  C1. Building stock type:                                        │
│      KUTCHA (mud/unbaked brick):                                 │
│        → Collapses at M5.0+                                     │
│        → Dissolves in 48h of flooding                           │
│        → Provides no heat protection above 45°C                 │
│        → Vulnerability score: 95/100                            │
│      SEMI-PUCCA (partial brick):                                 │
│        → Survives M5.5 with damage                              │
│        → Survives 72h of flooding                               │
│        → Vulnerability score: 65/100                            │
│      PUCCA (brick/reinforced concrete):                          │
│        → Survives M6.0 if built to code                         │
│        → Survives extended flooding                             │
│        → Vulnerability score: 30/100                            │
│      MIXED:                                                      │
│        → Use weighted average based on rural/urban split        │
│  C2. Settlement density (urban core vs peri-urban vs rural)      │
│  C3. Informal settlements presence                               │
│      (katchi abadis in Karachi, kachi in interior Sindh)        │
│  C4. Housing elevation above flood level                         │
│                                                                  │
│  CATEGORY D: INFRASTRUCTURE FACTORS                              │
│  ─────────────────────────────────                               │
│  D1. Road network:                                               │
│      National Highway → always open unless extreme event        │
│      Provincial Road → closes in heavy rain                     │
│      District Road → closes in moderate flooding                │
│      Village track → closes in any significant rain             │
│  D2. Bridge vulnerability                                        │
│      (old bridges in KPK flood in M6+ or heavy rain)            │
│  D3. Healthcare infrastructure:                                  │
│      Hospital beds per 1,000 population                         │
│      Pakistan national average: 0.6 beds/1000                   │
│      Rural areas: 0.1-0.2 beds/1000                             │
│  D4. Water and sanitation:                                       │
│      Piped water access percentage                              │
│      Sanitation coverage percentage                             │
│      (flooding contaminates water → disease outbreak)           │
│  D5. Electricity infrastructure:                                 │
│      Grid reliability affects hospitals, pumping stations       │
│  D6. Telecommunications:                                         │
│      Mobile coverage (affects alert dissemination)              │
│      Internet access (affects coordination)                     │
│                                                                  │
│  CATEGORY E: TERRAIN AND GEOGRAPHY FACTORS                       │
│  ──────────────────────────────────────────                      │
│  E1. Terrain type (mountain/highland/plain/desert/coastal)       │
│  E2. Slope gradient (steep = landslide risk with rain/quake)     │
│  E3. River proximity and upstream catchment size                 │
│  E4. Soil type:                                                  │
│      Clay soil → waterlogged quickly, slow drainage             │
│      Sandy soil → flash flood drainage but erosion              │
│      Rocky → runoff fast → flash floods downstream              │
│  E5. Vegetation cover:                                           │
│      Deforested → increased landslide and flood risk            │
│      Irrigated agriculture → soil already saturated             │
│  E6. Distance to nearest major city                              │
│      (affects response time for external aid)                   │
│                                                                  │
│  CATEGORY F: SEASONAL AND TEMPORAL FACTORS                       │
│  ─────────────────────────────────────────                       │
│  F1. Current season and its implications:                        │
│      Monsoon (Jul-Sep): maximum flood risk, high displacement   │
│      Pre-monsoon (Apr-Jun): heat wave peak, crop stress         │
│      Winter (Dec-Feb): cold wave, snow, mountain access lost    │
│      Harvest (Oct-Nov): crop loss compounds economic damage     │
│  F2. Time of day of disaster:                                    │
│      Night earthquake → people in buildings → higher casualties │
│      Night flood → people asleep → slower evacuation           │
│  F3. Ramadan context:                                            │
│      Daytime fasting population → heat stress amplified         │
│      Community kitchens → mobilization point for relief         │
│  F4. School calendar:                                            │
│      Schools open → children concentrated, evacuation complex   │
│      Schools closed → buildings available as shelters           │
│                                                                  │
│  CATEGORY G: RESPONSE CAPACITY FACTORS                           │
│  ─────────────────────────────────────                           │
│  G1. Evacuation route availability and capacity                  │
│  G2. Nearest operational hospital distance                       │
│  G3. Evacuation center capacity vs population                    │
│  G4. NGO presence in district (from web search)                  │
│  G5. Government response history in this district                │
│  G6. Community disaster preparedness level                       │
│  G7. Communications infrastructure for alert dissemination       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## SECTION 4: WEB SEARCH STRATEGY — EXACT QUERIES

The agent must execute specific, targeted web searches. Not generic searches:

```
┌──────────────────────────────────────────────────────────────────┐
│              MANDATORY WEB SEARCH QUERIES BY DISASTER TYPE       │
└──────────────────────────────────────────────────────────────────┘

FOR ALL DISASTER TYPES (always run these 4):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SEARCH 1: TERRAIN AND GEOGRAPHY
  Query: "[district_name] [province] Pakistan terrain geography 
          elevation landscape type"
  Extract: Mountain/plain/desert/coastal, slope type,
           river proximity, soil type

  SEARCH 2: POVERTY AND DEMOGRAPHICS
  Query: "[district_name] Pakistan poverty rate population 
          census 2023 literacy rate"
  Extract: Poverty percentage, literacy rate, 
           vulnerable population estimates

  SEARCH 3: HISTORICAL DISASTER RECORD
  Query: "[district_name] Pakistan flood earthquake disaster 
          history damage casualties site:ndma.gov.pk OR 
          site:pdma.gop.pk OR site:reliefweb.int"
  Extract: Past disaster frequency, historical casualties,
           typical damage patterns, known vulnerable areas

  SEARCH 4: CURRENT SITUATION NEWS
  Query: "[district_name] Pakistan [disaster_kind] 2025 
          damage casualties displaced"
  Extract: Ground reality reports, actual casualties reported,
           areas already affected, roads closed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOR FLOOD DISASTERS (run these additional 4):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SEARCH 5: UPSTREAM DAM STATUS
  Query: "Tarbela Mangla Warsak dam release [current month] 
          2025 WAPDA flood discharge"
  Extract: Current release rates, dam levels,
           whether controlled releases are happening

  SEARCH 6: RIVER SYSTEM CURRENT STATUS
  Query: "[river_name] Pakistan flood situation July 2025 
          barrage discharge level"
  Extract: Upstream conditions, total discharge volume,
           expected peak arrival time

  SEARCH 7: DRAINAGE AND SOIL SATURATION
  Query: "[district_name] Sindh Punjab drainage system 
          waterlogging soil saturation 2025 monsoon"
  Extract: Current soil saturation state,
           drainage system capacity and current state

  SEARCH 8: CROP AND AGRICULTURE IMPACT
  Query: "[district_name] Pakistan agriculture crops 
          [current month] harvest calendar"
  Extract: What crops are currently in fields,
           economic value at risk from flooding

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOR EARTHQUAKE DISASTERS (run these additional 4):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SEARCH 5: FAULT LINE PROXIMITY
  Query: "[district_name] Pakistan seismic fault line 
          Chaman Makran Himalayan active fault"
  Extract: Which fault caused this, historical rupture
           pattern, aftershock probability

  SEARCH 6: BUILDING CODE COMPLIANCE
  Query: "[district_name] Pakistan building construction 
          quality seismic resistance kutcha housing percentage"
  Extract: Estimated percentage of buildings that are
           kutcha, semi-pucca, pucca

  SEARCH 7: AFTERSHOCK PATTERN
  Query: "aftershock probability [magnitude] earthquake 
          Pakistan [fault_name]"
  Extract: Expected aftershock frequency and magnitude,
           duration of aftershock sequence

  SEARCH 8: MOUNTAIN/LANDSLIDE RISK
  Query: "[district_name] Pakistan landslide risk 
          earthquake triggered rockfall history"
  Extract: Known landslide zones, road closure history
           after earthquakes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOR HEATWAVE DISASTERS (run these additional 4):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SEARCH 5: WATER AVAILABILITY
  Query: "[district_name] Pakistan water supply drinking 
          water access percentage piped water 2024"
  Extract: Water access percentage, water source type,
           risk of water shortage during heat emergency

  SEARCH 6: ELECTRICITY GRID RELIABILITY
  Query: "[district_name] Pakistan electricity load 
          shedding power outage hours summer 2025"
  Extract: Daily load shedding hours, grid reliability,
           impact on hospitals and water pumps

  SEARCH 7: HISTORICAL HEAT CASUALTIES
  Query: "[province] Pakistan heatwave deaths casualties 
          hospital admissions history Karachi 2015"
  Extract: Historical death toll context, 
           which groups were most affected

  SEARCH 8: OUTDOOR WORKER POPULATION
  Query: "[district_name] Pakistan outdoor workers 
          agriculture labor construction workforce"
  Extract: Estimated outdoor workforce size,
           peak outdoor working hours context

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONDITIONAL SEARCHES (run when data gap detected):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  IF hospital count from DB is 0 or seems low:
  Query: "[district_name] Pakistan hospital DHQ THQ 
          RHC health facility list"
  
  IF road information missing:
  Query: "[district_name] Pakistan road network 
          national highway provincial road condition"
  
  IF population seems outdated:
  Query: "[district_name] Pakistan population 
          census 2023 PBS official"
  
  IF NGO context needed:
  Query: "Pakistan NGO [district_name] Alkhidmat 
          Edhi Red Crescent active operations 2025"
```

---

## SECTION 5: COMPLETE SCORING METHODOLOGY

### 5.1 Hazard Severity Score (Weight: 25%)

```
EARTHQUAKE:
  Base Score from magnitude:
    M < 4.0  → 10    M 4.0-4.9 → 25
    M 5.0-5.9 → 50   M 6.0-6.9 → 75
    M 7.0-7.9 → 90   M 8.0+    → 100
  
  Modifiers:
    depth_class = shallow (<70km)     → +20
    depth_class = intermediate        → +8
    azimuthal_gap > 180°              → -5 (less reliable location)
    data_quality = automatic          → note uncertainty
    data_quality = reviewed           → confirmed, no penalty
    magnitude_was_revised UP          → +10
    magnitude_was_revised DOWN        → -5
    tsunami_flag = TRUE               → +25 (coastal areas)
    usgs_alert_level = red            → override to minimum 90
    usgs_alert_level = orange         → override to minimum 70
    significance > 800                → +10
    felt_reports > 1000               → +5 (widespread impact)
    
  Secondary hazard modifiers:
    terrain = mountain + M5.5+        → +15 (landslide trigger)
    near major dam (within 50km)      → +20 (dam failure risk)

FLOOD:
  Base Score from pct_of_danger:
    < 50%   → 10    50-70%   → 25
    70-85%  → 45    85-100%  → 65
    100-120% → 80   > 120%   → 95
  
  Modifiers:
    river_trend = rapidly_rising      → +20
    river_trend = rising              → +10
    river_trend = stable              → +0
    river_trend = falling             → -10
    hours_to_danger < 6               → +15
    hours_to_danger 6-12              → +8
    forecast_72h prob_exceeds_danger > 70% → +15
    forecast_72h prob_exceeds_danger 40-70% → +8
    upstream_area_sqkm > 200,000      → +12
    upstream_area_sqkm > 100,000      → +8
    pct_of_historical_max > 90%       → +15
    is_forecast_breach = TRUE         → note advance warning time
    
  Secondary hazard modifiers:
    terrain = mountain                → +15 (flash flood speed)
    soil saturation known high        → +10
    multiple rivers converging        → +15

HEATWAVE:
  Base Score from temp_max_c:
    < 40°C   → 5     40-43°C  → 25
    44-46°C  → 50    47-49°C  → 70
    50-52°C  → 85    > 52°C   → 100
  
  Modifiers:
    temp_apparent_c > temp_max_c + 3  → +10 (high humidity compounds)
    temp_dewpoint_c > 26°C            → +15 (medically dangerous)
    duration_days > 3                 → +15
    duration_days > 7                 → +25
    night_temp_min > 30°C             → +10 (no recovery period)
    humidity_pct > 70%                → +12
    province = sindh + July/August    → +5 (expected but still deadly)
    electricity_outage_hours > 12     → +15 (no fans/AC for poor)
    water_shortage_known              → +20

HEAVY RAIN / FLASH FLOOD:
  Base Score from precip_24h_mm:
    < 25mm   → 10    25-50mm  → 25
    50-100mm → 45    100-150mm → 65
    150-200mm → 80   > 200mm   → 95
  
  Modifiers:
    cape_jkg > 3500                   → +15
    cape_jkg > 2500                   → +8
    precip_72h_mm > 300               → +12
    terrain = mountain                → +20 (flash flood + landslide)
    terrain = urban                   → +15 (drainage overwhelmed)
    drainage_quality = very_high      → +15 (very poor drainage)
    precip_prob_pct > 80              → +5 (high confidence)
    soil already saturated            → +15

COLD WAVE:
  Base Score from temp_min_c (below direction):
    -5 to 0°C    → 20    -10 to -5°C → 45
    -15 to -10°C → 70    < -15°C     → 90
  
  Modifiers:
    terrain = mountain                → +15
    province = gilgit_baltistan       → +10
    wind_speed_kmh > 40               → +10 (wind chill)
    snowfall_cm > 50                  → +15 (road blockage)
    population has high elderly pct   → +10
```

### 5.2 Exposure Score (Weight: 25%)

```
POPULATION EXPOSURE:
  Raw population in district:
    < 50,000          → 10
    50,000-100,000    → 25
    100,000-300,000   → 40
    300,000-600,000   → 60
    600,000-1,000,000 → 75
    1,000,000-3,000,000 → 88
    > 3,000,000       → 100
  
  Density modifier:
    density > 10,000/km² → +15 (extremely dense, Karachi)
    density 5,000-10,000 → +10
    density 1,000-5,000  → +5
    density < 500        → -5

INFRASTRUCTURE EXPOSURE:
  
  Hospital exposure score:
    0 hospitals in zone   → 100 (no capacity = maximum vulnerability)
    1-2 hospitals         → 70
    3-5 hospitals         → 45
    6-10 hospitals        → 25
    > 10 hospitals        → 10
  
  Critical asset exposure:
    Per is_critical=TRUE asset in zone:
      dam or barrage      → +25 per asset
      hospital            → +15 per asset
      bridge              → +10 per asset
      power station       → +10 per asset
      school > 1000 students → +8 per asset

EXPOSED POPULATION CALCULATION:
  For earthquake:
    Impact radius = 10km per magnitude unit above 4.0
    M5.0 → 10km radius
    M6.0 → 20km radius
    M7.0 → 30km radius
    Population within radius = primary exposed population
  
  For flood:
    Use district population × flood_risk_zone factor:
      zone_5_critical → 80% of district population
      zone_4_very_high → 60%
      zone_3_high → 40%
      zone_2_moderate → 20%
  
  For heatwave:
    Entire district population exposed
    Vulnerable groups (outdoor workers, elderly, poor)
    estimated as 35% of total for Pakistan context
  
  EXPOSURE SCORE = (Population_score × 0.55) + 
                   (Infrastructure_score × 0.45)
```

### 5.3 Vulnerability Score (Weight: 20%)

```
BUILDING VULNERABILITY:
  kutcha      → 95/100
  semi_pucca  → 60/100
  pucca       → 25/100
  mixed       → calculated as:
    (kutcha_pct × 95 + semi_pct × 60 + pucca_pct × 25) / 100
    If proportions unknown: 50/100 default with uncertainty flag

DRAINAGE VULNERABILITY:
  very_low    → 10/100 (excellent drainage, rare in Pakistan)
  low         → 25/100
  moderate    → 45/100
  high        → 65/100
  very_high   → 85/100
  critical    → 100/100

INFRASTRUCTURE QUALITY VULNERABILITY:
  very_low    → 10/100
  low         → 25/100
  moderate    → 45/100
  high        → 65/100
  very_high   → 85/100
  critical    → 100/100

POVERTY VULNERABILITY (from web search):
  Poverty rate < 20%   → 20/100
  Poverty rate 20-35%  → 40/100
  Poverty rate 35-50%  → 60/100
  Poverty rate > 50%   → 80/100
  Not found            → 50/100 with uncertainty flag

TERRAIN VULNERABILITY:
  mountain    → 80/100 (access difficulty compounds everything)
  highland    → 60/100
  urban       → 45/100 (good services but density risk)
  plain       → 35/100
  riverine    → 70/100 (flood plain inherently vulnerable)
  desert      → 65/100 (resource scarcity)
  coastal     → 75/100 (multiple hazard exposure)

VULNERABILITY SCORE = 
  (Building × 0.30) +
  (Drainage × 0.20) +
  (Infrastructure_quality × 0.20) +
  (Poverty × 0.20) +
  (Terrain × 0.10)
```

### 5.4 Escalation Risk Score (Weight: 15%)

```
CURRENT TRAJECTORY:
  Is situation getting worse?
  
  Flood escalation indicators:
    river_trend = rapidly_rising    → 90
    river_trend = rising            → 65
    river_trend = stable            → 30
    river_trend = falling           → 10
    
  72h forecast escalation:
    prob_exceeds_extreme > 60%      → +25
    prob_exceeds_extreme 30-60%     → +15
    prob_exceeds_danger > 80%       → +20
    
  Earthquake escalation:
    aftershock probability (M5+) > 50% → 70
    magnitude > 6.5 (higher aftershock) → 80
    near active fault                   → +15
    
  Weather escalation:
    cape_jkg > 3000 + convection → 80 (storm developing)
    5-day forecast worsening trend   → +20
    monsoon onset approaching        → +15

SECONDARY DISASTER POTENTIAL:
  earthquake → landslide risk (mountain terrain)  → +20
  earthquake → dam failure (dam within 50km)      → +30
  flood → disease outbreak (standing water 48h+)  → +15
  heatwave → grid failure → hospital risk         → +20
  heavy rain → flood (soil saturated)             → +25

ESCALATION SCORE = (Trajectory × 0.60) + 
                   (Secondary_disaster × 0.40)
```

### 5.5 Response Capacity Score (Weight: 15%)

```
NOTE: Higher score = LOWER capacity = MORE vulnerable

MEDICAL CAPACITY:
  Beds per 1,000 population:
    > 2.0          → Score: 15 (adequate)
    1.0-2.0        → Score: 35
    0.5-1.0        → Score: 60
    0.2-0.5        → Score: 80
    < 0.2          → Score: 95
  
  Pakistan national average: 0.6 beds/1000
  Rural areas typical: 0.1-0.2 beds/1000

EVACUATION CAPACITY:
  Evacuation center capacity / total population:
    > 20%          → Score: 10
    10-20%         → Score: 30
    5-10%          → Score: 55
    2-5%           → Score: 75
    < 2%           → Score: 95

ROAD ACCESS:
  All national highways open             → 10
  Provincial roads passable              → 30
  Only district roads available          → 55
  Only village tracks available          → 75
  Roads blocked or likely to be         → 95

NGO PRESENCE (from web search):
  Multiple NGOs operational in district → 10
  One NGO present                       → 35
  NGOs in province but not district     → 60
  No known NGO presence                 → 85

RESPONSE CAPACITY SCORE =
  (Medical × 0.30) +
  (Evacuation × 0.25) +
  (Road_access × 0.25) +
  (NGO_presence × 0.20)
```

---

## SECTION 6: COMPOSITE SCORING AND RISK CLASSIFICATION

```
COMPOSITE RISK SCORE =
  (Hazard_Severity × 0.25) +
  (Exposure × 0.25) +
  (Vulnerability × 0.20) +
  (Escalation × 0.15) +
  (Response_Capacity × 0.15)

TERRAIN MULTIPLIER applied after composite:
  mountain terrain    → composite × 1.20
  riverine plain      → composite × 1.10
  coastal             → composite × 1.15
  urban               → composite × 1.10
  desert              → composite × 1.08
  plain/agricultural  → composite × 1.00

FINAL CAPPED AT 100.

RISK LEVEL:
  0-24   → LOW
  25-49  → MEDIUM
  50-74  → HIGH
  75-100 → EXTREME

MANDATORY OVERRIDE RULES:
  IF usgs_alert_level = 'red'         → MINIMUM EXTREME
  IF tsunami_flag = TRUE              → MINIMUM EXTREME
  IF dam failure risk detected        → MINIMUM EXTREME
  IF flood_status = 'emergency'       → MINIMUM HIGH
  IF magnitude >= 7.0 + shallow       → MINIMUM EXTREME
  IF population > 1M + any breach     → MINIMUM HIGH
```

---

## SECTION 7: COMPLETE SYSTEM PROMPT

```
You are the Risk Analysis Agent for ClimaSync.ai — Pakistan's 
AI-powered disaster management platform.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR IDENTITY AND RESPONSIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are the most critical decision-support component in the 
ClimaSync pipeline. Your risk assessment directly determines 
what resources are deployed, how many NGOs are mobilized, and 
whether evacuations are ordered. Errors in your assessment 
cost lives. Overestimation wastes resources. Underestimation 
causes deaths. You must be accurate, explainable, and honest 
about uncertainty.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY EXECUTION WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You MUST follow this exact sequence. Do not skip steps.
Do not reverse order. Do not combine steps.

STEP 1 — DATABASE READ: LOCATION CONTEXT
  Call get_location_data(district, province)
  You MUST extract:
    population, population_density, elevation_m
    flood_risk_zone, seismic_zone, heat_risk_zone
    infrastructure_quality, drainage_quality
    building_stock, poll_priority, location_tier

STEP 2 — DATABASE READ: INFRASTRUCTURE AT RISK
  Call get_infrastructure_at_risk(latitude, longitude,
    disaster_kind, impact_radius_km)
  
  Impact radius by disaster type:
    earthquake M4-5: 15km, M5-6: 25km, M6-7: 40km, M7+: 60km
    flood: 30km from gauge location
    heatwave: entire district
    heavy_rain: 20km
  
  You MUST extract:
    Total hospital count and bed capacity
    Total schools count and student capacity
    All bridges within radius
    All dams and barrages within radius
    All evacuation centers and their capacity
    All critical assets (is_critical=TRUE)

STEP 3 — DATABASE READ: CURRENT DISASTER DATA
  Call get_current_disaster_data(disaster_kind, identifiers)
  
  For EARTHQUAKE: pass usgs_event_id
    Extract: magnitude, depth_km, depth_class, 
    magnitude_class, felt_reports, cdi, mmi,
    usgs_alert_level, significance, data_quality,
    azimuthal_gap_deg, magnitude_was_revised,
    initial_magnitude, tsunami_flag
  
  For FLOOD: pass gauge_id and location_id
    Extract from flood_gauge_current:
      current_level_m, pct_of_danger, pct_of_warning,
      rise_rate_m_per_hour, river_trend, 
      hours_to_warning, hours_to_danger,
      flood_status, pct_of_historical_max
    Extract from flood_gauge_forecasts (24h, 48h, 72h):
      level_p10_m, level_p50_m, level_p90_m,
      prob_exceeds_warning_pct, prob_exceeds_danger_pct,
      prob_exceeds_extreme_pct, forecast_status,
      worst_case_status
    Extract from weather_hourly_window:
      precip_24h_mm, precip_72h_mm, cape_jkg
  
  For HEATWAVE: pass location_id
    Extract: temp_c, temp_apparent_c, temp_dewpoint_c,
    humidity_pct, flag_heatwave, precip_24h_mm,
    wind_speed_kmh, uv_index
    Extract from weather_daily_summaries (5 days):
      temp_max_c, temp_min_c for each day
      (to determine heatwave duration)
  
  For HEAVY RAIN: pass location_id
    Extract: precip_1h_mm, precip_6h_mm, precip_12h_mm,
    precip_24h_mm, precip_72h_mm, cape_jkg,
    weather_condition, flag_heavy_rain, 
    flag_severe_storm, wind_gusts_kmh

STEP 4 — WEB SEARCH: TERRAIN AND GEOGRAPHY
  Query: "[district] [province] Pakistan geography terrain 
          elevation landscape type mountains plains desert"
  Extract: Terrain type, slope, soil type, vegetation cover
  
  If terrain cannot be determined:
    Derive from: elevation_m + province + flood_risk_zone
    Document the derivation method

STEP 5 — WEB SEARCH: DEMOGRAPHICS AND POVERTY
  Query: "[district] Pakistan poverty rate population 
          census 2023 literacy rate vulnerable groups"
  Extract: Poverty rate, literacy, estimated outdoor workers
  
  If not found:
    Use provincial average for Pakistan context:
      Punjab rural poverty: ~35%
      Sindh rural poverty: ~55%
      Balochistan: ~65%
      KPK rural: ~45%
      GB/AJK: ~40%
    Mark as estimated with uncertainty flag

STEP 6 — WEB SEARCH: HISTORICAL CONTEXT
  Query: "[district] Pakistan [disaster_kind] history 
          damage deaths displaced NDMA PDMA site:reliefweb.int"
  Extract: Historical frequency, worst past event,
           typical impact pattern for this area

STEP 7 — WEB SEARCH: CURRENT GROUND SITUATION
  Query: "[district] [province] Pakistan [disaster_kind] 
          2025 news damage casualties roads blocked"
  Extract: Current media reports, confirmed casualties,
           roads blocked, areas already flooded,
           government response status

STEP 8 — DISASTER-TYPE SPECIFIC WEB SEARCH
  Execute the additional 4 searches defined for this
  specific disaster type (flood/earthquake/heatwave/rain)

STEP 9 — COMPUTE ALL FIVE DIMENSION SCORES
  For each dimension, you MUST:
    a) State the raw data values used
    b) Apply the scoring rules explicitly
    c) List each modifier applied
    d) Provide the final score with full calculation shown
    e) Write a plain English justification (3-5 sentences)
    f) Note any data gaps or uncertainties

STEP 10 — COMPUTE COMPOSITE SCORE
  Apply weights:
    Hazard Severity:    25%
    Exposure:           25%
    Vulnerability:      20%
    Escalation Risk:    15%
    Response Capacity:  15%
  
  Apply terrain multiplier
  Apply mandatory override rules
  Assign risk level

STEP 11 — PRODUCE STRUCTURED OUTPUT
  Fill every field of RiskAssessmentReport
  Never leave required fields empty
  Use "data_not_available" for genuinely missing data
  Always populate data_gaps list with what is missing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAKISTAN-SPECIFIC KNOWLEDGE BASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BUILDING VULNERABILITY:
  Kutcha (mud brick): collapses at M5.0+, 
    dissolves in 72h flooding, no heat protection
  Semi-pucca: survives M5.5 with damage
  Pucca (RCC): survives M6.0 if to code
  
  Rural Sindh: 60-70% kutcha or semi-pucca
  Rural Punjab: 40-50% kutcha or semi-pucca
  Rural KPK/Balochistan: 70-80% kutcha
  Urban Karachi: 30% kutcha in informal settlements
  Urban Lahore: 20% kutcha

DRAINAGE REALITY:
  Sindh cities: designed for 25mm/hour maximum
    Karachi 2020: 89mm in 4 hours → complete flooding
  Punjab irrigation canals: can overflow in heavy rain
  KPK mountain areas: no formal drainage, all runoff
  Islamabad: modern drainage but overwhelmed at 50mm/hr

HEALTHCARE REALITY:
  Pakistan national average: 0.6 beds per 1,000
  Rural areas: 0.1-0.2 beds per 1,000
  DHQ hospital: serves entire district (300k-2M people)
  BHU: one per union council, no emergency capacity
  
ROAD NETWORK REALITY:
  National Highways (M-1, M-2, N-5, etc): 
    All-weather, rarely close
  Provincial roads: Close in heavy rain >50mm/24h
  District roads: Close in flooding >30cm depth
  Village tracks (KPK mountains): 
    Close in M5.5+ earthquakes, heavy snowfall
    Helicopter becomes only access

EVACUATION REALITY:
  Pakistan has inadequate formal evacuation centers
  Schools are used as informal shelters
  Mosque compounds used for community gathering
  70% of rural families evacuate to relatives' homes
  Government-run camps: capacity severely limited

RIVER SYSTEM KNOWLEDGE:
  Indus: Controlled by Tarbela. Floods peak Aug-Sep.
  Jhelum: Controlled by Mangla. Fast rise in Kashmir rain.
  Chenab: Floods from Indian releases + local rain.
  Ravi: Often receives Indian floodwater releases.
  Sutlej: Receives Indian floodwater, politically sensitive.
  Kabul River: Rapid rise, mountainous catchment.
  
  Downstream warning time:
    Kashmir earthquake → Jhelum flood peak: 18-36 hours
    KPK heavy rain → Indus at Sukkur peak: 5-7 days

SEASONAL CONTEXT:
  July-August: Peak monsoon. Floods maximum.
  April-June: Heatwave season. Karachi/interior Sindh.
  October-November: Harvest. Crop loss amplifies damage.
  December-February: Cold waves. GB/KPK mountains.
  
FAULT SYSTEM KNOWLEDGE:
  Chaman Fault: Balochistan. Major strike-slip.
    Magnitude potential: M7.5+
    Last major: 2013 M7.7 Awaran
  Makran Subduction Zone: Coastal Balochistan.
    Tsunami potential: YES
    1945 Makran earthquake caused tsunami
  Himalayan Frontal Thrust: Punjab/KPK foothills.
    2005 M7.6 Kashmir on this system
    Magnitude potential: M8.0+
  Quetta Fault: Directly under Quetta city
    1935 Quetta earthquake: 60,000 deaths

POVERTY AND VULNERABILITY CONTEXT:
  Pakistan national poverty rate: ~38% (2023)
  Interior Sindh (Jacobabad, Kashmore): ~65%
  Balochistan rural: ~65%
  Punjab rural average: ~35%
  Urban Karachi formal: ~25%
  Urban Karachi informal: ~55%
  
  Poor households: zero savings, no insurance,
  no vehicles for evacuation, dependent on 
  government/NGO relief entirely

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNCERTAINTY RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When data is missing or uncertain:
  1. Never fabricate a number
  2. State the uncertainty explicitly
  3. Use Pakistan-context defaults where appropriate
  4. Document which default was used and why
  5. Add the missing data to data_gaps list
  6. Adjust data_confidence accordingly:
     All data available → High
     1-2 gaps filled with estimates → Medium
     3+ gaps or major gaps → Low

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Always produce valid RiskAssessmentReport JSON.
Every score field must have a justification field.
The critical_actions_needed list must have minimum 5 items.
The data_gaps list must be populated even if empty list [].
The web_search_findings must cite sources.
```

---

## SECTION 8: COMPLETE OUTPUT SCHEMA

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

class DataConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class SituationTrajectory(str, Enum):
    IMPROVING = "Improving"
    STABLE = "Stable"
    WORSENING = "Worsening"
    RAPIDLY_WORSENING = "Rapidly Worsening"

class ResponseUrgency(str, Enum):
    MONITOR = "Monitor"
    PREPARE = "Prepare"
    RESPOND = "Respond"
    EMERGENCY = "Emergency"

# ── DIMENSION SCORE MODELS ────────────────────────────────────────

class HazardSeverityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    base_score: int
    modifiers_applied: list[str]
    key_metric_name: str
    key_metric_value: str
    secondary_hazards_identified: list[str]
    justification: str

class TerrainAssessment(BaseModel):
    terrain_type: str
    terrain_source: str        # "database_derived" or "web_search"
    terrain_vulnerability_score: int
    terrain_multiplier: float
    terrain_implications: list[str]
    # e.g. ["Single track mountain roads may close",
    #        "Landslide risk elevated"]

class PopulationBreakdown(BaseModel):
    total_population: int
    population_source: str
    estimated_directly_affected: int
    estimation_method: str
    vulnerable_groups: dict[str, int]
    # {"children_under_5": 15000, "elderly": 8000,
    #  "outdoor_workers": 25000}
    poverty_rate_pct: float
    poverty_source: str

class InfrastructureAtRisk(BaseModel):
    hospitals_count: int
    hospital_beds_total: int
    hospital_beds_per_1000: float
    critical_hospitals: list[str]
    schools_count: int
    students_at_risk: int
    bridges_count: int
    critical_bridges: list[str]
    dams_barrages_count: int
    dam_failure_risk: bool
    evacuation_centers_count: int
    evacuation_capacity_total: int
    evacuation_coverage_pct: float
    power_stations_at_risk: int
    water_treatment_at_risk: int
    total_critical_assets: int

class ExposureScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    population_score: int
    infrastructure_score: int
    population_breakdown: PopulationBreakdown
    infrastructure_at_risk: InfrastructureAtRisk
    justification: str

class VulnerabilityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    building_vulnerability_score: int
    building_stock_type: str
    building_stock_source: str
    drainage_vulnerability_score: int
    drainage_quality_level: str
    infrastructure_quality_score: int
    poverty_vulnerability_score: int
    terrain_vulnerability_score: int
    component_scores: dict[str, int]
    justification: str

class EscalationScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    is_worsening: bool
    trajectory_description: str
    current_trajectory_score: int
    secondary_disaster_score: int
    secondary_disasters_possible: list[str]
    escalation_probability_pct: float
    hours_until_peak_estimate: Optional[float]
    peak_estimate_basis: str
    justification: str

class ResponseCapacityScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    # Higher score = lower capacity = more vulnerable
    medical_capacity_score: int
    evacuation_capacity_score: int
    road_access_score: int
    ngo_presence_score: int
    road_status_description: str
    ngo_presence_description: str
    nearest_major_hospital_km: Optional[float]
    response_time_estimate_hours: Optional[float]
    justification: str

# ── WEB SEARCH FINDINGS ───────────────────────────────────────────

class WebSearchFinding(BaseModel):
    query_used: str
    key_findings: str
    sources_cited: list[str]
    confidence: str    # "confirmed" / "estimated" / "unverified"

class WebSearchFindings(BaseModel):
    terrain_geography: WebSearchFinding
    demographics_poverty: WebSearchFinding
    historical_disaster_context: WebSearchFinding
    current_ground_situation: WebSearchFinding
    disaster_specific_findings: list[WebSearchFinding]
    # Contains flood/earthquake/heat specific findings

# ── IMPACT ESTIMATES ──────────────────────────────────────────────

class ImpactEstimates(BaseModel):
    # Population impact
    estimated_population_affected: int
    estimation_confidence: DataConfidence
    
    # Casualty risk
    estimated_deaths_range: str
    # e.g. "10-50 deaths possible" or "mass casualty risk"
    death_risk_level: str
    # Low / Medium / High / Extreme
    
    # Displacement
    estimated_displaced_persons: int
    displacement_duration_estimate: str
    # "hours" / "days" / "weeks" / "months"
    
    # Economic damage
    estimated_economic_damage_pkr: str
    # e.g. "5-15 billion PKR"
    estimated_economic_damage_usd: str
    economic_damage_confidence: DataConfidence
    
    # Livelihood impact
    agricultural_land_at_risk_acres: Optional[int]
    crop_loss_probability_pct: Optional[float]
    livestock_at_risk: Optional[str]

# ── MAIN REPORT ───────────────────────────────────────────────────

class RiskAssessmentReport(BaseModel):
    
    # ── IDENTIFICATION ─────────────────────────────────────────────
    assessment_id: str
    breach_id: str
    disaster_kind: str
    breach_severity_received: str
    location_name: str
    district: str
    province: str
    latitude: float
    longitude: float
    observation_time: str
    is_forecast_breach: bool
    forecast_horizon_h: Optional[int]
    assessment_timestamp: str
    agent_version: str = "risk_analysis_v2.0"
    
    # ── TERRAIN ────────────────────────────────────────────────────
    terrain_assessment: TerrainAssessment
    
    # ── FIVE DIMENSION SCORES ──────────────────────────────────────
    hazard_severity: HazardSeverityScore
    exposure: ExposureScore
    vulnerability: VulnerabilityScore
    escalation_risk: EscalationScore
    response_capacity: ResponseCapacityScore
    
    # ── COMPOSITE RESULT ───────────────────────────────────────────
    score_breakdown: dict[str, float]
    # {"hazard_weighted": 22.5, "exposure_weighted": 19.0, ...}
    composite_score_before_terrain: float
    terrain_multiplier_applied: float
    composite_risk_score: float
    override_applied: bool
    override_reason: Optional[str]
    risk_level: RiskLevel
    risk_level_justification: str
    
    # ── IMPACT ESTIMATES ───────────────────────────────────────────
    impact_estimates: ImpactEstimates
    
    # ── SITUATIONAL ASSESSMENT ─────────────────────────────────────
    situation_trajectory: SituationTrajectory
    escalation_triggers: list[str]
    # List of specific conditions that would escalate risk
    
    # ── WEB SEARCH CONTEXT ─────────────────────────────────────────
    web_search_findings: WebSearchFindings
    
    # ── HANDOFF TO PRECAUTION DEFINER ──────────────────────────────
    recommended_response_urgency: ResponseUrgency
    critical_actions_needed: list[str]
    # Minimum 5 items, ordered by urgency
    time_sensitive_actions: list[str]
    # Actions that MUST happen within the next 6 hours
    
    # ── DATA QUALITY ───────────────────────────────────────────────
    data_confidence: DataConfidence
    data_gaps: list[str]
    # Empty list if all data available
    assumptions_made: list[str]
    # Explicit list of every assumption made during assessment
```

---

## SECTION 9: FILE STRUCTURE

```
risk_analysis_agent/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── exceptions.py
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── risk_agent.py          ← Agent + system prompt
│   │   │
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── location_tool.py
│   │   │   ├── infrastructure_tool.py
│   │   │   ├── disaster_data_tool.py
│   │   │   └── web_search_tool.py
│   │   │
│   │   └── scoring/
│   │       ├── __init__.py
│   │       ├── terrain_classifier.py
│   │       ├── hazard_scorer.py
│   │       ├── exposure_scorer.py
│   │       ├── vulnerability_scorer.py
│   │       ├── escalation_scorer.py
│   │       ├── response_scorer.py
│   │       └── composite_scorer.py
│   │
│   ├── models/
│   │   ├── input_models.py
│   │   └── output_models.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── queries/
│   │       ├── location_queries.py
│   │       ├── infrastructure_queries.py
│   │       └── disaster_data_queries.py
│   │
│   └── api/
│       └── routes/
│           ├── assessment_controller.py
│           └── health_controller.py
│
├── .env
├── pyproject.toml
└── README.md
```

---

## SECTION 10: WHAT MAKES THIS FINAL DESIGN COMPLETE

```
┌──────────────────────────────────────────────────────────────────┐
│              ALL GAPS NOW FILLED                                 │
├─────────────────────────────────┬────────────────────────────────┤
│  GAP                            │  SOLUTION                      │
├─────────────────────────────────┼────────────────────────────────┤
│  Terrain type unknown           │  Derived from DB elevation     │
│                                 │  + province + flood_zone.      │
│                                 │  Confirmed by web search.      │
│                                 │  Multiplier applied to score.  │
├─────────────────────────────────┼────────────────────────────────┤
│  Road network quality           │  Web search query 4 retrieves  │
│  not in database                │  road type and seasonal        │
│                                 │  accessibility. Road score     │
│                                 │  feeds response capacity.      │
├─────────────────────────────────┼────────────────────────────────┤
│  Poverty level missing          │  Web search query 5.           │
│                                 │  If not found: provincial      │
│                                 │  defaults applied with         │
│                                 │  explicit uncertainty flag.    │
├─────────────────────────────────┼────────────────────────────────┤
│  Building stock proportions     │  DB has type category.         │
│  not granular                   │  Web search gets district      │
│                                 │  specific kutcha percentages.  │
│                                 │  Pakistan defaults by region   │
│                                 │  documented in system prompt.  │
├─────────────────────────────────┼────────────────────────────────┤
│  NGO presence unknown           │  Web search query retrieves    │
│                                 │  active NGO operations.        │
│                                 │  Feeds response capacity score.│
├─────────────────────────────────┼────────────────────────────────┤
│  Upstream dam status            │  Flood-specific web search 5   │
│  for flood events               │  queries WAPDA release data.   │
│                                 │  Dam failure risk flag set.    │
├─────────────────────────────────┼────────────────────────────────┤
│  Seasonal context               │  System prompt encodes all     │
│                                 │  Pakistan seasons and their    │
│                                 │  disaster implications.        │
│                                 │  Agent applies automatically.  │
├─────────────────────────────────┼────────────────────────────────┤
│  Vulnerable population groups   │  Estimated from total          │
│                                 │  population + Pakistan ratios. │
│                                 │  Web search confirms local     │
│                                 │  demographic specifics.        │
├─────────────────────────────────┼────────────────────────────────┤
│  Historical disaster context    │  Web search targets NDMA,      │
│                                 │  PDMA, ReliefWeb databases     │
│                                 │  specifically.                 │
├─────────────────────────────────┼────────────────────────────────┤
│  Secondary disaster risk        │  Escalation score explicitly   │
│                                 │  checks all combinations:      │
│                                 │  quake→landslide, flood→       │
│                                 │  disease, heat→grid failure.   │
├─────────────────────────────────┼────────────────────────────────┤
│  Economic damage estimate       │  Impact estimates model        │
│                                 │  includes PKR and USD ranges.  │
│                                 │  Agriculture loss calculated   │
│                                 │  from land and crop calendar.  │
├─────────────────────────────────┼────────────────────────────────┤
│  Soil saturation state          │  Flood-specific web search 7   │
│                                 │  queries current waterlogging. │
│                                 │  72h precip data from DB       │
│                                 │  used as proxy when web        │
│                                 │  search unavailable.           │
└─────────────────────────────────┴────────────────────────────────┘
```

This is the complete, gap-free, Pakistan-specific Risk Analysis Agent design. Every ambiguity is resolved. Every data gap has a fallback. Every score is explainable. Ready for your next instruction.