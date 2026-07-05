# План выполнения финального проекта

> Дорожная карта. Задание: [TASK.md](TASK.md). Данные: [DATA_REVIEW.md](DATA_REVIEW.md).
> Ключевые решения: [PROJECT_DECISIONS.md](PROJECT_DECISIONS.md). Навигация: [PROJECT_NAVIGATION.md](PROJECT_NAVIGATION.md).
> Инструменты строго в рамках курса. Каждый этап = атомарный коммит (Conventional Commits) + push в `main`.
> Выводы — на русском, в markdown-ячейках, формат «вопрос → код → график → вывод».

## Стек по этапам («не только кодеры»)

| # | Этап | Инструмент | Артефакт |
|---|---|---|---|
| 0 | Загрузка данных | Python (pandas): Excel → DataFrame; исходники в `data/` не трогаем | `notebooks/01_cleaning.ipynb` |
| 1 | Очистка | Jupyter + pandas → сохранение в `data_clean/*.csv` и `*.parquet` | очищенные датасеты |
| 2 | Описательная статистика | Jupyter (pandas + matplotlib/seaborn) | `notebooks/02_descriptive.ipynb` |
| 3 | Анализ данных | Jupyter (pandas + seaborn/plotly) | `notebooks/03_analysis.ipynb` |
| 4 | Юнит-экономика, дерево метрик, гипотезы | Google Sheets как source of truth; Jupyter готовит/валидирует clean-данные | `notebooks/04_unit_economics.ipynb` + ссылка на Sheets |
| 5 | Дашборд основной | Power BI поверх `10_dashboard_export` из Google Sheets или clean Parquet/CSV | `final_dashboard_Honcharov_V_120925.pbix` |
| 5b | Мини-даш | Python Dash / Plotly | `dashboard/app.py` |
| 6 | Презентация | Google Presentation / PDF | ссылка + PDF-экспорт |
| 7 | Бонус | Docker/Python pipeline или SQL-слой, если останется время | scripts / docs |

## Структура проекта

```
final_v2_Honcharov/
├── data/                         # исходные данные (read-only, как выданы)
├── data_clean/                   # очищенные датасеты CSV + Parquet
├── notebooks/
│   ├── 01_cleaning.ipynb
│   ├── 02_descriptive.ipynb
│   ├── 03_analysis.ipynb
│   └── 04_unit_economics.ipynb
├── dashboard/                    # Python Dash
├── final_dashboard_*.pbix         # Power BI dashboard
├── TASK.md
├── DATA_REVIEW.md
├── PROJECT_PLAN.md
├── PROJECT_DECISIONS.md
├── PROJECT_NAVIGATION.md
├── ОТВЕТЫ_НА_ВОПРОСЫ.md
└── PRESENTATION_NOTES.md
```

## Этап 0–1. Загрузка и очистка — `01_cleaning.ipynb`

**Загрузка:**
- [ ] `pd.read_excel` всех 4 файлов, `dtype=str` для всех Id (`Deals.Id`, `Contact Name`, `Calls.Id`, `CONTACTID`, `Contacts.Id`).
- [ ] Контроль после загрузки: размеры, типы, head — сверка с `DATA_REVIEW.md`.
- [ ] Исходники в `data/` не изменяются; вся очистка — на копии в памяти.

**Очистка:**
- [ ] Deals: удалить 2 битые строки без Id; не считать float-коллизии реальными дублями.
- [ ] Spend: разобрать 917 полных дубликатов → удалить с обоснованием, чтобы не задвоить расходы.
- [ ] Calls: удалить пустые колонки `Dialled Number`, `Tag`.
- [ ] Даты: Created/Modified/Closing/Call Start Time (`dd.mm.yyyy HH:MM`), SLA → секунды/timedelta.
- [ ] Числовые: Initial Amount Paid, Offer Total Amount, Course duration, Months of study.
- [ ] Аномалии: Closing < Created — флаг/исключение из анализа времени; IAP > OTA — флаг; демо 0/1/9 — флаг.
- [ ] Payment Type: если `Payment Type` пустой и `Initial Amount Paid == Offer Total Amount`, заполнить `One Payment` в пункте 4.7 до итогов очистки.
- [ ] Нормализация: Level of Deutsch, City, Education Type `#REF!`, Quality `F`.
- [ ] Сохранить `data_clean/*.csv` и дополнительно `data_clean/*.parquet` для Power BI.

## Этап 2. Описательная статистика — `02_descriptive.ipynb`

- [ ] Числовые поля: mean, median, mode, range, std, квартили.
- [ ] Категориальные поля: Quality, Stage, Source, Product, Education Type, Payment Type, Call Type.
- [ ] Гистограммы/боксплоты и интерпретация каждого графика.
- [ ] Не смешивать описательную статистику звонков с анализом результата сделки: вопрос «сколько звонков до оплаты» идёт в этап 3.

## Этап 3. Анализ данных — `03_analysis.ipynb`

