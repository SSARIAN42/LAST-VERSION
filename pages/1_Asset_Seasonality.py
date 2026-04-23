import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

if "seas_analysis_done" not in st.session_state:
    st.session_state.seas_analysis_done = False
if "seas_results_df" not in st.session_state:
    st.session_state.seas_results_df = None
if "seas_analysis_params" not in st.session_state:
    st.session_state.seas_analysis_params = {}

st.title("Seasonality Board for Different Rates Products")
st.markdown("---")


@st.cache_data
def load_data():
    try:
        file_path = r"\\cad.local\dfsroot\GroupShares\PARIS\CAVENTOR\Analytics\8. Seasonality\DATA_SEASONALITY.xlsx"
        categories_map = {}
        try:
            df_mapping = pd.read_excel(file_path, sheet_name="Sheet1", header=0)
            if "NAME" in df_mapping.columns and "CATEGORIES" in df_mapping.columns:
                for _, row in df_mapping.iterrows():
                    name = row.get("NAME")
                    category = row.get("CATEGORIES")
                    if pd.notna(name) and pd.notna(category):
                        categories_map[str(name).strip()] = str(category).strip()
        except Exception as e:
            st.warning(f"Could not read categories from Sheet1: {str(e)}")
        df = pd.read_excel(file_path, sheet_name="DATA", header=2)
        df.columns = ["Date"] + list(df.columns[1:])
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        df = df.dropna(axis=1, how="all")
        categories_map_cleaned = {}
        for col in df.columns:
            if col in categories_map:
                categories_map_cleaned[col] = categories_map[col]
            else:
                found = False
                for name, category in categories_map.items():
                    if name.strip().lower() == str(col).strip().lower():
                        categories_map_cleaned[col] = category
                        found = True
                        break
                if not found:
                    categories_map_cleaned[col] = "Unknown"
        return df, categories_map_cleaned
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame(), {}


def get_available_windows(horizon):
    if horizon == "Month":
        return ["First 3 days of month", "Last 3 days of month", "First week of month",
                "First two weeks of month", "Last week of month", "Last two weeks of month"]
    elif horizon in ["Quarter", "Semester", "Year"]:
        period = horizon.lower()
        return [f"First 3 days of {period}", f"Last 3 days of {period}",
                f"First week of {period}", f"First two weeks of {period}",
                f"First four weeks of {period}", f"Last week of {period}",
                f"Last two weeks of {period}", f"Last four weeks of {period}"]
    else:
        return ["Custom period"]


def can_calculate_window(period_data, window, period_end, df_max_date):
    if len(period_data) == 0:
        return False
    if "First" in window and "days" in window:
        n_days = int(window.split()[1])
        return len(period_data) >= n_days + 1
    elif "Last" in window and "days" in window:
        n_days = int(window.split()[1])
        return df_max_date >= period_end and len(period_data) >= n_days + 1
    elif "First week" in window and "weeks" not in window:
        return len(period_data) >= 6
    elif "First two weeks" in window:
        return len(period_data) >= 11
    elif "First three weeks" in window:
        return len(period_data) >= 16
    elif "First four weeks" in window:
        return len(period_data) >= 21
    elif "Last week" in window and "weeks" not in window:
        return df_max_date >= period_end and len(period_data) >= 6
    elif "Last two weeks" in window:
        return df_max_date >= period_end and len(period_data) >= 11
    elif "Last three weeks" in window:
        return df_max_date >= period_end and len(period_data) >= 16
    elif "Last four weeks" in window:
        return df_max_date >= period_end and len(period_data) >= 21
    return False


