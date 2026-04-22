import streamlit as st
import re
import pandas as pd

st.set_page_config(page_title="Stratégia Elemző", layout="wide")
st.title("🎯 Stratégia: Félidő X -> Végeredmény 1/2")

raw_data = st.text_area("Másold be a meccs adatokat:", height=200)

def parse_data(raw_text):
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    data_by_hour = {}
    current_hour = "00"
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Óra felismerése
        if (line.isdigit() and len(line) <= 2) or ('%' in line):
            val = re.search(r'\d+', line)
            if val:
                num = int(val.group())
                if 0 <= num <= 23:
                    current_hour = f"{num:02d}"
                    if current_hour not in data_by_hour: data_by_hour[current_hour] = []
                    i += 1
                    continue
        
        # Meccs blokk (FT, HT, Oddsok)
        if re.match(r'^\d+-\d+$', line):
            if i + 3 < len(lines):
                try:
                    ft_scores = line.split('-')
                    ht_scores = lines[i+1].split('-')
                    
                    if current_hour not in data_by_hour: data_by_hour[current_hour] = []
                    
                    data_by_hour[current_hour].append({
                        'score': line, 
                        'ht_score': lines[i+1],
                        'h': int(ft_scores[0]), 'a': int(ft_scores[1]), 
                        'ht_h': int(ht_scores[0]), 'ht_a': int(ht_scores[1]),
                        'htc': float(lines[i+2].split('@')[1]),
                        'htv': float(lines[i+3].split('@')[1])
                    })
                    i += 4 
                    continue
                except: pass
        i += 1
    return data_by_hour

if raw_data:
    results = parse_data(raw_data)
    
    # --- ÖSSZEGZŐ TÁBLÁZAT ---
    summary_data = []
    for hour in sorted(results.keys()):
        matches = results[hour][:9] # Csak az első 9
        hits = 0
        first_hit = None
        
        for idx, m in enumerate(matches):
            if (m['ht_h'] == m['ht_a']) and (m['h'] != m['a']):
                hits += 1
                if first_hit is None: first_hit = idx + 1
        
        summary_data.append({
            "Óra": f"{hour}:00",
            "Stratégia (9 meccs)": f"{first_hit}.ra nyert" if hits > 0 else "0 NYERT"
        })
    
    st.subheader("📈 Stratégia Összegzés")
    
    def color_zeros(val):
        return 'background-color: #ff4b4b; color: white' if val == "0 NYERT" else 'background-color: #00cc96; color: white'

    df_summary = pd.DataFrame(summary_data)
    st.dataframe(
        df_summary.style.map(color_zeros, subset=['Stratégia (9 meccs)']), 
        width=500, hide_index=True
    )
    st.markdown("---")

    # --- RÉSZLETES NÉZET ---
    for hour in sorted(results.keys()):
        st.subheader(f"🕒 {hour}:00 Óra")
        matches = results[hour][:9]
        
        strat_data = []
        for idx, m in enumerate(matches):
            is_success = (m['ht_h'] == m['ht_a']) and (m['h'] != m['a'])
            strat_data.append({
                "Meccs": f"{idx+1}.",
                "Félidő": m['ht_score'],
                "Eredmény": m['score'],
                "Státusz": "✅ NYERT" if is_success else "❌"
            })
        
        st.table(pd.DataFrame(strat_data))
        st.divider()