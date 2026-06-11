# План выполнения финального проекта

> Дорожная карта. Задание: [TASK.md](TASK.md). Данные: [DATA_REVIEW.md](DATA_REVIEW.md).
> Инструменты строго в рамках курса. Каждый этап = атомарный коммит (Conventional Commits) + push в `main`.
> Выводы — на русском, в markdown-ячейках, формат «вопрос → код → график → вывод».

## Стек по этапам («не только кодеры»)

| # | Этап | Инструмент | Артефакт |
|---|---|---|---|
| 0 | Загрузка данных | Python (pandas): Excel → DataFrame; исходники в `data/` не трогаем | `notebooks/01_cleaning.ipynb` (первая секция) |
| 1 | Очистка | Jupyter + pandas → сохранение в `data_clean/*.csv` | очищенный датасет |
| 2 | Описательная статистика | Jupyter (pandas + matplotlib/seaborn) | `02_descriptive.ipynb` |
| 3 | Анализ данных | Jupyter (pandas + seaborn/plotly) | `03_analysis.ipynb` |
| 4 | Юнит-экономика, дерево метрик, гипотезы | Jupyter (расчёты) + **Google Sheets** (итоговая таблица юнит-экономики, дерево метрик) | `04_unit_economics.ipynb` + ссылка на Sheets |
| 5 | Дашборд основной | **Power BI** поверх `data_clean/` (или MySQL, см. этап 7) | `dashboard/*.pbix` |
| 5b | Мини-даш | **Python (plotly)** — 2–3 интерактивных графика | в ноутбуках / `dashboard/` |
| 6 | Презентация | **Google Presentation** | ссылка + PDF-экспорт в `presentation/` |
| 7 | ✱ Бонус: SQL-слой | Python (PyMySQL) грузит raw и clean в **MySQL**; Power BI подключается к БД | `scripts/load_to_mysql.py` |

> Примечание: в ТЗ нет требований к слою загрузки. Ядро проекта работает локально (Excel → pandas → CSV) и не зависит от БД; MySQL — дополнительная функция (по критериям оценки бонусы могут компенсировать недочёты). Ключи БД — только в `.env`, в репозиторий не попадают.

## Структура проекта (целевая)

```
final_project_Honcahrov_120925/
├── data/                      # исходные данные (read-only, как выданы)
├── data_clean/                # очищенные датасеты (CSV)
├── notebooks/
│   ├── 01_cleaning.ipynb
│   ├── 02_descriptive.ipynb
│   ├── 03_analysis.ipynb
│   └── 04_unit_economics.ipynb
├── dashboard/                 # .pbix (+ plotly мини-даш)
├── presentation/              # PDF презентации + ссылки
├── scripts/                   # ✱ load_to_mysql.py (бонус)
├── TASK.md, DATA_REVIEW.md, PROJECT_PLAN.md, README.md
└── .gitignore                 # .env, STUDENT_PROFILE.md и пр.
```

## Этап 0–1. Загрузка и очистка — `01_cleaning.ipynb`

**Загрузка:**
- [ ] `pd.read_excel` всех 4 файлов, `dtype=str` для всех Id (Deals.Id, Contact Name, Calls.Id, CONTACTID, Contacts.Id).
- [ ] Контроль после загрузки: размеры, типы, head — сверка с DATA_REVIEW.md.
- [ ] Исходники в `data/` не изменяются; вся очистка — на копии в памяти, результат — в `data_clean/`.

**Очистка:**
- [ ] Deals: удалить 2 битые строки, 3 полных дубликата.
- [ ] Spend: разобрать 917 полных дубликатов → удалить с обоснованием.
- [ ] Calls: удалить пустые колонки `Dialled Number`, `Tag`.
- [ ] Даты: Created/Modified/Closing/Call Start Time (`dd.mm.yyyy HH:MM`), SLA → timedelta.
- [ ] Числовые: Initial Amount Paid (16 нечисловых → NaN/число), Offer Total Amount, Course duration, Months of study.
- [ ] Аномалии (по FAQ): Closing < Created (44) — исправить и обосновать; IAP > OTA (55) — исправить и обосновать; демо-значения 0/1/9 — пометить флагом.
- [ ] Нормализация: Level of Deutsch (б1→B1, единая шкала), City («-»→NaN, унификация), Education Type (`#REF!`→NaN), Quality («F»).
- [ ] Стратегия пропусков по колонкам (структурные пропуски воронки не удалять!).
- [ ] Сохранить в `data_clean/` + таблица «было/стало».
- Коммит: `feat: data loading and cleaning (01_cleaning)` → push main

## Этап 2. Описательная статистика — `02_descriptive.ipynb`