def get_periods_to_analyze(df, horizon, lookback_years, window, selected_months=None):
    current_date = df.index.max()
    periods = []
    if horizon == "Month":
        current_month = current_date.month
        current_year = current_date.year
        can_use_current = False
        month_start = pd.Timestamp(year=current_year, month=current_month, day=1)
        if current_month == 12:
            month_end = pd.Timestamp(year=current_year, month=12, day=31)
        else:
            month_end = pd.Timestamp(year=current_year, month=current_month + 1, day=1) - pd.DateOffset(days=1)
        month_data = df[(df.index >= month_start) & (df.index <= month_end)]
        if can_calculate_window(month_data, window, month_end, current_date):
            can_use_current = True
        if can_use_current:
            start_year = current_year - lookback_years
            start_month = current_month
        else:
            if current_month == 1:
                start_year = current_year - lookback_years - 1
                start_month = 12
            else:
                start_year = current_year - lookback_years
                start_month = current_month - 1
        for year in range(start_year, current_year + 1):
            month_range = range(1, 13)
            if year == start_year:
                month_range = range(start_month, 13)
            elif year == current_year:
                month_range = range(1, current_month + 1) if can_use_current else range(1, current_month)
            for month in month_range:
                if selected_months and "All" not in selected_months:
                    month_names = ["January", "February", "March", "April", "May", "June",
                                   "July", "August", "September", "October", "November", "December"]
                    if month_names[month - 1] not in selected_months:
                        continue
                month_start = pd.Timestamp(year=year, month=month, day=1)
                if month == 12:
                    month_end = pd.Timestamp(year=year, month=12, day=31)
                else:
                    month_end = pd.Timestamp(year=year, month=month + 1, day=1) - pd.DateOffset(days=1)
                month_data = df[(df.index >= month_start) & (df.index <= month_end)]
                if can_calculate_window(month_data, window, month_end, current_date):
                    periods.append((month_start, month_end, month_data))
        if not selected_months or "All" in selected_months:
            periods = periods[-lookback_years * 12:]
    elif horizon == "Quarter":
        current_quarter = (current_date.month - 1) // 3 + 1
        current_year = current_date.year
        can_use_current = False
        quarter_start = pd.Timestamp(year=current_year, month=(current_quarter - 1) * 3 + 1, day=1)
        quarter_end = quarter_start + pd.DateOffset(months=3) - pd.DateOffset(days=1)
        quarter_data = df[(df.index >= quarter_start) & (df.index <= quarter_end)]
        if can_calculate_window(quarter_data, window, quarter_end, current_date):
            can_use_current = True
        if can_use_current:
            start_year = current_year - lookback_years
            start_quarter = current_quarter
        else:
            if current_quarter == 1:
                start_year = current_year - lookback_years - 1
                start_quarter = 4
            else:
                start_year = current_year - lookback_years
                start_quarter = current_quarter - 1
        for year in range(start_year, current_year + 1):
            quarter_range = range(1, 5)
            if year == start_year:
                quarter_range = range(start_quarter, 5)
            elif year == current_year:
                quarter_range = range(1, current_quarter + 1) if can_use_current else range(1, current_quarter)
            for quarter in quarter_range:
                quarter_start = pd.Timestamp(year=year, month=(quarter - 1) * 3 + 1, day=1)
                quarter_end = quarter_start + pd.DateOffset(months=3) - pd.DateOffset(days=1)
                quarter_data = df[(df.index >= quarter_start) & (df.index <= quarter_end)]
                if can_calculate_window(quarter_data, window, quarter_end, current_date):
                    periods.append((quarter_start, quarter_end, quarter_data))
        periods = periods[-lookback_years * 4:]
    elif horizon == "Semester":
        current_semester = 1 if current_date.month <= 6 else 2
        current_year = current_date.year
        can_use_current = False
        sem_start = pd.Timestamp(year=current_year, month=(current_semester - 1) * 6 + 1, day=1)
        sem_end = sem_start + pd.DateOffset(months=6) - pd.DateOffset(days=1)
        sem_data = df[(df.index >= sem_start) & (df.index <= sem_end)]
        if can_calculate_window(sem_data, window, sem_end, current_date):
            can_use_current = True
        if can_use_current:
            start_year = current_year - lookback_years
            start_semester = current_semester
        else:
            if current_semester == 1:
                start_year = current_year - lookback_years - 1
                start_semester = 2
            else:
                start_year = current_year - lookback_years
                start_semester = 1
        for year in range(start_year, current_year + 1):
            semester_range = range(1, 3)
            if year == start_year:
                semester_range = range(start_semester, 3) if start_semester == 2 else range(1, 3)
            elif year == current_year:
                semester_range = range(1, current_semester + 1) if can_use_current else range(1, current_semester)
            for semester in semester_range:
                sem_start = pd.Timestamp(year=year, month=(semester - 1) * 6 + 1, day=1)
                sem_end = sem_start + pd.DateOffset(months=6) - pd.DateOffset(days=1)
                sem_data = df[(df.index >= sem_start) & (df.index <= sem_end)]
                if can_calculate_window(sem_data, window, sem_end, current_date):
                    periods.append((sem_start, sem_end, sem_data))
        periods = periods[-lookback_years * 2:]
    elif horizon == "Year":
        current_year = current_date.year
        can_use_current = False
        year_start = pd.Timestamp(year=current_year, month=1, day=1)
        year_end = pd.Timestamp(year=current_year, month=12, day=31)
        year_data = df[(df.index >= year_start) & (df.index <= year_end)]
        if can_calculate_window(year_data, window, year_end, current_date):
            can_use_current = True
        start_year = current_year - lookback_years + 1 if can_use_current else current_year - lookback_years
        for year in range(start_year, current_year + 1):
            if year == current_year and not can_use_current:
                continue
            year_start = pd.Timestamp(year=year, month=1, day=1)
            year_end = pd.Timestamp(year=year, month=12, day=31)
            year_data = df[(df.index >= year_start) & (df.index <= year_end)]
            if can_calculate_window(year_data, window, year_end, current_date):
                periods.append((year_start, year_end, year_data))
        periods = periods[-lookback_years:]
    return periods


