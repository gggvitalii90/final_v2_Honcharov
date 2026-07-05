# Project Navigation

Карта проекта: где искать каждый блок задания и какие файлы открывать в первую очередь.

## Быстрый маршрут проверки

| # | Что проверить | Где находится | Комментарий |
|---|---|---|---|
| 1 | Задание и критерии | `TASK.md` | Исходные требования проекта и FAQ по данным. |
| 2 | Ревью данных | `DATA_REVIEW.md` | Профилирование raw-файлов, проблемы качества, связи таблиц. |
| 3 | Решения по спорным вопросам | `PROJECT_DECISIONS.md` | Короткая фиксация решений по Google Sheets, Power BI, revenue, менеджерам и навигации. |
| 4 | Общий план проекта | `PROJECT_PLAN.md` | Дорожная карта этапов и артефактов. |
| 5 | Очистка данных | `notebooks/01_cleaning.ipynb` | Загрузка Excel, чистка, флаги ошибок, сохранение `data_clean/*.csv`. |
| 6 | Описательная статистика | `notebooks/02_descriptive.ipynb` | Распределения, категории, первые выводы по таблицам. |
| 7 | Основной анализ | `notebooks/03_analysis.ipynb` | Временные ряды, кампании, менеджеры, продукты, география, звонки. |
| 8 | Подготовка unit economics | `notebooks/04_unit_economics.ipynb` | Подготовка clean-данных для Google Sheets и контроль метрик. |
| 9 | Unit economics | Google Sheets | Source of truth для unit economics, дерева метрик, точек роста и гипотез. |
| 10 | Дашборд | `final_dashboard_Honcharov_V_120925.pbix`, `dashboard/app.py` | Power BI как основной дашборд, Dash как дополнительная демонстрация. |
| 11 | Подготовка к защите | `ОТВЕТЫ_НА_ВОПРОСЫ.md`, `PRESENTATION_NOTES.md` | Ответы преподавателю, формулировки ограничений и выводов. |

## Навигация внутри ноутбуков

Надёжная навигация должна быть внутри каждого `.ipynb`, потому что внешние ссылки из `.md` в конкретный якорь ноутбука могут по-разному работать в VS Code, классическом Jupyter и GitHub.

Рекомендуемый шаблон в начале ноутбука:

```markdown
<a id="plan"></a>

## План

- [1. Загрузка данных](#load-data)
- [2. Очистка](#cleaning)
- [3. Итоги](#summary)
```

Перед разделом:

```markdown
<a id="load-data"></a>

## 1. Загрузка данных

[Вернуться к плану](#plan)
```

## Правила якорей

- Использовать стабильные английские id: `load-data`, `manager-roles`, `unit-by-source`.
- Не полагаться на автоматические якоря по русским заголовкам.
- Не ставить пустой якорь далеко от заголовка, если VS Code/Jupyter промахивается при прокрутке.
- Для проблемных мест лучше ставить `id` на видимый HTML-заголовок, например `<h3 id="manager-roles">7.4 Роли менеджеров</h3>`.

## Карта будущих доработок

| Блок | Куда добавить | Что сделать |
|---|---|---|
| Google Sheets workflow | `PROJECT_PLAN.md`, `04_unit_economics.ipynb` | Зафиксировать, что Sheets является source of truth для unit economics. |
| First Payment terminology | `04_unit_economics.ipynb`, `dashboard/app.py`, Sheets | Переименовать "Revenue" по первому платежу в `First Payment Amount`. |
| Revenue recognition | `04_unit_economics.ipynb` или отдельный сценарный блок | Посчитать projected/recognized revenue и refund risk отдельно от базовой unit economics. |
| Manager roles | `03_analysis.ipynb` | Добавить first-touch vs closer перед финальным рейтингом менеджеров. |
| Calls before payment | `03_analysis.ipynb` | Посчитать количество звонков до оплаты по `CONTACTID` и `Closing Date`. |
| Parquet export | scripts/export_clean_parquet.py | Сохранять clean-данные в CSV и Parquet. |
| Google Sheets exports | scripts/export_google_sheets_inputs.py, exports/google_sheets/ | Копировать полные clean CSV для Deals + Spend в папку загрузки Google Sheets. |