- [ ] Числовые поля: mean, median, mode, range (+std, квартили) — IAP, OTA, Call Duration, SLA, Course duration, Months of study, Spend/Clicks/Impressions.
- [ ] Категориальные: Quality, Stage, Source, Product, Education Type, Payment Type, Call Type — value_counts + барчарты.
- [ ] Гистограммы/боксплоты, интерпретация каждого графика.
- Коммит: `feat: descriptive statistics (02_descriptive)` → push main

## Этап 3. Анализ данных — `03_analysis.ipynb`

- [ ] **Временные ряды:** динамика создания сделок (день/неделя/месяц), наложение на динамику звонков; распределение времени от создания до закрытия (Payment Done и Lost отдельно).
- [ ] **Кампании:** лиды и конверсия в Payment Done по Campaign; источники (Source) по качеству лидов (Quality A/B vs D/E).
- [ ] **Отдел продаж:** по Deal Owner Name — число сделок, конверсия, сумма продаж; топ/антитоп.
- [ ] **Платежи и продукты:** Payment Type vs успешность; популярность и выручка по Product и Education Type.
- [ ] **География (✱):** сделки по City; влияние Level of Deutsch на успешность по городам.
- [ ] Сквозные выводы и рекомендации для бизнеса (списком).
- Коммит: `feat: time series, campaigns, sales, products, geo analysis (03_analysis)` → push main

## Этап 4. Юнит-экономика и гипотезы — `04_unit_economics.ipynb` + Google Sheets

- [ ] Связка Spend ↔ Deals по Source/Campaign: расходы, лиды, оплаты по продуктам.
- [ ] Юнит-экономика по продуктам: CAC, конверсия C1, средний чек / ARPPU, выручка (LTV по Months of study — насколько позволяют данные).
- [ ] Экспорт итоговой таблицы юнит-экономики в **Google Sheets** (оформление как в Product Analytics).
- [ ] Дерево метрик бизнеса (схема: выручка → лиды × конверсия × чек → драйверы) — в Sheets/презентации.
- [ ] Точки роста из юнит-экономики (2–3 кандидата с цифрами).
- [ ] 1–2 гипотезы: формулировка (если X, то метрика Y вырастет на Z), целевая метрика, дизайн теста ≤ 2 недель (группы, длительность, критерий успеха, риски).
- Коммит: `feat: unit economics, metrics tree, growth hypotheses (04_unit_economics)` → push main

## Этап 5. Дашборды — `dashboard/`

**Power BI (основной):**
- [ ] Источник: `data_clean/` (или MySQL после этапа 7).
- [ ] Модель данных: Deals ↔ Contacts ↔ Calls, Spend по Source/Campaign; календарь.
- [ ] Страницы: 1) воронка и динамика, 2) маркетинг (источники/кампании/CAC), 3) продажи (менеджеры), 4) продукты/платежи.
- [ ] DAX-меры: конверсия, выручка, CAC, средний чек.

**Python мини-даш:**
- [ ] 2–3 интерактивных plotly-графика (динамика сделок, воронка, источники) — в ноутбуке или простое Dash-приложение.
- Коммит: `feat: Power BI dashboard and plotly mini-dash` → push main

## Этап 6. Презентация и подготовка к защите — `presentation/`

- [ ] **Google Presentation** 5–10 мин по структуре из TASK.md: приветствие → проект/задание → результат → сложности/открытия.
- [ ] Слайды: данные и очистка (коротко) → 3–4 ключевых инсайта с графиками → юнит-экономика → гипотеза и план теста → рекомендации.
- [ ] PDF-экспорт в `presentation/`, README.md проекта (описание, структура, как запустить).
- [ ] Шпаргалка ответов «почему так» по каждому решению (вопросы преподавателя ×3!).
- [ ] Загрузить ссылку в LMS (модуль Project) **за 1 день до защиты**. Проверить отсутствие ключей!
- Коммит: `docs: presentation and README` → push main

## Этап 7. ✱ Бонус: SQL-слой (если останется время)

- [ ] `scripts/load_to_mysql.py`: создание схем `raw`/`clean`, загрузка через PyMySQL, ключи в `.env`.
- [ ] 3–5 показательных SQL-запросов (агрегации) в ноутбуке/скрипте.
- [ ] Переключить Power BI на MySQL-источник.
- Коммит: `feat: MySQL raw/clean layer (bonus)` → push main

## Соответствие критериям оценки

| Критерий | Закрывается этапом |
|---|---|
| Очистка и подготовка | 0–1 |
| Описательная статистика | 2 |
| Анализ данных | 3 |
| Юнит-экономика и дерево метрик | 4 |
| Гипотезы и проверка | 4 |
| Представление результатов | 5, 6 |
| Вопросы преподавателя | шпаргалка обоснований во всех ноутбуках |
| Доп. функции (бонус к оценке) | 5b, 7 |