def extract_period_from_data(df, period_data, window):
    def concat_period(prev_row, current_rows):
        if prev_row is None or current_rows is None or current_rows.empty:
            return None
        return pd.concat([prev_row, current_rows])
    if "First" in window and "days" in window:
        n_days = int(window.split()[1])
        if len(period_data) < n_days: return None
        first_day = period_data.index[0]
        prev_row = df.iloc[df.index.get_loc(first_day) - 1: df.index.get_loc(first_day)] if df.index.get_loc(first_day) > 0 else None
        return concat_period(prev_row, period_data.iloc[:n_days])
    elif "Last" in window and "days" in window:
        n_days = int(window.split()[1])
        if len(period_data) < n_days: return None
        prev_row = period_data.iloc[[-(n_days + 1)]] if len(period_data) > n_days else None
        return concat_period(prev_row, period_data.iloc[-n_days:])
    elif "First week" in window and "weeks" not in window:
        if len(period_data) < 5: return None
        first_day = period_data.index[0]
        prev_row = df.iloc[df.index.get_loc(first_day) - 1: df.index.get_loc(first_day)] if df.index.get_loc(first_day) > 0 else None
        return concat_period(prev_row, period_data.iloc[:5])
    elif "First two weeks" in window:
        if len(period_data) < 10: return None
        first_day = period_data.index[0]
        prev_row = df.iloc[df.index.get_loc(first_day) - 1: df.index.get_loc(first_day)] if df.index.get_loc(first_day) > 0 else None
        return concat_period(prev_row, period_data.iloc[:10])
    elif "First three weeks" in window:
        if len(period_data) < 15: return None
        first_day = period_data.index[0]
        prev_row = df.iloc[df.index.get_loc(first_day) - 1: df.index.get_loc(first_day)] if df.index.get_loc(first_day) > 0 else None
        return concat_period(prev_row, period_data.iloc[:15])
    elif "First four weeks" in window:
        if len(period_data) < 20: return None
        first_day = period_data.index[0]
        prev_row = df.iloc[df.index.get_loc(first_day) - 1: df.index.get_loc(first_day)] if df.index.get_loc(first_day) > 0 else None
        return concat_period(prev_row, period_data.iloc[:20])
    elif "Last week" in window and "weeks" not in window:
        if len(period_data) < 5: return None
        prev_row = period_data.iloc[[-6]] if len(period_data) > 5 else None
        return concat_period(prev_row, period_data.iloc[-5:])
    elif "Last two weeks" in window:
        if len(period_data) < 10: return None
        prev_row = period_data.iloc[[-11]] if len(period_data) > 10 else None
        return concat_period(prev_row, period_data.iloc[-10:])
    elif "Last three weeks" in window:
        if len(period_data) < 15: return None
        prev_row = period_data.iloc[[-16]] if len(period_data) > 15 else None
        return concat_period(prev_row, period_data.iloc[-15:])
    elif "Last four weeks" in window:
        if len(period_data) < 20: return None
        prev_row = period_data.iloc[[-21]] if len(period_data) > 20 else None
        return concat_period(prev_row, period_data.iloc[-20:])
    return None


def calculate_performance(filtered_periods, asset):
    variations, gains, losses = [], [], []
    for period_data in filtered_periods:
        if asset not in period_data.columns: continue
        asset_data = period_data[asset].dropna()
        if len(asset_data) < 2: continue
        variation = asset_data.iloc[-1] - asset_data.iloc[0]
        variations.append(variation)
        if variation > 0: gains.append(variation)
        else: losses.append(abs(variation))
    if len(variations) == 0: return None
    avg_variation_bp = np.mean(variations)
    success_rate = (len(gains) / len(variations)) * 100
    avg_gain = np.mean(gains) if gains else 0
    avg_loss = np.mean(losses) if losses else 1
    return {
        "Gain (bp)": round(avg_variation_bp, 2),
        "Success Rate (%)": round(success_rate, 1),
        "G/L Ratio Bull": round(avg_gain / avg_loss if avg_loss != 0 else float("inf"), 2),
        "G/L Ratio Bear": round(avg_loss / avg_gain if avg_gain != 0 else float("inf"), 2),
        "Nb observations": len(variations),
    }