- [ ] Временные ряды: динамика создания сделок, звонков, оплат; учесть незрелость последних когорт.
- [ ] Кампании: лиды, конверсия в оплату, качество лидов, пороги по размеру выборки.
- [ ] Отдел продаж: Deal Owner Name — число сделок, конверсия, сумма первого платежа, топ/антитоп.
- [ ] Роли менеджеров: first-touch manager, участник коммуникации, deal owner / closer, payment closer.
- [ ] Проверить, сколько клиентов обрабатывали 2+ менеджера, и не строить несправедливый единый рейтинг без учёта ролей.
- [ ] Звонки до оплаты: для `Payment Done` + непустой `Initial Amount Paid` посчитать число звонков по `CONTACTID` до `Closing Date`.
- [ ] Revenue recognition: отдельный сценарный блок projected revenue / recognized revenue / refund risk; не смешивать с базовой unit economics.
- [ ] Платежи и продукты: Payment Type, Product, Education Type, сумма первого платежа, конверсия.
- [ ] География и Level of Deutsch: использовать с оговорками из-за пропусков и нестандартизированного ввода.
- [ ] Сквозные выводы и рекомендации для бизнеса.

## Этап 4. Юнит-экономика и гипотезы — `04_unit_economics.ipynb` + Google Sheets

**Роль Python:**
- [ ] Подготовить clean-выгрузки для новой Google Таблицы `1ybv6r_ZyLiyFJv0SggjvJQaiYa568UYCv9r6ml6uIsg`: Deals + Spend, без raw Excel.
- [ ] Проверить объём, типы, обязательные колонки и базовые контрольные суммы.
- [ ] Для Google Sheets использовать полноценные очищенные `deals_clean.csv` и `spend_clean.csv`; не создавать отдельную урезанную схему.

**Роль Google Sheets:**
- [ ] Загрузить `deals_clean` и `spend_clean`; Contacts/Calls не нужны для базовой unit economics.
- [ ] Сделать raw-листы неизменяемыми: `01_deals_clean_raw`, `02_spend_clean_raw`.
- [ ] Завести `03_methodology` с правилами метрик и фильтрами.
- [ ] Посчитать unit economics по Source/Campaign/Product: Leads, Paid Deals, First Payment Amount, Spend, C1, CAC, CPL, Avg First Payment, First Payment Return / Spend.
- [ ] Не называть `Initial Amount Paid` полной выручкой; базовая финансовая метрика — First Payment Amount / сумма первого платежа.
- [ ] Сделать дерево метрик, точки роста и 1–2 глубокие гипотезы с тестом до 2 недель.
- [ ] Подготовить `10_dashboard_export` для Power BI и презентации.

## Этап 5. Дашборды

**Power BI:**
- [ ] Источник: Google Sheets `10_dashboard_export` или clean Parquet/CSV из `data_clean/`.
- [ ] Модель данных: Deals ↔ Contacts ↔ Calls, Spend по Source/Campaign; отдельная Calendar table.
- [ ] Проверить проблему дат в Power BI: даты должны быть настоящими date/datetime, а не текстом.
- [ ] Страницы: воронка и динамика, маркетинг/CAC, продажи/менеджеры, продукты/платежи.
- [ ] DAX-меры: конверсия, First Payment Amount, CAC, средний первый платёж; полную revenue-модель не смешивать с базовой unit economics.

**Python Dash:**
- [ ] Оставить как дополнительную демонстрацию, не как source of truth для unit economics.
- [ ] Если в Dash есть `Revenue` по `Initial Amount Paid`, привести терминологию к First Payment Amount или явно подписать как первый платёж.

## Этап 6. Презентация и защита

- [ ] Слайды: данные и очистка → ключевые инсайты → Google Sheets unit economics → гипотезы → рекомендации.
- [ ] Отдельно объяснить, почему Python = очистка, Google Sheets = продуктовая аналитика, Power BI = визуализация.
- [ ] Использовать `ОТВЕТЫ_НА_ВОПРОСЫ.md` и `PROJECT_DECISIONS.md` как шпаргалку.
- [ ] Честно назвать ограничения: один год данных, пропуски City, Level of Deutsch, субъективность Quality, незрелые когорты, First Payment ≠ полная revenue.

## Этап 7. Бонус: автоматизация / SQL-слой

- [ ] Docker рассматривать только для автоматизации data pipeline: очистка, экспорт CSV/Parquet, обновление данных.
- [ ] Не делать ставку на «Docker одной кнопкой создаёт красивый Power BI отчёт с нуля» — это избыточно и рискованно.
- [ ] SQL/MySQL слой делать только если останется время и он не мешает основной защите.

## Соответствие критериям оценки

| Критерий | Закрывается этапом |
|---|---|
| Очистка и подготовка | 0–1 |
| Описательная статистика | 2 |
| Анализ данных | 3 |
| Юнит-экономика и дерево метрик | 4 |
| Гипотезы и проверка | 4 |
| Представление результатов | 5, 6 |
| Вопросы преподавателя | `ОТВЕТЫ_НА_ВОПРОСЫ.md`, `PROJECT_DECISIONS.md` |
| Доп. функции | 5b, 7 |
