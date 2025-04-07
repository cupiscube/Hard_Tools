# Run with:
# streamlit run clickhouse_size_estimator.py
import streamlit as st
import sqlparse
import re

# Примерные размеры типов данных в байтах
type_size_map = {
    "UInt8": 1, "Int8": 1,
    "UInt16": 2, "Int16": 2,
    "UInt32": 4, "Int32": 4, "Float32": 4,
    "UInt64": 8, "Int64": 8, "Float64": 8,
    "Date": 2,
    "DateTime": 8,
    "Enum8": 1,
    "Enum16": 2,
    "String": 50,         # средняя длина строки
    "FixedString": 50     # можно уточнять
}

# Перевод в ГБ
def to_gb(bytes_val):
    return round(bytes_val / (1024 ** 3), 2)

# Парсинг CREATE TABLE
def parse_create_table(sql):
    columns = []
    parsed = sqlparse.parse(sql)[0]
    tokens = parsed.tokens

    table_def_start = False
    for token in tokens:
        if isinstance(token, sqlparse.sql.Parenthesis):
            table_def_start = True
            col_defs = token.value.strip('() \n').split(',')
            for col_def in col_defs:
                parts = re.split(r'\s+', col_def.strip(), maxsplit=2)
                if len(parts) >= 2:
                    col_name = parts[0].strip('`"')
                    col_type = parts[1].split('(')[0]  # убрать параметры, как в FixedString(100)
                    columns.append((col_name, col_type))
    return columns

# Интерфейс
st.set_page_config(page_title="ClickHouse Size Estimator", layout="centered")
st.title("📦 Оценка размера таблицы ClickHouse по CREATE TABLE")

create_sql = st.text_area("Вставь команду `CREATE TABLE`:")

row_count = st.number_input("Количество строк", min_value=1000, value=10_000_000, step=1000)

if st.button("🔍 Рассчитать"):
    if not create_sql.lower().startswith("create table"):
        st.warning("Пожалуйста, вставь корректный `CREATE TABLE` SQL.")
    else:
        columns = parse_create_table(create_sql)
        if not columns:
            st.warning("Не удалось распарсить колонки. Проверь синтаксис.")
        else:
            st.subheader("📄 Распознанные колонки:")
            for name, dtype in columns:
                st.write(f"- **{name}**: `{dtype}`")

            total_row_size = 0
            for _, dtype in columns:
                dtype_base = dtype.split('(')[0]
                size = type_size_map.get(dtype_base, 50)  # по умолчанию считаем как String
                total_row_size += size

            raw_size = total_row_size * row_count
            compression_ratio = 4
            compressed_size = raw_size / compression_ratio
            recommended_disk = compressed_size * 2.5

            st.markdown("## 📊 Результаты оценки:")
            st.write(f"**Размер строки:** `{total_row_size}` байт")
            st.write(f"**Сырые данные:** `{to_gb(raw_size)} ГБ`")
            st.write(f"**После сжатия:** `{to_gb(compressed_size)} ГБ`")
            st.write(f"**Рекомендованный минимум на диск:** `{to_gb(recommended_disk)} ГБ`")