def plot_big_picture_heatmap(df, asset_name, lookback_years, timeframe):
    if asset_name not in df.columns: return None
    current_date = df.index.max()
    start_year = current_date.year - lookback_years + 1
    years = list(range(start_year, current_date.year + 1))
    if timeframe == "Weekly":
        n_cols, col_labels = 53, [f"W{w}" for w in range(1, 54)]
    elif timeframe == "Monthly":
        n_cols, col_labels = 12, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    else:
        n_cols, col_labels = 4, ["Q1", "Q2", "Q3", "Q4"]
    heatmap_data = np.full((len(years), n_cols), np.nan)
    asset_series = df[asset_name].dropna()
    for yi, year in enumerate(years):
        if timeframe == "Weekly":
            for week in range(1, 54):
                try:
                    iso = asset_series.index.isocalendar()
                    mask = (iso.year == year) & (iso.week == week)
                    week_dates = asset_series[mask.values]
                    if len(week_dates) < 1: continue
                    first_loc = asset_series.index.get_loc(week_dates.index[0])
                    if first_loc == 0: continue
                    heatmap_data[yi, week - 1] = week_dates.iloc[-1] - asset_series.iloc[first_loc - 1]
                except Exception: continue
        elif timeframe == "Monthly":
            for month in range(1, 13):
                try:
                    month_dates = asset_series[(asset_series.index.year == year) & (asset_series.index.month == month)]
                    if len(month_dates) < 1: continue
                    first_loc = asset_series.index.get_loc(month_dates.index[0])
                    if first_loc == 0: continue
                    heatmap_data[yi, month - 1] = month_dates.iloc[-1] - asset_series.iloc[first_loc - 1]
                except Exception: continue
        else:
            for quarter in range(1, 5):
                try:
                    q_months = [(quarter - 1) * 3 + m for m in range(1, 4)]
                    quarter_dates = asset_series[(asset_series.index.year == year) & (asset_series.index.month.isin(q_months))]
                    if len(quarter_dates) < 1: continue
                    first_loc = asset_series.index.get_loc(quarter_dates.index[0])
                    if first_loc == 0: continue
                    heatmap_data[yi, quarter - 1] = quarter_dates.iloc[-1] - asset_series.iloc[first_loc - 1]
                except Exception: continue
    avg_row = np.nanmean(heatmap_data, axis=0)
    combined_data = np.vstack([avg_row, heatmap_data])
    combined_labels = ["Average"] + [str(y) for y in years]
    combined_text = [[f"{v:.2f}" if not np.isnan(v) else "" for v in avg_row]]
    combined_text.extend([[f"{v:.2f}" if not np.isnan(v) else "" for v in row] for row in heatmap_data])
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=combined_data, x=col_labels, y=combined_labels,
        colorscale=[[0, "rgb(220,30,30)"], [0.5, "rgb(255,255,255)"], [1, "rgb(0,180,50)"]],
        zmid=0, text=combined_text, texttemplate="%{text}", textfont={"size": 10, "color": "black"},
        colorbar=dict(title=dict(text="Variation (bps)", side="right"), tickmode="linear", tick0=0, dtick=10),
        hovertemplate="<b>%{y} - %{x}</b><br>%{z:.2f} bps<extra></extra>"))
    fig.update_layout(title=f"Big Picture – {asset_name} ({timeframe}, {lookback_years}y lookback)",
        xaxis=dict(side="bottom"), yaxis=dict(title="", autorange="reversed"),
        template="plotly_white", height=400 + len(years) * 30, margin=dict(l=80, r=80, t=80, b=80))
    return fig


def plot_spaghetti(df, asset_name, horizon, window, lookback_years, selected_months=None, custom_start=None, custom_end=None):
    if horizon != "Custom":
        periods = get_periods_to_analyze(df, horizon, lookback_years, window, selected_months)
    else:
        periods = []
        if custom_start and custom_end:
            current_date = df.index.max()
            for year in range(df.index.min().year, df.index.max().year + 1):
                try:
                    start_date = pd.Timestamp(year=year, month=custom_start.month, day=custom_start.day)
                    end_date = pd.Timestamp(year=year, month=custom_end.month, day=custom_end.day)
                    if (current_date - end_date).days <= 365 * lookback_years or (current_date >= start_date and current_date <= end_date):
                        period_data = df[(df.index >= start_date) & (df.index <= end_date)]
                        if len(period_data) > 0:
                            periods.append((start_date, end_date, period_data))
                except Exception: continue
    fig = go.Figure()
    fig.add_hline(y=0, line_width=1.5, line_color="rgba(0,0,0,0.2)")
    margin, num_periods, all_rel_vals, max_core_length = 5, len(periods), [], 0
    if num_periods == 0: return None
    for i, (start_date, _, p_data) in enumerate(periods):
        ext = p_data if horizon == "Custom" else extract_period_from_data(df, p_data, window)
        if ext is not None and asset_name in ext.columns:
            start_idx = df.index.get_loc(ext.index[0])
            end_idx = df.index.get_loc(ext.index[-1])
            core_length = len(ext)
            max_core_length = max(max_core_length, core_length)
            full_seq = df.iloc[max(0, start_idx - margin): min(len(df), end_idx + margin + 1)][asset_name]
            rel_vals = full_seq.values - full_seq.iloc[0]
            x_axis = np.arange(-margin, len(rel_vals) - margin)
            core_start_pos, core_end_pos = 0, core_length - 1
            month = start_date.month
            year_label = start_date.strftime("%Y")
            if horizon == "Month": period_label = f"M{month} {year_label}"
            elif horizon == "Quarter": period_label = f"Q{(month-1)//3+1} {year_label}"
            elif horizon == "Semester": period_label = f"S{1 if month<=6 else 2} {year_label}"
            elif horizon == "Custom": period_label = f"{start_date.strftime('%d/%m')} - {ext.index[-1].strftime('%d/%m/%Y')}"
            else: period_label = year_label
            weight = ((i + 1) / num_periods) ** 2
            before_mask = x_axis <= core_start_pos
            fig.add_trace(go.Scatter(x=x_axis[before_mask], y=rel_vals[before_mask], mode="lines",
                line=dict(width=1, color="rgba(150,150,150,0.2)"), showlegend=False,
                hoverinfo="skip", legendgroup="Périodes", name="Périodes historiques"))
            core_mask = (x_axis >= core_start_pos) & (x_axis <= core_end_pos)
            final_perf = rel_vals[core_mask][-1] - rel_vals[core_mask][0]
            color = f"rgba(0,180,50,{0.2+0.7*weight})" if final_perf > 0 else f"rgba(220,30,30,{0.2+0.7*weight})"
            fig.add_trace(go.Scatter(x=x_axis[core_mask], y=rel_vals[core_mask], mode="lines",
                name="Périodes historiques", line=dict(width=1.5+3.5*weight, color=color),
                hovertemplate=f"<b>{period_label}</b>: %{{y:.2f}} bps<extra></extra>",
                legendgroup="Périodes", showlegend=(i == 0)))
            after_mask = x_axis >= core_end_pos
            fig.add_trace(go.Scatter(x=x_axis[after_mask], y=rel_vals[after_mask], mode="lines",
                line=dict(width=1, color="rgba(150,150,150,0.2)"), showlegend=False,
                hoverinfo="skip", legendgroup="Périodes", name="Périodes historiques"))
            all_rel_vals.append((x_axis, rel_vals))
    if all_rel_vals:
        all_x = np.concatenate([v[0] for v in all_rel_vals])
        x_range = np.arange(int(min(all_x)), int(max(all_x)) + 1)
        mean_curve = np.nanmean([np.interp(x_range, x_ax, v_ax, left=np.nan, right=np.nan) for x_ax, v_ax in all_rel_vals], axis=0)
        fig.add_trace(go.Scatter(x=x_range, y=mean_curve, mode="lines", name="<b>MOYENNE HIST.</b>",
            line=dict(width=4, color="black"), hovertemplate="<b>MOYENNE</b>: %{y:.2f} bps<extra></extra>",
            legendgroup="Moyenne", showlegend=True))
    all_tickvals = list(range(-margin, max_core_length + margin))
    all_ticktext = [f"t{x}" if x < 0 else (str(x) if x < max_core_length else (f"t+{x-max_core_length+1}" if x < max_core_length+margin else "")) for x in all_tickvals]
    fig.update_layout(title=f"Contextual Seasonality: {asset_name}",
        xaxis=dict(title="Jours", showgrid=False, tickmode="array", tickvals=all_tickvals, ticktext=all_ticktext),
        yaxis=dict(title="Variation (bps)", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        template="plotly_white", height=700, hovermode="closest", showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5, font=dict(size=10), traceorder="reversed"),
        margin=dict(b=100))
    for x in list(range(-margin, 0)) + [0, max_core_length - 1] + list(range(max_core_length, max_core_length + margin)):
        fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=1, yref="paper",
            line=dict(color="rgba(0,0,0,0.1)", width=1), layer="below")
    return fig


