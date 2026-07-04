# -*- coding: utf-8 -*-
"""
Финальный проект DA — интерактивный дашборд.
Запуск: python dashboard/app.py
Откроется на http://127.0.0.1:8055
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from pathlib import Path

# ================================================================
# ЗАГРУЗКА ДАННЫХ
# ================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data_clean'

deals = pd.read_csv(DATA_DIR / 'deals_clean.csv', low_memory=False,
                    dtype={'Id': str, 'Contact Name': str})
calls = pd.read_csv(DATA_DIR / 'calls_clean.csv', low_memory=False,
                    dtype={'Id': str, 'CONTACTID': str})
spend = pd.read_csv(DATA_DIR / 'spend_clean.csv', low_memory=False)

# Конвертируем даты
deals['Created Time'] = pd.to_datetime(deals['Created Time'])
deals['Closing Date'] = pd.to_datetime(deals['Closing Date'], errors='coerce')
calls['Call Start Time'] = pd.to_datetime(calls['Call Start Time'])
spend['Date'] = pd.to_datetime(spend['Date'])

# Реальные сделки — исключаем демо-доступы за символическую плату (0, 1, 9 €)
deals_real = deals[~deals['Initial Amount Paid'].isin([0, 1, 9])].copy()

# Временные признаки
deals['Month'] = deals['Created Time'].dt.to_period('M').dt.to_timestamp()

# ================================================================
# ЮНИТ-ЭКОНОМИКА — локальная демонстрация из CSV.
# Финальная unit economics считается в Google Sheets; здесь показываем первый платёж,
# а не полную признанную выручку.
# ================================================================
def _agg_unit(df, group_col):
    base = (df.groupby(group_col, observed=True)
            .apply(lambda x: pd.Series({
                'Leads': len(x),
                'Paid': ((x['Stage'] == 'Payment Done') & x['Initial Amount Paid'].notna()).sum(),
                'First Payment Amount': x.loc[(x['Stage'] == 'Payment Done')
                                 & x['Initial Amount Paid'].notna(),
                                 'Initial Amount Paid'].sum(),
            }), include_groups=False)
            .reset_index())
    base['C1 %'] = (base['Paid'] / base['Leads'] * 100).round(2)
    return base


# По каналам (Source)
ue_channels = _agg_unit(deals_real, 'Source')
_spend_src = (spend.groupby('Source', observed=True)['Spend'].sum()
              .reset_index().rename(columns={'Spend': 'Total Spend'}))
ue_channels = ue_channels.merge(_spend_src, on='Source', how='left')
ue_channels['Total Spend'] = ue_channels['Total Spend'].fillna(0)
ue_channels['CAC'] = np.where(ue_channels['Paid'] > 0,
                              (ue_channels['Total Spend'] / ue_channels['Paid']).round(2), np.nan)
ue_channels['Avg First Payment'] = np.where(ue_channels['Paid'] > 0,
                                (ue_channels['First Payment Amount'] / ue_channels['Paid']).round(2), np.nan)
ue_channels['First Payment Return'] = np.where(ue_channels['Total Spend'] > 0,
                               (ue_channels['First Payment Amount'] / ue_channels['Total Spend']).round(2), np.nan)
ue_channels = ue_channels.sort_values('Leads', ascending=False)

# По продуктам (Product) — Avg First Payment как медианный чек
_wp = deals_real[deals_real['Product'].notna()]
ue_products = _agg_unit(_wp, 'Product')
_prod_arppu = (_wp[_wp['Stage'] == 'Payment Done']
               .groupby('Product', observed=True)['Initial Amount Paid'].median()
               .reset_index().rename(columns={'Initial Amount Paid': 'Avg First Payment'}))
ue_products = ue_products.merge(_prod_arppu, on='Product', how='left')

# KPI-скаляры (итоги по всем каналам)
total_leads   = len(deals_real)
total_paid    = int(((deals_real['Stage'] == 'Payment Done') & deals_real['Initial Amount Paid'].notna()).sum())
conv_rate     = round(total_paid / total_leads * 100, 2) if total_leads else 0
total_spend   = float(spend['Spend'].sum())
total_first_payment = float(ue_channels['First Payment Amount'].sum())
cac           = total_spend / total_paid if total_paid else 0
first_payment_return          = total_first_payment / total_spend if total_spend else 0

# Менеджеры
manager_stats = (
    deals[deals['Deal Owner Name'].notna()]
    .groupby('Deal Owner Name')
    .apply(lambda x: pd.Series({
        'Сделок': len(x),
        'Оплат': ((x['Stage'] == 'Payment Done') & x['Initial Amount Paid'].notna()).sum(),
        'Конверсия': round(((x['Stage'] == 'Payment Done') & x['Initial Amount Paid'].notna()).sum() / len(x) * 100, 1),
        'Сумма первого платежа': x.loc[
            (x['Stage'] == 'Payment Done') &
            x['Initial Amount Paid'].notna() &
            (~x['Initial Amount Paid'].isin([0, 1, 9])),
            'Initial Amount Paid'
        ].sum()
    }), include_groups=False)
    .reset_index()
    .sort_values('Конверсия', ascending=False)
)

# Список месяцев для слайсера
months_sorted = sorted(deals['Month'].dropna().unique())
month_options = [{'label': m.strftime('%b %Y'), 'value': str(m)} for m in months_sorted]

# Список источников для фильтра
source_options = [{'label': s, 'value': s}
                  for s in sorted(deals['Source'].dropna().unique())]

# ================================================================
# ЦВЕТА И СТИЛЬ
# ================================================================
COLORS = {
    'bg':       '#0f1117',
    'card':     '#1a1d27',
    'accent':   '#4361ee',
    'green':    '#2ec4b6',
    'red':      '#e63946',
    'yellow':   '#f4a261',
    'text':     '#e0e0e0',
    'subtext':  '#9a9ab0',
    'border':   '#2a2d3e',
}

CARD_STYLE = {
    'backgroundColor': COLORS['card'],
    'border': f'1px solid {COLORS["border"]}',
    'borderRadius': '12px',
    'padding': '20px',
    'height': '100%',
}

PLOTLY_TEMPLATE = dict(
    paper_bgcolor=COLORS['card'],
    plot_bgcolor=COLORS['card'],
    font=dict(color=COLORS['text'], size=12),
    colorway=[COLORS['accent'], COLORS['green'], COLORS['yellow'],
              COLORS['red'], '#9d4edd', '#06d6a0'],
)

AXIS_STYLE = dict(gridcolor=COLORS['border'], zerolinecolor=COLORS['border'])


def make_fig(fig, margin=None):
    """Применяет единый тёмный стиль ко всем графикам."""
    fig.update_layout(**PLOTLY_TEMPLATE)
    fig.update_layout(margin=margin or dict(l=40, r=20, t=50, b=40))
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    return fig


def kpi_card(title, value, sub='', color=COLORS['accent']):
    """Карточка с одной KPI-метрикой."""
    return html.Div([
        html.P(title, style={'color': COLORS['subtext'], 'fontSize': '13px',
                             'marginBottom': '6px', 'textTransform': 'uppercase',
                             'letterSpacing': '0.5px'}),
        html.H3(value, style={'color': color, 'fontSize': '28px',
                               'fontWeight': '700', 'margin': '0'}),
        html.P(sub, style={'color': COLORS['subtext'], 'fontSize': '12px',
                           'marginTop': '4px'}) if sub else html.Div(),
    ], style=CARD_STYLE)


# ================================================================
# ВКЛАДКИ
# ================================================================

def tab_funnel():
    """Страница 1: Воронка и динамика."""

    # Динамика по месяцам
    monthly = deals.groupby('Month').size().reset_index(name='Лидов')
    monthly_paid = (deals[deals['Stage'] == 'Payment Done']
                    .groupby('Month').size().reset_index(name='Оплат'))
    monthly = monthly.merge(monthly_paid, on='Month', how='left').fillna(0)
    monthly['Конверсия %'] = (monthly['Оплат'] / monthly['Лидов'] * 100).round(1)

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=monthly['Month'], y=monthly['Лидов'],
        name='Лидов', marker_color=COLORS['accent'], opacity=0.6,
        yaxis='y'
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly['Month'], y=monthly['Конверсия %'],
        name='Конверсия %', mode='lines+markers',
        line=dict(color=COLORS['green'], width=2),
        yaxis='y2'
    ))
    fig_trend.update_layout(
        title=dict(text='Динамика лидов и конверсии по месяцам', y=0.95),
        yaxis=dict(title='Лидов', gridcolor=COLORS['border']),
        yaxis2=dict(title='Конверсия %', overlaying='y', side='right',
                    gridcolor='rgba(0,0,0,0)'),
        legend=dict(orientation='h', x=0, y=-0.2),
        barmode='overlay',
    )
    make_fig(fig_trend, margin=dict(l=40, r=40, t=50, b=60))

    # Воронка — только 6 ключевых стадий воронки продаж
    stage_counts = deals['Stage'].value_counts()
    funnel_order = ['Lost', 'Call Delayed', 'Registered on Webinar',
                    'Qualificated', 'Waiting For Payment', 'Payment Done']
    funnel_vals  = [stage_counts.get(s, 0) for s in funnel_order]
    funnel_colors = [COLORS['red'], COLORS['subtext'], '#6c757d',
                     COLORS['yellow'], COLORS['accent'], COLORS['green']]

    fig_funnel = go.Figure(go.Funnel(
        y=funnel_order,
        x=funnel_vals,
        textposition='inside',
        textinfo='value+percent total',
        marker=dict(color=funnel_colors),
        connector=dict(line=dict(color=COLORS['border'], width=1)),
    ))
    fig_funnel.update_layout(title='Воронка продаж (6 стадий)')
    make_fig(fig_funnel, margin=dict(l=10, r=10, t=50, b=20))

    return html.Div([
        # KPI-строка
        dbc.Row([
            dbc.Col(kpi_card('Лидов всего',   f'{total_leads:,}'), md=3),
            dbc.Col(kpi_card('Оплат',          f'{total_paid:,}', color=COLORS['green']), md=3),
            dbc.Col(kpi_card('Конверсия C1',   f'{conv_rate:.1f}%', color=COLORS['yellow']), md=3),
            dbc.Col(kpi_card('Первый платёж €',      f'{total_first_payment:,.0f}', color=COLORS['accent']), md=3),
        ], className='g-3 mb-4'),

        # Графики
        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_trend)), md=8),
            dbc.Col(dcc.Graph(figure=make_fig(fig_funnel)), md=4),
        ], className='g-3'),
    ])


def tab_marketing():
    """Страница 2: Маркетинг — CAC и First Payment Return."""

    # Числовые колонки — очистка (запятые → точки для локали)
    for col in ['CAC', 'First Payment Return', 'C1 %', 'Total Spend', 'First Payment Amount', 'Avg First Payment']:
        if col in ue_channels.columns:
            ue_channels[col] = (pd.to_numeric(
                ue_channels[col].astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            ))

    paid_ch = ue_channels[ue_channels['Total Spend'] > 0].dropna(subset=['CAC'])

    # CAC по каналам
    fig_cac = go.Figure(go.Bar(
        x=paid_ch.sort_values('CAC')['CAC'],
        y=paid_ch.sort_values('CAC')['Source'],
        orientation='h',
        marker=dict(
            color=paid_ch.sort_values('CAC')['CAC'],
            colorscale=[[0, COLORS['green']], [0.5, COLORS['yellow']],
                        [1, COLORS['red']]],
            showscale=False,
        ),
        text=paid_ch.sort_values('CAC')['CAC'].apply(lambda x: f'{x:.0f} €'),
        textposition='outside',
    ))
    fig_cac.update_layout(**PLOTLY_TEMPLATE, title='CAC по каналам (€)')

    # First Payment Return по каналам
    first_payment_return_ch = ue_channels[ue_channels['First Payment Return'].notna()].sort_values('First Payment Return', ascending=False)
    fig_first_payment_return = go.Figure(go.Bar(
        x=first_payment_return_ch['First Payment Return'],
        y=first_payment_return_ch['Source'],
        orientation='h',
        marker=dict(
            color=['#2ec4b6' if r >= 1 else '#e63946' for r in first_payment_return_ch['First Payment Return']]
        ),
        text=first_payment_return_ch['First Payment Return'].apply(lambda x: f'{x:.2f}x'),
        textposition='outside',
    ))
    fig_first_payment_return.add_vline(x=1, line_dash='dash', line_color='white',
                       annotation_text='безубыточность')
    fig_first_payment_return.update_layout(**PLOTLY_TEMPLATE, title='First Payment Return по каналам')

    # Таблица
    table_cols = ['Source', 'Leads', 'Paid', 'C1 %', 'Total Spend', 'CAC', 'Avg First Payment', 'First Payment Amount', 'First Payment Return']
    tbl = ue_channels[table_cols].sort_values('Leads', ascending=False)

    fig_table = go.Figure(go.Table(
        header=dict(
            values=table_cols,
            fill_color=COLORS['border'],
            font=dict(color=COLORS['text'], size=12),
            align='left',
        ),
        cells=dict(
            values=[tbl[c].tolist() for c in table_cols],
            fill_color=COLORS['card'],
            font=dict(color=COLORS['text'], size=11),
            align='left',
        )
    ))
    fig_table.update_layout(**PLOTLY_TEMPLATE, title='Юнит-экономика по каналам',
                            height=350)

    # CAC и First Payment Return по месяцам (из CSV: Spend по дате расхода,
    # оплаты/первый платёж по месяцу создания сделки — только Payment Done с суммой)
    dr = deals_real.copy()
    dr['Month'] = dr['Created Time'].dt.to_period('M').dt.to_timestamp()
    paid_dr = dr[(dr['Stage'] == 'Payment Done') & dr['Initial Amount Paid'].notna()]

    sp = spend.copy()
    sp['Month'] = sp['Date'].dt.to_period('M').dt.to_timestamp()

    mon = pd.DataFrame({
        'Spend':   sp.groupby('Month')['Spend'].sum(),
        'Оплат':   paid_dr.groupby('Month').size(),
        'Сумма первого платежа': paid_dr[paid_dr['Initial Amount Paid'].notna()]
                   .groupby('Month')['Initial Amount Paid'].sum(),
    }).fillna(0)
    mon['CAC']  = (mon['Spend'] / mon['Оплат']).replace([np.inf, -np.inf], np.nan).round(0)
    mon['First Payment Return'] = (mon['Сумма первого платежа'] / mon['Spend']).replace([np.inf, -np.inf], np.nan).round(2)
    mon = mon.reset_index()

    fig_ue_trend = go.Figure()
    fig_ue_trend.add_trace(go.Scatter(
        x=mon['Month'], y=mon['CAC'], name='CAC €',
        mode='lines+markers', line=dict(color=COLORS['yellow'], width=2), yaxis='y'
    ))
    fig_ue_trend.add_trace(go.Scatter(
        x=mon['Month'], y=mon['First Payment Return'], name='First Payment Return',
        mode='lines+markers', line=dict(color=COLORS['green'], width=2), yaxis='y2'
    ))
    fig_ue_trend.add_hline(y=1, line_dash='dash', line_color=COLORS['subtext'],
                           yref='y2')
    fig_ue_trend.update_layout(
        title=dict(text='CAC и First Payment Return по месяцам', y=0.95),
        yaxis=dict(title='CAC, €', gridcolor=COLORS['border']),
        yaxis2=dict(title='First Payment Return, x', overlaying='y', side='right',
                    gridcolor='rgba(0,0,0,0)'),
        legend=dict(orientation='h', x=0, y=-0.2),
    )
    make_fig(fig_ue_trend, margin=dict(l=40, r=40, t=50, b=60))

    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card('Расходы €',  f'{total_spend:,.0f}', color=COLORS['red']), md=3),
            dbc.Col(kpi_card('Первый платёж €',  f'{total_first_payment:,.0f}', color=COLORS['green']), md=3),
            dbc.Col(kpi_card('CAC €',      f'{cac:,.0f}', color=COLORS['yellow']), md=3),
            dbc.Col(kpi_card('First Payment Return',       f'{first_payment_return:.2f}x', color=COLORS['accent']), md=3),
        ], className='g-3 mb-4'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_ue_trend)), md=12),
        ], className='g-3 mb-3'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_cac)), md=6),
            dbc.Col(dcc.Graph(figure=make_fig(fig_first_payment_return)), md=6),
        ], className='g-3 mb-3'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_table), md=12),
        ], className='g-3'),
    ])


def tab_sales():
    """Страница 3: Менеджеры по продажам."""

    active = manager_stats[manager_stats['Сделок'] >= 50].copy()

    fig_conv = go.Figure(go.Bar(
        x=active.sort_values('Конверсия')['Конверсия'],
        y=active.sort_values('Конверсия')['Deal Owner Name'],
        orientation='h',
        marker=dict(
            color=active.sort_values('Конверсия')['Конверсия'],
            colorscale=[[0, COLORS['red']], [0.5, COLORS['yellow']],
                        [1, COLORS['green']]],
        ),
        text=active.sort_values('Конверсия')['Конверсия'].apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
    ))
    fig_conv.update_layout(**PLOTLY_TEMPLATE,
                           title='Конверсия менеджеров в оплату, % (≥ 50 сделок)')

    fig_rev = go.Figure(go.Bar(
        x=active.sort_values('Сумма первого платежа', ascending=False)['Deal Owner Name'],
        y=active.sort_values('Сумма первого платежа', ascending=False)['Сумма первого платежа'],
        marker_color=COLORS['accent'],
        text=active.sort_values('Сумма первого платежа', ascending=False)['Сумма первого платежа']
            .apply(lambda x: f'{x:,.0f}'),
        textposition='outside',
    ))
    fig_rev.update_layout(**PLOTLY_TEMPLATE, title='Сумма первого платежа по менеджерам, €')

    # Скаттер: Сделок vs Конверсия
    fig_scatter = px.scatter(
        active,
        x='Сделок', y='Конверсия',
        size='Сумма первого платежа', color='Сумма первого платежа',
        color_continuous_scale=['#e63946', '#f4a261', '#2ec4b6'],
        hover_name='Deal Owner Name',
        text='Deal Owner Name',
        title='Менеджеры: объём vs конверсия (размер = выручка)',
    )
    fig_scatter.update_traces(textposition='top center', textfont_size=9)
    fig_scatter.update_layout(**PLOTLY_TEMPLATE)

    best = active.nlargest(1, 'Конверсия').iloc[0]
    worst = active.nsmallest(1, 'Конверсия').iloc[0]

    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card('Менеджеров', str(len(manager_stats))), md=3),
            dbc.Col(kpi_card('Лучший', f'{best["Deal Owner Name"]}',
                             f'{best["Конверсия"]:.1f}% конверсия',
                             color=COLORS['green']), md=3),
            dbc.Col(kpi_card('Нужна помощь', f'{worst["Deal Owner Name"]}',
                             f'{worst["Конверсия"]:.1f}% конверсия',
                             color=COLORS['red']), md=3),
            dbc.Col(kpi_card('Первый платёж €', f'{active["Сумма первого платежа"].sum():,.0f}',
                             color=COLORS['accent']), md=3),
        ], className='g-3 mb-4'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_conv)), md=7),
            dbc.Col(dcc.Graph(figure=make_fig(fig_scatter)), md=5),
        ], className='g-3 mb-3'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_rev)), md=12),
        ], className='g-3'),
    ])


def tab_products():
    """Страница 4: Продукты и юнит-экономика."""

    for col in ['C1 %', 'First Payment Amount', 'Avg First Payment', 'Leads', 'Paid']:
        if col in ue_products.columns:
            ue_products[col] = pd.to_numeric(
                ue_products[col].astype(str).str.replace(',', '.', regex=False),
                errors='coerce'
            )

    fig_c1 = go.Figure(go.Bar(
        x=ue_products.sort_values('C1 %', ascending=False)['Product'],
        y=ue_products.sort_values('C1 %', ascending=False)['C1 %'],
        marker_color=COLORS['green'],
        text=ue_products.sort_values('C1 %', ascending=False)['C1 %']
            .apply(lambda x: f'{x:.1f}%'),
        textposition='outside',
    ))
    fig_c1.update_layout(**PLOTLY_TEMPLATE, title='Конверсия по продуктам, %')

    fig_arppu = go.Figure(go.Bar(
        x=ue_products.sort_values('Avg First Payment', ascending=False)['Product'],
        y=ue_products.sort_values('Avg First Payment', ascending=False)['Avg First Payment'],
        marker_color=COLORS['yellow'],
        text=ue_products.sort_values('Avg First Payment', ascending=False)['Avg First Payment']
            .apply(lambda x: f'{x:,.0f} €'),
        textposition='outside',
    ))
    fig_arppu.update_layout(**PLOTLY_TEMPLATE, title='Медианный первый платёж, €')

    fig_pie = go.Figure(go.Pie(
        labels=ue_products['Product'],
        values=ue_products['First Payment Amount'],
        hole=0.45,
        marker=dict(colors=[COLORS['accent'], COLORS['green'],
                             COLORS['yellow'], COLORS['red'], '#9d4edd']),
        textinfo='label+percent',
    ))
    fig_pie.update_layout(**PLOTLY_TEMPLATE, title='Доля первого платежа по продуктам',
                          showlegend=False)

    # Lost Reason
    lost = deals[deals['Stage'] == 'Lost']['Lost Reason'].value_counts().head(8)
    fig_lost = go.Figure(go.Bar(
        x=lost.values[::-1],
        y=lost.index[::-1],
        orientation='h',
        marker_color=COLORS['red'],
        text=lost.values[::-1],
        textposition='outside',
    ))
    fig_lost.update_layout(**PLOTLY_TEMPLATE, title='Топ причин потери сделок')

    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card('Продуктов', str(len(ue_products))), md=3),
            dbc.Col(kpi_card('Лучший продукт',
                             ue_products.nlargest(1, 'C1 %')['Product'].iloc[0],
                             f'{ue_products["C1 %"].max():.1f}% конверсия',
                             color=COLORS['green']), md=3),
            dbc.Col(kpi_card('Сумма первого платежа лидера',
                             f'{ue_products["First Payment Amount"].max():,.0f} €',
                             ue_products.nlargest(1, 'First Payment Amount')['Product'].iloc[0],
                             color=COLORS['accent']), md=3),
            dbc.Col(kpi_card('Средний первый платёж',
                             f'{ue_products["Avg First Payment"].mean():,.0f} €',
                             color=COLORS['yellow']), md=3),
        ], className='g-3 mb-4'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_c1)), md=6),
            dbc.Col(dcc.Graph(figure=make_fig(fig_arppu)), md=6),
        ], className='g-3 mb-3'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_pie)), md=5),
            dbc.Col(dcc.Graph(figure=make_fig(fig_lost)), md=7),
        ], className='g-3'),
    ])


# ================================================================
# LAYOUT
# ================================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title='CRM Analytics Dashboard',
)

app.layout = html.Div(
    style={'backgroundColor': COLORS['bg'], 'minHeight': '100vh',
           'padding': '20px', 'fontFamily': 'Inter, Segoe UI, sans-serif'},
    children=[
        # Заголовок
        html.Div([
            html.H2('CRM Analytics Dashboard',
                    style={'color': COLORS['text'], 'fontWeight': '700',
                           'marginBottom': '4px'}),
            html.P('Онлайн-школа программирования X · Июль 2023 – Июнь 2024',
                   style={'color': COLORS['subtext'], 'marginBottom': '20px'}),
        ]),

        # Вкладки — контент рендерится сразу, без callback
        dbc.Tabs(
            children=[
                dbc.Tab(
                    label='Воронка и динамика',
                    children=tab_funnel(),
                    label_style={'color': COLORS['subtext']},
                    active_label_style={'color': COLORS['accent']},
                ),
                dbc.Tab(
                    label='Маркетинг (CAC / First Payment Return)',
                    children=tab_marketing(),
                    label_style={'color': COLORS['subtext']},
                    active_label_style={'color': COLORS['accent']},
                ),
                dbc.Tab(
                    label='Менеджеры по продажам',
                    children=tab_sales(),
                    label_style={'color': COLORS['subtext']},
                    active_label_style={'color': COLORS['accent']},
                ),
                dbc.Tab(
                    label='Продукты и юнит-экономика',
                    children=tab_products(),
                    label_style={'color': COLORS['subtext']},
                    active_label_style={'color': COLORS['accent']},
                ),
            ],
            style={'marginBottom': '24px'},
        ),
    ]
)


# Expose Flask server for Vercel (WSGI entry point)
server = app.server

if __name__ == '__main__':
    app.run(debug=True, port=8055)
