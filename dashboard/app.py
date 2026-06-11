# -*- coding: utf-8 -*-
"""
Финальный проект DA — интерактивный дашборд.
Запуск: python dashboard/app.py
Откроется на http://127.0.0.1:8050
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# ================================================================
# ЗАГРУЗКА ДАННЫХ
# ================================================================
DATA = '../data_clean/'

GS_CHANNELS = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vR1z7RIwAVG7fBZyEpHeKOrPpE7BPXDnGgbmMX49CJwedF5IYavchKrpedTUEn9X-UClq67HpiLjkRU'
    '/pub?gid=1215376088&single=true&output=csv'
)
GS_PRODUCTS = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vR1z7RIwAVG7fBZyEpHeKOrPpE7BPXDnGgbmMX49CJwedF5IYavchKrpedTUEn9X-UClq67HpiLjkRU'
    '/pub?gid=2057863604&single=true&output=csv'
)
GS_KPI = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vR1z7RIwAVG7fBZyEpHeKOrPpE7BPXDnGgbmMX49CJwedF5IYavchKrpedTUEn9X-UClq67HpiLjkRU'
    '/pub?gid=1640872499&single=true&output=csv'
)

deals = pd.read_csv(DATA + 'deals_clean.csv', low_memory=False)
calls = pd.read_csv(DATA + 'calls_clean.csv', low_memory=False)
spend = pd.read_csv(DATA + 'spend_clean.csv', low_memory=False)
ue_channels = pd.read_csv(GS_CHANNELS)
ue_products = pd.read_csv(GS_PRODUCTS)
ue_kpi = pd.read_csv(GS_KPI)

# Конвертируем даты
deals['Created Time'] = pd.to_datetime(deals['Created Time'])
deals['Closing Date'] = pd.to_datetime(deals['Closing Date'], errors='coerce')
calls['Call Start Time'] = pd.to_datetime(calls['Call Start Time'])
spend['Date'] = pd.to_datetime(spend['Date'])

deals_real = deals[deals['Is Demo'] == False].copy()

# Временные признаки
deals['Month'] = deals['Created Time'].dt.to_period('M').dt.to_timestamp()

# Менеджеры
manager_stats = (
    deals[deals['Deal Owner Name'].notna()]
    .groupby('Deal Owner Name')
    .apply(lambda x: pd.Series({
        'Сделок': len(x),
        'Оплат': (x['Stage'] == 'Payment Done').sum(),
        'Конверсия': round((x['Stage'] == 'Payment Done').sum() / len(x) * 100, 1),
        'Выручка': x.loc[
            (x['Stage'] == 'Payment Done') &
            x['Initial Amount Paid'].notna() &
            (x['Is Demo'] == False),
            'Initial Amount Paid'
        ].sum()
    }), include_groups=False)
    .reset_index()
    .sort_values('Конверсия', ascending=False)
)

# KPI из Google Sheets
kpi_dict = dict(zip(ue_kpi['Метрика'], ue_kpi['Значение']))


def to_num(val, default=0):
    """Конвертирует значение из Sheets (запятая как десятичный разделитель)."""
    try:
        return float(str(val).replace(',', '.').replace(' ', ''))
    except (ValueError, TypeError):
        return default


# Числа для KPI-карточек
total_leads   = int(to_num(kpi_dict.get('Лидов всего', 0)))
total_paid    = int(to_num(kpi_dict.get('Оплат всего', 0)))
conv_rate     = to_num(kpi_dict.get('Конверсия C1 %', 0))
total_spend   = to_num(kpi_dict.get('Расходы € (итого)', 0))
total_revenue = to_num(kpi_dict.get('Выручка € (итого)', 0))
cac           = to_num(kpi_dict.get('CAC € (средний)', 0))
roas          = to_num(kpi_dict.get('ROAS (общий)', 0))

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
    xaxis=dict(gridcolor=COLORS['border'], zerolinecolor=COLORS['border']),
    yaxis=dict(gridcolor=COLORS['border'], zerolinecolor=COLORS['border']),
    colorway=[COLORS['accent'], COLORS['green'], COLORS['yellow'],
              COLORS['red'], '#9d4edd', '#06d6a0'],
    margin=dict(l=40, r=20, t=40, b=40),
)


def make_fig(fig):
    """Применяет единый тёмный стиль ко всем графикам."""
    fig.update_layout(**PLOTLY_TEMPLATE)
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
        **PLOTLY_TEMPLATE,
        title='Динамика лидов и конверсии по месяцам',
        yaxis=dict(title='Лидов', gridcolor=COLORS['border']),
        yaxis2=dict(title='Конверсия %', overlaying='y', side='right',
                    gridcolor='rgba(0,0,0,0)'),
        legend=dict(orientation='h', y=1.1),
        barmode='overlay',
    )

    # Воронка по стадиям
    stage_counts = deals['Stage'].value_counts()
    funnel_order = ['Payment Done', 'Waiting For Payment', 'Qualificated',
                    'Registered on Webinar', 'Call Delayed', 'Lost']
    funnel_data = [(s, stage_counts.get(s, 0)) for s in funnel_order
                   if stage_counts.get(s, 0) > 0]
    funnel_data += [(s, v) for s, v in stage_counts.items()
                    if s not in funnel_order]
    funnel_df = pd.DataFrame(funnel_data, columns=['Stage', 'Count'])

    fig_funnel = go.Figure(go.Funnel(
        y=funnel_df['Stage'],
        x=funnel_df['Count'],
        textposition='inside',
        textinfo='value+percent initial',
        marker=dict(color=[COLORS['green'], COLORS['accent'], COLORS['yellow'],
                           COLORS['yellow'], COLORS['subtext'], COLORS['red']
                           ][:len(funnel_df)])
    ))
    fig_funnel.update_layout(**PLOTLY_TEMPLATE, title='Воронка продаж')

    return html.Div([
        # KPI-строка
        dbc.Row([
            dbc.Col(kpi_card('Лидов всего',   f'{total_leads:,}'), md=3),
            dbc.Col(kpi_card('Оплат',          f'{total_paid:,}', color=COLORS['green']), md=3),
            dbc.Col(kpi_card('Конверсия C1',   f'{conv_rate:.1f}%', color=COLORS['yellow']), md=3),
            dbc.Col(kpi_card('Выручка €',      f'{total_revenue:,.0f}', color=COLORS['accent']), md=3),
        ], className='g-3 mb-4'),

        # Графики
        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_trend)), md=8),
            dbc.Col(dcc.Graph(figure=make_fig(fig_funnel)), md=4),
        ], className='g-3'),
    ])


def tab_marketing():
    """Страница 2: Маркетинг — CAC и ROAS."""

    # Числовые колонки — очистка (запятые → точки для локали)
    for col in ['CAC', 'ROAS', 'C1 %', 'Total Spend', 'Revenue', 'ARPPU']:
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

    # ROAS по каналам
    roas_ch = ue_channels[ue_channels['ROAS'].notna()].sort_values('ROAS', ascending=False)
    fig_roas = go.Figure(go.Bar(
        x=roas_ch['ROAS'],
        y=roas_ch['Source'],
        orientation='h',
        marker=dict(
            color=['#2ec4b6' if r >= 1 else '#e63946' for r in roas_ch['ROAS']]
        ),
        text=roas_ch['ROAS'].apply(lambda x: f'{x:.2f}x'),
        textposition='outside',
    ))
    fig_roas.add_vline(x=1, line_dash='dash', line_color='white',
                       annotation_text='безубыточность')
    fig_roas.update_layout(**PLOTLY_TEMPLATE, title='ROAS по каналам')

    # Таблица
    table_cols = ['Source', 'Leads', 'Paid', 'C1 %', 'Total Spend', 'CAC', 'ARPPU', 'Revenue', 'ROAS']
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

    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card('Расходы €',  f'{total_spend:,.0f}', color=COLORS['red']), md=3),
            dbc.Col(kpi_card('Выручка €',  f'{total_revenue:,.0f}', color=COLORS['green']), md=3),
            dbc.Col(kpi_card('CAC €',      f'{cac:,.0f}', color=COLORS['yellow']), md=3),
            dbc.Col(kpi_card('ROAS',       f'{roas:.2f}x', color=COLORS['accent']), md=3),
        ], className='g-3 mb-4'),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=make_fig(fig_cac)), md=6),
            dbc.Col(dcc.Graph(figure=make_fig(fig_roas)), md=6),
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
        x=active.sort_values('Выручка', ascending=False)['Deal Owner Name'],
        y=active.sort_values('Выручка', ascending=False)['Выручка'],
        marker_color=COLORS['accent'],
        text=active.sort_values('Выручка', ascending=False)['Выручка']
            .apply(lambda x: f'{x:,.0f}'),
        textposition='outside',
    ))
    fig_rev.update_layout(**PLOTLY_TEMPLATE, title='Выручка по менеджерам, €')

    # Скаттер: Сделок vs Конверсия
    fig_scatter = px.scatter(
        active,
        x='Сделок', y='Конверсия',
        size='Выручка', color='Выручка',
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
            dbc.Col(kpi_card('Выручка €', f'{active["Выручка"].sum():,.0f}',
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

    for col in ['C1 %', 'Revenue', 'ARPPU', 'Leads', 'Paid']:
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
        x=ue_products.sort_values('ARPPU', ascending=False)['Product'],
        y=ue_products.sort_values('ARPPU', ascending=False)['ARPPU'],
        marker_color=COLORS['yellow'],
        text=ue_products.sort_values('ARPPU', ascending=False)['ARPPU']
            .apply(lambda x: f'{x:,.0f} €'),
        textposition='outside',
    ))
    fig_arppu.update_layout(**PLOTLY_TEMPLATE, title='Медианный чек (ARPPU), €')

    fig_pie = go.Figure(go.Pie(
        labels=ue_products['Product'],
        values=ue_products['Revenue'],
        hole=0.45,
        marker=dict(colors=[COLORS['accent'], COLORS['green'],
                             COLORS['yellow'], COLORS['red'], '#9d4edd']),
        textinfo='label+percent',
    ))
    fig_pie.update_layout(**PLOTLY_TEMPLATE, title='Доля выручки по продуктам',
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
            dbc.Col(kpi_card('Выручка лидера',
                             f'{ue_products["Revenue"].max():,.0f} €',
                             ue_products.nlargest(1, 'Revenue')['Product'].iloc[0],
                             color=COLORS['accent']), md=3),
            dbc.Col(kpi_card('Средний ARPPU',
                             f'{ue_products["ARPPU"].mean():,.0f} €',
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

        # Вкладки
        dbc.Tabs(
            id='tabs',
            active_tab='funnel',
            children=[
                dbc.Tab(label='Воронка и динамика', tab_id='funnel',
                        label_style={'color': COLORS['subtext']},
                        active_label_style={'color': COLORS['accent']}),
                dbc.Tab(label='Маркетинг (CAC / ROAS)', tab_id='marketing',
                        label_style={'color': COLORS['subtext']},
                        active_label_style={'color': COLORS['accent']}),
                dbc.Tab(label='Менеджеры по продажам', tab_id='sales',
                        label_style={'color': COLORS['subtext']},
                        active_label_style={'color': COLORS['accent']}),
                dbc.Tab(label='Продукты и юнит-экономика', tab_id='products',
                        label_style={'color': COLORS['subtext']},
                        active_label_style={'color': COLORS['accent']}),
            ],
            style={'marginBottom': '24px'},
        ),

        # Контент вкладки
        html.Div(id='tab-content'),
    ]
)


@app.callback(Output('tab-content', 'children'), Input('tabs', 'active_tab'))
def render_tab(tab):
    if tab == 'funnel':
        return tab_funnel()
    if tab == 'marketing':
        return tab_marketing()
    if tab == 'sales':
        return tab_sales()
    if tab == 'products':
        return tab_products()
    return html.Div('Выберите вкладку')


if __name__ == '__main__':
    app.run(debug=False, port=8050)