def plot_heatmap(df, asset_name, horizon, window, lookback_years, selected_months=None, custom_start=None, custom_end=None):
    show_monthly_heatmap = (horizon == "Month" and selected_months and "All" in selected_months)
    if show_monthly_heatmap:
        base_periods = get_periods_to_analyze(df, horizon, lookback_years, window, selected_months)
        if len(base_periods) == 0: return None
        years = sorted(list(set([s.year for s, _, _ in base_periods])))
        col_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        heatmap_data = np.full((len(years), 12), np.nan)
        for start_date, _, p_data in base_periods:
            ext = extract_period_from_data(df, p_data, window)
            if ext is not None and asset_name in ext.columns:
                asset_data = ext[asset_name].dropna()
                if len(asset_data) >= 2:
                    heatmap_data[years.index(start_date.year), start_date.month - 1] = asset_data.iloc[-1] - asset_data.iloc[0]
        title_suffix = "by Month"
    else:
        use_first = "First" in window
        if horizon == "Month":
            if use_first:
                all_windows = ["First 2 days of month", "First 3 days of month", "First 4 days of month",
                    "First 6 days of month", "First 7 days of month", "First 8 days of month",
                    "First 9 days of month", "First week of month", "First two weeks of month"]
                col_labels = ["First 2d", "First 3d", "First 4d", "First 6d", "First 7d", "First 8d", "First 9d", "First 1w", "First 2w"]
            else:
                all_windows = ["Last 2 days of month", "Last 3 days of month", "Last 4 days of month",
                    "Last 6 days of month", "Last 7 days of month", "Last 8 days of month",
                    "Last 9 days of month", "Last week of month", "Last two weeks of month"]
                col_labels = ["Last 2d", "Last 3d", "Last 4d", "Last 6d", "Last 7d", "Last 8d", "Last 9d", "Last 1w", "Last 2w"]
        elif horizon in ["Quarter", "Semester", "Year"]:
            period = horizon.lower()
            if use_first:
                all_windows = [f"First 2 days of {period}", f"First 3 days of {period}", f"First 4 days of {period}",
                    f"First 6 days of {period}", f"First 7 days of {period}", f"First 8 days of {period}",
                    f"First 9 days of {period}", f"First week of {period}", f"First two weeks of {period}",
                    f"First three weeks of {period}", f"First four weeks of {period}"]
                col_labels = ["First 2d", "First 3d", "First 4d", "First 6d", "First 7d", "First 8d", "First 9d", "First 1w", "First 2w", "First 3w", "First 4w"]
            else:
                all_windows = [f"Last 2 days of {period}", f"Last 3 days of {period}", f"Last 4 days of {period}",
                    f"Last 6 days of {period}", f"Last 7 days of {period}", f"Last 8 days of {period}",
                    f"Last 9 days of {period}", f"Last week of {period}", f"Last two weeks of {period}",
                    f"Last three weeks of {period}", f"Last four weeks of {period}"]
                col_labels = ["Last 2d", "Last 3d", "Last 4d", "Last 6d", "Last 7d", "Last 8d", "Last 9d", "Last 1w", "Last 2w", "Last 3w", "Last 4w"]
        else:
            all_windows, col_labels = [window], ["Period"]
        if horizon != "Custom":
            base_periods = get_periods_to_analyze(df, horizon, lookback_years, all_windows[0], selected_months)
        else:
            base_periods = []
            if custom_start and custom_end:
                current_date = df.index.max()
                for year in range(df.index.min().year, df.index.max().year + 1):
                    try:
                        start_date = pd.Timestamp(year=year, month=custom_start.month, day=custom_start.day)
                        end_date = pd.Timestamp(year=year, month=custom_end.month, day=custom_end.day)
                        if (current_date - end_date).days <= 365 * lookback_years or (current_date >= start_date and current_date <= end_date):
                            period_data = df[(df.index >= start_date) & (df.index <= end_date)]
                            if len(period_data) > 0: base_periods.append((start_date, end_date, period_data))
                    except Exception: continue
        if len(base_periods) == 0: return None
        years = sorted(list(set([s.year for s, _, _ in base_periods])))
        heatmap_data = np.full((len(years), len(all_windows)), np.nan)
        for window_idx, current_window in enumerate(all_windows):
            for start_date, _, p_data in base_periods:
                ext = p_data if horizon == "Custom" else extract_period_from_data(df, p_data, current_window)
                if ext is not None and asset_name in ext.columns:
                    asset_data = ext[asset_name].dropna()
                    if len(asset_data) >= 2:
                        heatmap_data[years.index(start_date.year), window_idx] = asset_data.iloc[-1] - asset_data.iloc[0]
        title_suffix = "Progressive Windows"
    avg_row = np.nanmean(heatmap_data, axis=0)
    combined_data = np.vstack([avg_row, heatmap_data])
    combined_labels = ["Average"] + [str(y) for y in years]
    combined_text = [[f"{v:.2f}" if not np.isnan(v) else "" for v in avg_row]]
    combined_text.extend([[f"{v:.2f}" if not np.isnan(v) else "" for v in row] for row in heatmap_data])
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=combined_data, x=col_labels, y=combined_labels,
        colorscale=[[0, "rgb(220,30,30)"], [0.5, "rgb(255,255,255)"], [1, "rgb(0,180,50)"]],
        zmid=0, text=combined_text, texttemplate="%{text}", textfont={"size": 11, "color": "black"},
        colorbar=dict(title=dict(text="Variation (bps)", side="right"), tickmode="linear", tick0=0, dtick=10),
        hovertemplate="<b>%{y} - %{x}</b><br>%{z:.2f} bps<extra></extra>"))
    fig.update_layout(title=f"Seasonality Heatmap: {asset_name} ({title_suffix})",
        xaxis=dict(title="Window" if not show_monthly_heatmap else "Month", side="bottom"),
        yaxis=dict(title="", autorange="reversed"), template="plotly_white",
        height=400 + len(years) * 30, margin=dict(l=80, r=80, t=80, b=80))
    return fig


# ========== CSS SIDEBAR DARK CAVENTOR ==========
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #0a1628 !important;
    border-right: 1px solid #1a3a5c !important;
    padding: 2rem 1rem !important;
}
section[data-testid="stSidebar"] * { color: #e8f4fd !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #7a9cc0 !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] label p { color: #7a9cc0 !important; font-weight: 500 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background-color: #00aaff !important; color: #0a1628 !important;
    border: none !important; border-radius: 3px !important;
    font-size: 0.82rem !important; font-weight: 700 !important;
    letter-spacing: 1px !important; text-transform: uppercase !important;
    width: 100% !important; padding: 0.5rem !important;
    box-shadow: none !important; height: auto !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #33bbff !important; box-shadow: 0 0 10px rgba(0,170,255,0.4) !important;
}
div[data-baseweb="select"] > div {
    background-color: #0f2040 !important; color: #e8f4fd !important;
    border-radius: 3px !important; border: 1px solid #1a3a5c !important;
}
.stSelectbox div[role="listbox"] div, .stMultiSelect div[role="listbox"] div {
    color: #e8f4fd !important; background-color: #0f2040 !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background-color: #00aaff !important; color: #0a1628 !important;
    border-radius: 3px !important; border: none !important; padding: 2px 6px !important;
}
.stMultiSelect [data-baseweb="tag"] span { color: #0a1628 !important; font-weight: 600 !important; }
.stMultiSelect [data-baseweb="tag"] svg { fill: #0a1628 !important; color: #0a1628 !important; }
div[data-baseweb="select"] svg { color: #7a9cc0 !important; fill: #7a9cc0 !important; }
[data-testid="stTooltipIcon"] svg { color: #00aaff !important; fill: #00aaff !important; }
</style>
""", unsafe_allow_html=True)


def main():
    df, categories_map = load_data()
    if df.empty:
        st.warning("No data could be loaded. Please check the file path.")
        return

    with st.sidebar:
        st.header("Analysis Parameters")
        horizon = st.selectbox("Horizon", ["Month", "Quarter", "Semester", "Year", "Custom"],
                               help="Select the analysis period")
        selected_months = None
        if horizon == "Month":
            month_options = ["All", "January", "February", "March", "April", "May", "June",
                             "July", "August", "September", "October", "November", "December"]
            selected_months = st.multiselect("Which ones?", options=month_options, default=["All"])
            if "All" in selected_months and len(selected_months) > 1:
                selected_months = ["All"]
                st.warning("'All' selected - other month selections ignored")
            if not selected_months:
                selected_months = ["All"]
        windows = get_available_windows(horizon)
        window = st.selectbox("Window", windows, help="Select the time window")
        custom_start, custom_end = None, None
        if horizon == "Custom":
            col1, col2 = st.columns(2)
            with col1: custom_start = st.date_input("Start date")
            with col2: custom_end = st.date_input("End date")
        lookback = st.selectbox("Lookback", ["6m", "1y", "2y", "3y", "4y", "5y", "7y", "10y", "12y", "15y"],
                                index=2, help="Historical depth")
        sort_by = st.selectbox("Sort by", ["Gain (bp)", "Success Rate (%)", "G/L Ratio Bull", "G/L Ratio Bear"],
                               index=0)
        st.markdown("---")
        st.header("Big Picture")
        bp_timeframe = st.selectbox("Timeframe", ["Weekly", "Monthly", "Quarterly"])
        st.markdown("---")
        st.header("Asset Selection")
        unique_categories = sorted([c for c in set(categories_map.values()) if c != "Unknown"])
        select_by_category = st.checkbox("Filter by category")
        if select_by_category:
            selected_categories = st.multiselect("Categories", options=unique_categories, default=[])
            if selected_categories:
                filtered_assets = [a for a in df.columns if categories_map.get(a) in selected_categories]
                st.info(f"{len(filtered_assets)} assets in selected categories")
            else:
                filtered_assets = list(df.columns)
                st.warning("No category selected — showing all assets")
            select_all = st.checkbox("Select all from selected categories")
            selected_assets = filtered_assets if select_all else st.multiselect("Assets", filtered_assets,
                default=filtered_assets[:5] if len(filtered_assets) > 5 else filtered_assets)
        else:
            available_assets = list(df.columns)
            select_all = st.checkbox("Select all assets")
            selected_assets = available_assets if select_all else st.multiselect("Assets", available_assets,
                default=available_assets[:5] if len(available_assets) > 5 else available_assets)
        run_analysis = st.button("Run Analysis", type="primary", use_container_width=True)
        if st.session_state.seas_analysis_done:
            if st.button("Reset", use_container_width=True):
                st.session_state.seas_analysis_done = False
                st.session_state.seas_results_df = None
                st.session_state.seas_analysis_params = {}
                st.rerun()

    if run_analysis:
        if not selected_assets:
            st.warning("Please select at least one asset.")
            return
        st.session_state.seas_analysis_done = True
        st.session_state.seas_analysis_params = {
            "horizon": horizon, "window": window, "lookback": lookback,
            "selected_assets": selected_assets, "selected_months": selected_months,
            "custom_start": custom_start, "custom_end": custom_end,
            "sort_by": sort_by, "bp_timeframe": bp_timeframe
        }
        with st.spinner("Analysis in progress..."):
            lookback_years = 0.5 if lookback.startswith("6") else int(lookback.replace("y", ""))
            results = []
            for asset in selected_assets:
                if horizon != "Custom":
                    periods = get_periods_to_analyze(df, horizon, lookback_years, window, selected_months)
                    filtered_periods = [p for p in [extract_period_from_data(df, pd_data, window) for _, _, pd_data in periods] if p is not None]
                else:
                    filtered_periods = []
                    if custom_start and custom_end:
                        current_date = df.index.max()
                        for year in range(df.index.min().year, df.index.max().year + 1):
                            try:
                                start_date = pd.Timestamp(year=year, month=custom_start.month, day=custom_start.day)
                                end_date = pd.Timestamp(year=year, month=custom_end.month, day=custom_end.day)
                                if (current_date - end_date).days <= 365 * lookback_years or (current_date >= start_date and current_date <= end_date):
                                    period_data = df[(df.index >= start_date) & (df.index <= end_date)]
                                    if len(period_data) > 0: filtered_periods.append(period_data)
                            except Exception: continue
                if not filtered_periods: continue
                perf = calculate_performance(filtered_periods, asset)
                if perf:
                    perf["Asset"] = asset
                    if asset in df.columns: perf["Last Level"] = round(df[asset].dropna().iloc[-1], 2)
                    perf["Horizon"] = horizon; perf["Window"] = window; perf["Lookback"] = lookback
                    results.append(perf)
            if results: st.session_state.seas_results_df = pd.DataFrame(results)

    if st.session_state.seas_analysis_done and st.session_state.seas_results_df is not None:
        results_df = st.session_state.seas_results_df
        params = st.session_state.seas_analysis_params
        sort_criterion = params.get("sort_by", "Gain (bp)")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🐂 Top 15 Bull/Pay/Steepener")
            top_bulls = results_df.sort_values("Gain (bp)" if sort_criterion == "Gain (bp)" else sort_criterion,
                                               ascending=False).head(15).copy()
            top_bulls.insert(0, "Rank", range(1, len(top_bulls) + 1))
            st.dataframe(top_bulls[["Rank", "Asset", "Horizon", "Window", "Lookback",
                "Gain (bp)", "Success Rate (%)", "G/L Ratio Bull", "Nb observations", "Last Level"]],
                use_container_width=True, hide_index=True)
        with col2:
            st.subheader("🐻 Top 15 Bear/Rec/Flattener")
            if sort_criterion == "Gain (bp)":
                top_bears = results_df.sort_values("Gain (bp)", ascending=True).head(15).copy()
            elif sort_criterion == "Success Rate (%)":
                top_bears = results_df.sort_values("Success Rate (%)", ascending=True).head(15).copy()
            else:
                top_bears = results_df.sort_values("G/L Ratio Bear", ascending=False).head(15).copy()
            top_bears.insert(0, "Rank", range(1, len(top_bears) + 1))
            top_bears["Gain (bp)"] = -top_bears["Gain (bp)"]
            top_bears["Success Rate (%)"] = 100 - top_bears["Success Rate (%)"]
            st.dataframe(top_bears[["Rank", "Asset", "Horizon", "Window", "Lookback",
                "Gain (bp)", "Success Rate (%)", "G/L Ratio Bear", "Nb observations", "Last Level"]],
                use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📊 Detailed Historical Analysis")
        assets_to_plot = st.multiselect("Select assets to visualize in detail:",
            options=results_df["Asset"].tolist(),
            default=results_df.nlargest(1, "Gain (bp)")["Asset"].tolist(),
            key="spaghetti_assets")

        if assets_to_plot:
            lookback_years = 0.5 if params['lookback'].startswith("6") else int(params['lookback'].replace("y", ""))
            bp_tf = params.get("bp_timeframe", "Monthly")
            for asset in assets_to_plot:
                st.markdown(f"### {asset}")
                fig_spaghetti = plot_spaghetti(df, asset, params["horizon"], params["window"], lookback_years,
                    selected_months=params.get("selected_months"), custom_start=params.get("custom_start"),
                    custom_end=params.get("custom_end"))
                if fig_spaghetti: st.plotly_chart(fig_spaghetti, use_container_width=True)
                else: st.warning(f"Unable to generate spaghetti chart for {asset}")

                if params["horizon"] != "Custom":
                    periods_for_stats = get_periods_to_analyze(df, params["horizon"], lookback_years,
                                                               params["window"], params.get("selected_months"))
                    filtered_periods_for_stats = [p for p in [extract_period_from_data(df, pd_data, params["window"])
                                                  for _, _, pd_data in periods_for_stats] if p is not None]
                else:
                    filtered_periods_for_stats = []
                    if params.get("custom_start") and params.get("custom_end"):
                        current_date = df.index.max()
                        for year in range(df.index.min().year, df.index.max().year + 1):
                            try:
                                start_date = pd.Timestamp(year=year, month=params["custom_start"].month, day=params["custom_start"].day)
                                end_date = pd.Timestamp(year=year, month=params["custom_end"].month, day=params["custom_end"].day)
                                if (current_date - end_date).days <= 365 * lookback_years or (current_date >= start_date and current_date <= end_date):
                                    period_data = df[(df.index >= start_date) & (df.index <= end_date)]
                                    if len(period_data) > 0: filtered_periods_for_stats.append(period_data)
                            except Exception: continue

                if filtered_periods_for_stats:
                    perf = calculate_performance(filtered_periods_for_stats, asset)
                    if perf:
                        perf["Last Level"] = round(df[asset].dropna().iloc[-1], 2) if asset in df.columns else 0
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("#### 🐂 Bull/Pay/Steepener")
                            st.dataframe(pd.DataFrame([{"Gain (bp)": perf["Gain (bp)"],
                                "Success Rate (%)": perf["Success Rate (%)"], "G/L Ratio Bull": perf["G/L Ratio Bull"],
                                "Nb observations": perf["Nb observations"], "Last Level": perf["Last Level"]}]),
                                use_container_width=True, hide_index=True)
                        with c2:
                            st.markdown("#### 🐻 Bear/Rec/Flattener")
                            st.dataframe(pd.DataFrame([{"Gain (bp)": -perf["Gain (bp)"],
                                "Success Rate (%)": 100 - perf["Success Rate (%)"], "G/L Ratio Bear": perf["G/L Ratio Bear"],
                                "Nb observations": perf["Nb observations"], "Last Level": perf["Last Level"]}]),
                                use_container_width=True, hide_index=True)

                fig_heatmap = plot_heatmap(df, asset, params["horizon"], params["window"], lookback_years,
                    selected_months=params.get("selected_months"), custom_start=params.get("custom_start"),
                    custom_end=params.get("custom_end"))
                if fig_heatmap: st.plotly_chart(fig_heatmap, use_container_width=True)
                else: st.warning(f"Unable to generate heatmap for {asset}")

                fig_bp = plot_big_picture_heatmap(df, asset, lookback_years, bp_tf)
                if fig_bp: st.plotly_chart(fig_bp, use_container_width=True)
                else: st.warning(f"Unable to generate Big Picture heatmap for {asset}")
                st.markdown("---")

    elif not st.session_state.seas_analysis_done:
        st.info("""
👋 Welcome to the Seasonality Analysis Tool!

- 🎯 Select your parameters in the sidebar
- 📊 Choose the assets to analyze (by category or individually)
- 🚀 Launch the analysis to discover the best opportunities
""")


main()
